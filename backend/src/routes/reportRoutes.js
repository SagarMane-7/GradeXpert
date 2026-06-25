import express from 'express';
import { downloadReport } from '../controllers/reportController.js';

const router = express.Router();

router.get('/:id', downloadReport);

export default router;
