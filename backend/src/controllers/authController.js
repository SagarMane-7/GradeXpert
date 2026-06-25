import bcrypt from 'bcrypt';
import jwt from 'jsonwebtoken';
import pool from '../config/db.js';

export const registerUser = async (req, res) => {
  const { name, registration_id, institute, department, password } = req.body;
  if (!name || !registration_id || !department || !password) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  try {
    const [existing] = await pool.query('SELECT * FROM users WHERE username = ?', [registration_id]);
    if (existing.length > 0) {
      return res.status(400).json({ error: 'User with this Registration ID already exists' });
    }

    let branchId = null;
    const [branches] = await pool.query('SELECT id FROM branches WHERE name = ?', [department]);
    if (branches.length > 0) {
      branchId = branches[0].id;
    } else {
      const [insertBranch] = await pool.query('INSERT INTO branches (name) VALUES (?) RETURNING id', [department]);
      branchId = insertBranch[0].id;
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await pool.query(
      'INSERT INTO users (username, password_hash, role, branch_id, name, registration_id, institute) VALUES (?, ?, ?, ?, ?, ?, ?)',
      [registration_id, hashedPassword, 'faculty', branchId, name, registration_id, institute]
    );

    res.status(201).json({ message: 'Successfully registered!' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const loginUser = async (req, res) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Missing username or password' });
  }

  try {
    const [users] = await pool.query('SELECT * FROM users WHERE username = ?', [username]);
    if (users.length === 0) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const user = users[0];
    const passwordMatch = await bcrypt.compare(password, user.password_hash);
    if (!passwordMatch) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }

    const token = jwt.sign(
      { id: user.id, username: user.username, role: user.role, branch_id: user.branch_id },
      process.env.JWT_SECRET || 'new-secret-key-2026-v2',
      { expiresIn: '24h' }
    );

    res.json({
      access_token: token,
      role: user.role,
      name: user.name || 'User'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const getMe = async (req, res) => {
  try {
    const [users] = await pool.query('SELECT * FROM users WHERE id = ?', [req.user.id]);
    if (users.length === 0) return res.status(404).json({ error: 'User not found' });

    const user = users[0];
    let branchName = 'All Branches';
    if (user.branch_id) {
      const [branches] = await pool.query('SELECT name FROM branches WHERE id = ?', [user.branch_id]);
      if (branches.length > 0) branchName = branches[0].name;
    }

    res.json({
      id: user.id,
      username: user.username,
      role: user.role.toUpperCase(),
      branch: branchName,
      created_at: new Date(user.created_at).toISOString().split('T')[0]
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
