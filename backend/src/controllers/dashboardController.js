import pool from '../config/db.js';

async function getActiveUploadId(userId, requestedUploadId) {
  if (requestedUploadId && requestedUploadId !== 'undefined' && requestedUploadId !== 'null') {
    return requestedUploadId;
  }
  const [rows] = await pool.query(
    'SELECT id FROM ledger_uploads WHERE uploaded_by = ? ORDER BY upload_date DESC LIMIT 1',
    [userId]
  );
  return rows.length > 0 ? rows[0].id : null;
}

export const getDashboardStats = async (req, res) => {
  try {
    const uploadId = await getActiveUploadId(req.user.id, req.query.upload_id);
    if (!uploadId) {
      return res.json({
        totalStudents: 0,
        passPercentage: 0,
        passedStudents: 0,
        failedStudents: 0,
        atktCount: 0,
        collegeTopper: null
      });
    }

    const [uploads] = await pool.query('SELECT * FROM ledger_uploads WHERE id = ?', [uploadId]);
    if (uploads.length === 0) return res.status(404).json({ error: 'Record not found' });
    const u = uploads[0];

    const passPerc = u.total_students > 0 ? parseFloat(((u.pass_count / u.total_students) * 100).toFixed(2)) : 0.0;

    const [topperRows] = await pool.query(
      `SELECT s.name, s.sgpa, b.name as branch 
       FROM students s 
       LEFT JOIN branches b ON s.branch_id = b.id 
       WHERE s.upload_id = ? AND s.sgpa IS NOT NULL 
       ORDER BY s.sgpa DESC LIMIT 1`,
      [uploadId]
    );

    const topper = topperRows.length > 0 ? {
      name: topperRows[0].name,
      branch: topperRows[0].branch || 'Unknown',
      percentage: topperRows[0].sgpa
    } : null;

    res.json({
      totalStudents: u.total_students,
      passedStudents: u.pass_count,
      failedStudents: u.fail_count,
      passPercentage: passPerc,
      atktCount: 0,
      collegeTopper: topper
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export { getActiveUploadId };
