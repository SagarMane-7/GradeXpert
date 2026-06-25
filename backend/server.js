import app from './src/app.js';
import { seedAdmin } from './src/config/db.js';
import dotenv from 'dotenv';

dotenv.config();

// Initialize default admin user
seedAdmin();

const PORT = process.env.PORT || 5001;

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Node Express gateway server active on port ${PORT}`);
});
