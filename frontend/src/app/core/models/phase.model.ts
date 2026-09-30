export interface Phase {
  id: string;
  competition_id: string | null;
  name: string;
  order: number;
  created_at: string;
  updated_at: string;
}

export interface Pool {
  id: string;
  phase_id: string | null;
  name: string;
  team_ids: string[];
  created_at: string;
  updated_at: string;
}

export interface CreatePhasePayload {
  name: string;
  order: number;
}

export interface CreatePoolPayload {
  name: string;
}
