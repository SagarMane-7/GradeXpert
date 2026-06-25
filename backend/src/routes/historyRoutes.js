import express from 'express';
import { getHistory, deleteHistory } from '../controllers/historyController.js';
import { authenticateToken } from '../middlewares/authMiddleware.js';

const router = express.Router();

router.get('/', authenticateToken, getHistory);
router.delete('/:id', authenticateToken, deleteHistory);

export default router;
