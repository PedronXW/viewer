CREATE TABLE IF NOT EXISTS vehicles (
  id SERIAL PRIMARY KEY,
  plate TEXT,
  features JSONB,
  damage JSONB,
  embedding JSONB,
  exemplar TEXT,
  score FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);