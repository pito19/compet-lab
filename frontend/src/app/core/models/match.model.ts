export type MatchStatus = 'SCHEDULED' | 'POSTPONED' | 'CANCELLED' | 'PLAYED';

export interface Match {
  id: string;
  pool_id: string | null;
  home_team_id: string | null;
  away_team_id: string | null;
  scheduled_at: string | null;
  venue_id: string | null;
  status: MatchStatus;
}

export interface GenerateSchedulePayload {
  start_date: string;
  days_between_matchdays: number;
}

export interface RescheduleMatchPayload {
  scheduled_at: string;
  venue_id?: string | null;
}

export interface ScheduleConflict {
  type: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  match_id: string;
  message: string;
}

export interface MatchResult {
  id: string;
  match_id: string | null;
  home_score: number;
  away_score: number;
  is_validated: boolean;
  correction_count: number;
  updated_at: string;
}

export interface RecordResultPayload {
  home_score: number;
  away_score: number;
}
