import pool from '../config/db.js';
import { getActiveUploadId } from './dashboardController.js';

export const getBranchAnalysis = async (req, res) => {
  try {
    const uploadId = await getActiveUploadId(req.user.id, req.query.upload_id);
    if (!uploadId) return res.json([]);

    const [branchStats] = await pool.query(
      `SELECT 
        b.name, 
        COUNT(s.id) as total_students,
        SUM(CASE WHEN s.status = 'Pass' THEN 1 ELSE 0 END) as passed_students,
        AVG(s.sgpa) as avg_sgpa
       FROM students s
       JOIN branches b ON s.branch_id = b.id
       WHERE s.upload_id = ?
       GROUP BY b.id`,
      [uploadId]
    );

    const results = [];
    for (const b of branchStats) {
      const [topperRows] = await pool.query(
        `SELECT name FROM students 
         WHERE upload_id = ? AND branch_id = (SELECT id FROM branches WHERE name = ?) AND sgpa IS NOT NULL 
         ORDER BY sgpa DESC LIMIT 1`,
        [uploadId, b.name]
      );
      
      const topperName = topperRows.length > 0 ? topperRows[0].name : 'N/A';
      const passed = Number(b.passed_students);
      const total = Number(b.total_students);
      const passPerc = total > 0 ? parseFloat(((passed / total) * 100).toFixed(1)) : 0;
      
      results.push({
        name: b.name,
        passPercentage: passPerc,
        avgMarks: parseFloat(((b.avg_sgpa || 0) * 10).toFixed(1)), 
        topper: topperName
      });
    }

    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getFailedAnalysis = async (req, res) => {
  try {
    const uploadId = await getActiveUploadId(req.user.id, req.query.upload_id);
    if (!uploadId) return res.json([]);

    const [rows] = await pool.query(
      `SELECT s.seat_no, s.name, b.name as branch, s.sgpa, s.status 
       FROM students s
       LEFT JOIN branches b ON s.branch_id = b.id
       WHERE s.upload_id = ? AND s.status = 'Fail'`,
      [uploadId]
    );

    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getMeritAnalysis = async (req, res) => {
  const uploadId = await getActiveUploadId(req.user.id, req.query.upload_id);
  if (!uploadId) return res.json([]);

  try {
    const [rows] = await pool.query(
      `SELECT s.name, s.sgpa, s.seat_no, b.name as branch 
       FROM students s 
       LEFT JOIN branches b ON s.branch_id = b.id 
       WHERE s.upload_id = ? AND s.sgpa IS NOT NULL 
       ORDER BY s.sgpa DESC LIMIT 10`,
      [uploadId]
    );

    res.json(rows.map(r => ({
      name: r.name,
      percentage: r.sgpa,
      branch: r.branch || 'Unknown',
      seat_no: r.seat_no
    })));
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getSubjectAnalysis = async (req, res) => {
  const uploadId = await getActiveUploadId(req.user.id, req.query.upload_id);
  if (!uploadId) return res.json([]);

  try {
    const [rows] = await pool.query(
      `SELECT 
         su.name,
         su.id as subject_id,
         COUNT(m.id) as total_students,
         SUM(CASE WHEN m.grade NOT IN ('F', 'AB', 'ABSENT', 'XX', 'NP', 'AC') AND m.marks_obtained > 0 THEN 1 ELSE 0 END) as passed_students,
         MAX(m.marks_obtained) as highest_marks,
         MIN(m.marks_obtained) as lowest_marks,
         AVG(m.marks_obtained) as avg_marks,
         MAX(m.max_marks) as max_marks_val
       FROM marks m
       JOIN subjects su ON m.subject_id = su.id
       JOIN students s ON m.student_id = s.id
       WHERE s.upload_id = ?
       GROUP BY su.id, su.name`,
      [uploadId]
    );

    res.json(rows.map(r => {
      const passed = Number(r.passed_students) || 0;
      const total = Number(r.total_students) || 0;
      const passPerc = total > 0 ? parseFloat(((passed / total) * 100).toFixed(1)) : 0;
      const maxMarksVal = Number(r.max_marks_val) || 100;
      return {
        name: r.name,
        passPercentage: passPerc,
        highestMarks: r.highest_marks,
        lowestMarks: r.lowest_marks,
        avgMarks: parseFloat(Number(r.avg_marks).toFixed(2)),
        failCount: total - passed,
        subjectType: maxMarksVal === 100 ? 'Theory' : 'Practical'
      };
    }));
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getStudentMarks = async (req, res) => {
  const uploadId = await getActiveUploadId(req.user.id, req.query.upload_id);
  if (!uploadId) return res.json([]);

  try {
    const [rows] = await pool.query(
      `SELECT su.name as subject_name, m.marks_obtained, m.max_marks, m.grade
       FROM marks m
       JOIN subjects su ON m.subject_id = su.id
       JOIN students s ON m.student_id = s.id
       WHERE s.seat_no = ? AND s.upload_id = ?
       ORDER BY su.name`,
      [req.params.seat_no, uploadId]
    );
    res.json(rows);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getSubjectToppers = async (req, res) => {
  const uploadId = await getActiveUploadId(req.user.id, req.query.upload_id);
  const category = req.query.category || 'Theory';
  if (!uploadId) return res.json([]);

  try {
    const [subjects] = await pool.query(
      `SELECT su.id as subject_id, su.name as subject_name, MAX(m.max_marks) as max_marks_val
       FROM marks m
       JOIN subjects su ON m.subject_id = su.id
       JOIN students s ON m.student_id = s.id
       WHERE s.upload_id = ?
       GROUP BY su.id, su.name`,
      [uploadId]
    );

    const results = [];
    for (const su of subjects) {
      const maxMarksVal = Number(su.max_marks_val) || 100;
      const subjectType = maxMarksVal === 100 ? 'Theory' : 'Practical';
      const catLower = category.toLowerCase();
      
      if (catLower.includes('practical') && !subjectType.toLowerCase().includes('practical')) continue;
      if (catLower === 'theory' && subjectType !== 'Theory') continue;

      const [topper] = await pool.query(
        `SELECT s.name as student_name, s.seat_no, m.marks_obtained, m.max_marks, m.grade
         FROM marks m
         JOIN students s ON m.student_id = s.id
         WHERE m.subject_id = ? AND s.upload_id = ?
         AND m.grade NOT IN ('F', 'AB', 'ABSENT', 'XX')
         ORDER BY m.marks_obtained DESC
         LIMIT 1`,
        [su.subject_id, uploadId]
      );

      if (topper.length > 0) {
        results.push({
          subject_name: su.subject_name,
          student_name: topper[0].student_name,
          seat_no: topper[0].seat_no,
          marks_obtained: topper[0].marks_obtained,
          max_marks: topper[0].max_marks,
          grade: topper[0].grade
        });
      }
    }
    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
