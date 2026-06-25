import fs from 'fs';
import pool from '../config/db.js';

export const uploadLedger = async (req, res) => {
  if (!req.file) return res.status(400).json({ error: 'No file uploaded' });

  const connection = await pool.getConnection();
  try {
    await connection.beginTransaction();

    const [uploadInsert] = await connection.query(
      'INSERT INTO ledger_uploads (filename, uploaded_by, academic_year, semester) VALUES (?, ?, ?, ?) RETURNING id',
      [req.file.originalname, req.user.id, '2023-2024', '2']
    );
    const uploadId = uploadInsert[0].id;

    const pythonUrl = process.env.PYTHON_SERVICE_URL || 'http://localhost:5002';
    const formData = new FormData();
    const blob = new Blob([fs.readFileSync(req.file.path)], { type: req.file.mimetype });
    formData.append('ledger', blob, req.file.originalname);
    formData.append('upload_id', uploadId.toString());

    const pyResponse = await fetch(`${pythonUrl}/parse`, {
      method: 'POST',
      body: formData
    });

    if (!pyResponse.ok) {
      const errorText = await pyResponse.text();
      throw new Error(`Python parser failed: ${errorText}`);
    }

    const pyData = await pyResponse.json();
    const studentsList = pyData.students || [];

    // 1. Collect all unique branches
    const uniqueBranches = [...new Set(studentsList.map(s => s.branch || 'Unknown'))];
    const branchCache = {};
    if (uniqueBranches.length > 0) {
      // Bulk upsert branches
      let branchQuery = 'INSERT INTO branches (name) VALUES ';
      const branchParams = [];
      uniqueBranches.forEach((b, i) => {
        branchQuery += `($${i + 1})` + (i < uniqueBranches.length - 1 ? ', ' : '');
        branchParams.push(b);
      });
      branchQuery += ' ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id, name';
      
      const [branchRows] = await connection.query(branchQuery, branchParams);
      branchRows.forEach(row => branchCache[row.name] = row.id);
    }

    // 2. Prepare all students for bulk upsert
    let passCount = 0;
    let failCount = 0;
    const uniqueStudentsMap = new Map();
    
    studentsList.forEach(s => {
      if (!uniqueStudentsMap.has(s.seat_no)) {
        const bId = branchCache[s.branch || 'Unknown'];
        const st = s.status || 'Fail';
        if (st === 'Pass') passCount++;
        else failCount++;
        uniqueStudentsMap.set(s.seat_no, [s.seat_no, s.name || '', bId, '2023-2024', uploadId, s.sgpa || 0.0, st]);
      }
    });
    
    const studentRecords = Array.from(uniqueStudentsMap.values());
    const studentCache = {}; // seat_no -> student.id
    if (studentRecords.length > 0) {
      // Chunk students to avoid param limits (pg has 65535 param limit)
      const chunkSize = 1000;
      for (let i = 0; i < studentRecords.length; i += chunkSize) {
        const chunk = studentRecords.slice(i, i + chunkSize);
        let stuQuery = 'INSERT INTO students (seat_no, name, branch_id, academic_year, upload_id, sgpa, status) VALUES ';
        const stuParams = [];
        chunk.forEach((rec, idx) => {
          const offset = idx * 7;
          stuQuery += `($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5}, $${offset + 6}, $${offset + 7})` + (idx < chunk.length - 1 ? ', ' : '');
          stuParams.push(...rec);
        });
        stuQuery += ` ON CONFLICT (seat_no) DO UPDATE SET 
          name = EXCLUDED.name, branch_id = EXCLUDED.branch_id, 
          academic_year = EXCLUDED.academic_year, upload_id = EXCLUDED.upload_id, 
          sgpa = EXCLUDED.sgpa, status = EXCLUDED.status RETURNING id, seat_no`;

        const [stuRows] = await connection.query(stuQuery, stuParams);
        stuRows.forEach(row => studentCache[row.seat_no] = row.id);
      }
    }

    // 3. Collect all unique subjects
    const uniqueSubjectsMap = new Map(); // key -> [name, branchId, semester]
    studentsList.forEach(s => {
      const bId = branchCache[s.branch || 'Unknown'];
      const subs = s.subjects_list || [];
      subs.forEach(sub => {
        const key = `${sub.subject_name}_${bId}_2`;
        if (!uniqueSubjectsMap.has(key)) {
          uniqueSubjectsMap.set(key, [sub.subject_name, bId, 2]);
        }
      });
    });

    const subjectCache = {}; // key -> subject.id
    const uniqueSubjectsArray = Array.from(uniqueSubjectsMap.entries());
    if (uniqueSubjectsArray.length > 0) {
      const chunkSize = 1000;
      for (let i = 0; i < uniqueSubjectsArray.length; i += chunkSize) {
        const chunk = uniqueSubjectsArray.slice(i, i + chunkSize);
        let subQuery = 'INSERT INTO subjects (name, branch_id, semester) VALUES ';
        const subParams = [];
        chunk.forEach((entry, idx) => {
          const offset = idx * 3;
          subQuery += `($${offset + 1}, $${offset + 2}, $${offset + 3})` + (idx < chunk.length - 1 ? ', ' : '');
          subParams.push(...entry[1]);
        });
        subQuery += ' ON CONFLICT (name, branch_id, semester) DO UPDATE SET name = EXCLUDED.name RETURNING id, name, branch_id';
        
        const [subRows] = await connection.query(subQuery, subParams);
        subRows.forEach(row => subjectCache[`${row.name}_${row.branch_id}_2`] = row.id);
      }
    }

    // 4. Bulk insert marks
    const uniqueMarksMap = new Map();
    studentsList.forEach(s => {
      const stId = studentCache[s.seat_no];
      const bId = branchCache[s.branch || 'Unknown'];
      const subs = s.subjects_list || [];
      
      subs.forEach(sub => {
        const subKey = `${sub.subject_name}_${bId}_2`;
        const subId = subjectCache[subKey];
        
        let marksObtained = 0.0;
        let maxMarks = 100.0;
        let finalGrade = sub.grade || '';
        const marksStr = sub.marks ? sub.marks.toString() : '';

        if (marksStr) {
          const match = marksStr.match(/(\d+)\s*\/\s*(\d+)/);
          if (match) {
            marksObtained = parseFloat(match[1]);
            maxMarks = parseFloat(match[2]);
          } else if (/^\d+$/.test(marksStr)) {
            marksObtained = parseFloat(marksStr);
          } else {
            finalGrade = 'F';
          }
        }
        if (!finalGrade || ['AB', 'ABSENT', 'FF', 'F'].includes(finalGrade.toUpperCase())) {
          finalGrade = 'F';
        }

        if (stId && subId) {
          const markKey = `${stId}_${subId}`;
          if (!uniqueMarksMap.has(markKey)) {
            uniqueMarksMap.set(markKey, [stId, subId, marksObtained, maxMarks, finalGrade]);
          }
        }
      });
    });

    const marksRecords = Array.from(uniqueMarksMap.values());
    if (marksRecords.length > 0) {
      const chunkSize = 1000; // 5 params * 1000 = 5000 parameters per query
      for (let i = 0; i < marksRecords.length; i += chunkSize) {
        const chunk = marksRecords.slice(i, i + chunkSize);
        let marksQuery = 'INSERT INTO marks (student_id, subject_id, marks_obtained, max_marks, grade) VALUES ';
        const marksParams = [];
        chunk.forEach((rec, idx) => {
          const offset = idx * 5;
          marksQuery += `($${offset + 1}, $${offset + 2}, $${offset + 3}, $${offset + 4}, $${offset + 5})` + (idx < chunk.length - 1 ? ', ' : '');
          marksParams.push(...rec);
        });
        marksQuery += ` ON CONFLICT (student_id, subject_id) DO UPDATE SET 
          marks_obtained = EXCLUDED.marks_obtained, 
          max_marks = EXCLUDED.max_marks, 
          grade = EXCLUDED.grade`;
        
        await connection.query(marksQuery, marksParams);
      }
    }

    await connection.query(
      'UPDATE ledger_uploads SET total_students = ?, pass_count = ?, fail_count = ? WHERE id = ?',
      [studentsList.length, passCount, failCount, uploadId]
    );

    await connection.commit();

    if (fs.existsSync(req.file.path)) fs.unlinkSync(req.file.path);

    res.json({
      message: 'File processing completed successfully!',
      upload_id: uploadId,
      students_processed: studentsList.length
    });

  } catch (error) {
    await connection.rollback();
    if (fs.existsSync(req.file.path)) fs.unlinkSync(req.file.path);
    console.error('Upload processing error:', error);
    res.status(500).json({ error: error.message });
  } finally {
    connection.release();
  }
};
