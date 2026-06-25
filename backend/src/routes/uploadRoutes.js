import express from 'express';
import upload from '../middlewares/uploadMiddleware.js';
import { authenticateToken } from '../middlewares/authMiddleware.js';
import { uploadLedger } from '../controllers/uploadController.js';

const router = express.Router();

router.post('/', authenticateToken, upload.single('ledger'), uploadLedger);

export default router;
