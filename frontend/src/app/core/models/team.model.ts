export interface Team {
  id: string;
  competition_id: string | null;
  name: string;
  club_name: string;
  pool_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTeamPayload {
  name: string;
  club_name: string;
}
