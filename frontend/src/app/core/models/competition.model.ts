export type CompetitionType = 'CHAMPIONSHIP' | 'CUP' | 'TOURNAMENT';
export type CompetitionStatus = 'DRAFT' | 'ACTIVE' | 'CLOSED';

export interface Competition {
  id: string;
  season_id: string | null;
  name: string;
  category: string;
  gender: string;
  type: CompetitionType;
  status: CompetitionStatus;
  is_published: boolean;
  legacy_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreateCompetitionPayload {
  season_id: string;
  name: string;
  category: string;
  // Optional on the backend: CompetitionCreateRequest.gender defaults to "MIXED".
  gender?: string;
  type: CompetitionType;
}
