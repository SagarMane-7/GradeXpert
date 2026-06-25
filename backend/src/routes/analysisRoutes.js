import express from 'express';
import { getBranchAnalysis, getFailedAnalysis, getMeritAnalysis, getSubjectAnalysis, getStudentMarks, getSubjectToppers } from '../controllers/analysisController.js';
import { authenticateToken } from '../middlewares/authMiddleware.js';

const router = express.Router();

router.get('/branch', authenticateToken, getBranchAnalysis);
router.get('/failed', authenticateToken, getFailedAnalysis);
router.get('/merit', authenticateToken, getMeritAnalysis);
router.get('/subject', authenticateToken, getSubjectAnalysis);
router.get('/student-marks/:seat_no', authenticateToken, getStudentMarks);
router.get('/subject-toppers', authenticateToken, getSubjectToppers);

export default router;
