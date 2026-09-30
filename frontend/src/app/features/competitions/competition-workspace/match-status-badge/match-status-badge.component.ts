import { Component, input } from '@angular/core';
import { MatchStatus } from '../../../../core/models';

@Component({
  selector: 'cl-match-status-badge',
  template: `<span class="badge" [class]="cssClass()">{{ status() }}</span>`,
})
export class MatchStatusBadgeComponent {
  readonly status = input.required<MatchStatus>();

  protected cssClass(): string {
    switch (this.status()) {
      case 'PLAYED':
        return 'ok';
      case 'CANCELLED':
        return 'high';
      case 'POSTPONED':
      case 'SCHEDULED':
      default:
        return 'medium';
    }
  }
}
