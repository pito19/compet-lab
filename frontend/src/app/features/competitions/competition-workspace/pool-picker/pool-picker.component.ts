import { Component, inject } from '@angular/core';
import { CompetitionContextService } from '../competition-context.service';

/**
 * Pool selector shared by the Calendar, Results and Standings tabs.
 * The selection lives in CompetitionContextService, so it persists
 * when switching tabs.
 */
@Component({
  selector: 'cl-pool-picker',
  template: `
    <div class="card pool-picker">
      <label>
        Poule
        <select (change)="onChange($event)">
          @for (pool of context.pools(); track pool.id) {
            <option [value]="pool.id" [selected]="pool.id === context.selectedPoolId()">
              {{ pool.phase_name }} — {{ pool.name }}
            </option>
          }
        </select>
      </label>
    </div>
  `,
  styles: [
    `
      label { display: flex; flex-direction: column; gap: 0.3rem; font-size: 0.8rem; }
    `,
  ],
})
export class PoolPickerComponent {
  protected readonly context = inject(CompetitionContextService);

  protected onChange(event: Event): void {
    this.context.selectedPoolId.set((event.target as HTMLSelectElement).value);
  }
}
