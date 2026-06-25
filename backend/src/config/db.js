import pg from 'pg';
import bcrypt from 'bcrypt';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

const pgPool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: {
    rejectUnauthorized: false
  }
});

// Wrapper to mimic mysql2 syntax so we don't have to rewrite 500 lines of code
const pool = {
  query: async (text, params) => {
    // Automatically convert ? to $1, $2, etc.
    let i = 1;
    const pgText = text.replace(/\?/g, () => `$${i++}`);
    const res = await pgPool.query(pgText, params);
    // mysql2 returns [rows, fields]
    return [res.rows, res.fields];
  },
  getConnection: async () => {
    const client = await pgPool.connect();
    return {
      query: async (text, params) => {
        let i = 1;
        const pgText = text.replace(/\?/g, () => `$${i++}`);
        const res = await client.query(pgText, params);
        return [res.rows, res.fields];
      },
      beginTransaction: async () => client.query('BEGIN'),
      commit: async () => client.query('COMMIT'),
      rollback: async () => client.query('ROLLBACK'),
      release: () => client.release()
    };
  }
};

export async function seedAdmin() {
  try {
    const [rows] = await pool.query("SELECT * FROM users WHERE role = 'admin'");
    if (rows.length === 0) {
      const passwordHash = await bcrypt.hash('admin123', 10);
      await pool.query(
        'INSERT INTO users (username, password_hash, role, name, registration_id, institute) VALUES (?, ?, ?, ?, ?, ?)',
        ['admin', passwordHash, 'admin', 'Administrator', 'ADMIN001', 'PICT']
      );
      console.log('Default Admin user initialized: admin / admin123');
    }
  } catch (error) {
    console.error('Error seeding admin user:', error);
  }
}

export default pool;
