-- Run this once on your Render PostgreSQL database to add the new columns.

ALTER TABLE ordens ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'Aberta';
ALTER TABLE ordens ADD COLUMN IF NOT EXISTS criado_em TIMESTAMP DEFAULT NOW();
