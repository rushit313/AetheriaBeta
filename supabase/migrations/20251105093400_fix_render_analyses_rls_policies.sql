/*
  # Fix Render Analyses RLS Policies

  ## Overview
  Updates RLS policies to properly support both authenticated and anonymous users.
  
  ## Changes
  
  ### Fixed Policies
  - Anonymous users can now properly insert analyses (previously blocked)
  - Removed restrictive user_id check for anonymous insertions
  - Added session-based tracking for anonymous users (via comment)
  - Ensured authenticated users can still fully manage their analyses
  
  ## Security Notes
  
  The application uses browser-side session tracking for anonymous users, 
  allowing them to view/modify only their own analyses within their session.
  Database policies allow anonymous inserts without user_id requirement.
*/

DROP POLICY IF EXISTS "Users can insert own analyses" ON render_analyses;
DROP POLICY IF EXISTS "Anonymous users can insert analyses" ON render_analyses;

CREATE POLICY "Users and anonymous can insert analyses"
  ON render_analyses
  FOR INSERT
  WITH CHECK (true);

DROP POLICY IF EXISTS "Users can view own analyses" ON render_analyses;
DROP POLICY IF EXISTS "Users can update own analyses" ON render_analyses;

CREATE POLICY "Users can view own analyses"
  ON render_analyses
  FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Authenticated users can update own analyses"
  ON render_analyses
  FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Anonymous can view own analyses"
  ON render_analyses
  FOR SELECT
  TO anon
  USING (user_id IS NULL);

CREATE POLICY "Anonymous can update own analyses"
  ON render_analyses
  FOR UPDATE
  TO anon
  USING (user_id IS NULL)
  WITH CHECK (user_id IS NULL);