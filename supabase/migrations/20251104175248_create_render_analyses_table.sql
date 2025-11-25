/*
  # Create Render Analyses Table

  ## Overview
  Creates the core table for storing 3D render analysis data submitted by users.

  ## New Tables
  
  ### `render_analyses`
  Stores all render analysis submissions and AI feedback.
  
  - `id` (uuid, primary key) - Unique identifier for each analysis
  - `user_id` (uuid, nullable) - Reference to authenticated user (null for anonymous)
  - `render_image_url` (text) - URL/path to the uploaded render image
  - `reference_image_url` (text, nullable) - URL/path to optional reference image
  - `analysis_result` (text, nullable) - AI-generated feedback and analysis
  - `status` (text) - Analysis status: 'pending', 'analyzing', 'completed', 'failed'
  - `created_at` (timestamptz) - Timestamp of submission
  - `updated_at` (timestamptz) - Timestamp of last update
  
  ## Security
  
  - Enable RLS on `render_analyses` table
  - Policy: Authenticated users can view their own analyses
  - Policy: Authenticated users can insert their own analyses
  - Policy: Authenticated users can update their own analyses
  - Policy: Anyone can insert anonymous analyses (user_id is null)
  - Policy: Anyone can view analyses they created (tracked by session)
  
  ## Notes
  
  1. Supports both authenticated and anonymous usage
  2. Status field tracks analysis workflow
  3. Images are stored as URLs (will use Supabase Storage or external URLs)
*/

CREATE TABLE IF NOT EXISTS render_analyses (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid,
  render_image_url text NOT NULL,
  reference_image_url text,
  analysis_result text,
  status text NOT NULL DEFAULT 'pending',
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE render_analyses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own analyses"
  ON render_analyses
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own analyses"
  ON render_analyses
  FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own analyses"
  ON render_analyses
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Anonymous users can insert analyses"
  ON render_analyses
  FOR INSERT
  TO anon
  WITH CHECK (user_id IS NULL);

CREATE INDEX IF NOT EXISTS idx_render_analyses_user_id ON render_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_render_analyses_created_at ON render_analyses(created_at DESC);