import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import pool from '../config/db.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const generatedDir = path.join(__dirname, '..', '..', '..', 'generated');

export const getHistory = async (req, res) => {
  try {
    let query = 'SELECT * FROM ledger_uploads ORDER BY upload_date DESC';
    let params = [];

    if (req.user.role !== 'admin') {
      query = 'SELECT * FROM ledger_uploads WHERE uploaded_by = ? ORDER BY upload_date DESC';
      params = [req.user.id];
    }

    const [uploads] = await pool.query(query, params);
    
    const results = uploads.map(u => {
      const passPerc = u.total_students > 0 ? parseFloat(((u.pass_count / u.total_students) * 100).toFixed(1)) : 0;
      return {
        id: u.id,
        filename: u.filename,
        upload_date: new Date(u.upload_date).toISOString().replace('T', ' ').substring(0, 16),
        academic_year: u.academic_year,
        semester: u.semester,
        total_students: u.total_students,
        pass_percentage: passPerc,
        pass_count: u.pass_count,
        fail_count: u.fail_count
      };
    });

    res.json(results);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const deleteHistory = async (req, res) => {
  const uploadId = req.params.id;
  try {
    await pool.query('DELETE FROM students WHERE upload_id = ?', [uploadId]);
    await pool.query('DELETE FROM ledger_uploads WHERE id = ?', [uploadId]);

    const excelPath = path.join(generatedDir, `report_${uploadId}.xlsx`);
    if (fs.existsSync(excelPath)) {
      fs.unlinkSync(excelPath);
    }

    res.json({ message: 'Successfully deleted upload history record.' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
