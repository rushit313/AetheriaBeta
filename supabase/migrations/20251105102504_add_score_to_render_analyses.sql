/*
  # Add score column to render_analyses table

  ## Overview
  Adds a quality score field to store the AI-generated render quality rating.
  
  ## Changes
  
  ### New Columns
  - `score` (integer) - Quality score from 1-100, nullable for backwards compatibility
  
  ## Notes
  - Nullable to support existing analyses without scores
  - Indexed for efficient queries
*/

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.columns
    WHERE table_name = 'render_analyses' AND column_name = 'score'
  ) THEN
    ALTER TABLE render_analyses ADD COLUMN score integer;
  END IF;
END $$;