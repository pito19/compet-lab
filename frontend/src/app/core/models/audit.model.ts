export interface AuditEvent {
  id: string;
  actor_email: string;
  action: string;
  entity_type: string;
  entity_id: string | null;
  old_value: Record<string, unknown>;
  new_value: Record<string, unknown>;
  occurred_at: string;
}
