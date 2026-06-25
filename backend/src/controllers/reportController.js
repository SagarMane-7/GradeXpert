import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const generatedDir = path.join(__dirname, '..', '..', '..', 'generated');

export const downloadReport = (req, res) => {
  const uploadId = req.params.id;
  const filePath = path.join(generatedDir, `report_${uploadId}.xlsx`);
  
  if (fs.existsSync(filePath)) {
    res.download(filePath, `Student_Result_Report_${uploadId}.xlsx`);
  } else {
    res.status(404).json({ error: 'Report file not found. Ensure file parsing was processed correctly.' });
  }
};
