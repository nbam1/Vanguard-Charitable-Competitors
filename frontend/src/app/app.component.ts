import { Component, ChangeDetectionStrategy, computed, signal, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms'; // +Validators
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { NgOptimizedImage } from '@angular/common';
import { DecimalPipe } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [
    ReactiveFormsModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatListModule,
    HttpClientModule,
    NgOptimizedImage,
    DecimalPipe,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
  <div class="container">
    <header>
      <img ngSrc="assets/logo-nimbl.png" width="140" height="46" alt="Nimbl Digital Logo" class="logo" />
      <h1>Competitor Analyzer</h1>
      <p class="subtitle accent">Empowering research for Vanguard Charitable</p>
    </header>

    <form [formGroup]="form" class="analysis-form" (ngSubmit)="onAnalyze()">
      <mat-form-field appearance="outline">
        <mat-label>Company Name</mat-label>
        <input matInput formControlName="company_name" required autocomplete="off">
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label>Company Description</mat-label>
        <textarea matInput formControlName="company_description" rows="3" required></textarea>
      </mat-form-field>

      <mat-form-field appearance="outline">
        <mat-label># of competitors</mat-label>
        <input
          matInput
          type="number"
          formControlName="top_k"
          min="1"
          max="50"
          step="1"
          placeholder="10">
        <mat-hint>1–50 (defaults to 10)</mat-hint>
      </mat-form-field>

      <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || loading()">
        {{ loading() ? "Analyzing..." : "Analyze Competitors" }}
      </button>
    </form>

    @if (report()) {
      <section>
        <h2>Competitor Analysis</h2>
        <pre class="analysis-report">{{ report() }}</pre>
      </section>
    }

    @if (matches().length) {
      <section>
        <h3>Top Matches ({{ matches().length }})</h3>
        <div class="card-grid">
          @for (match of matches(); track match.id) {
            <mat-card class="competitor-card">
              <mat-card-header>
                <mat-card-title class="company-name">{{ match.name }}</mat-card-title>
                <mat-card-subtitle class="score">Score: {{ match.score | number:'1.2-2' }}</mat-card-subtitle>
              </mat-card-header>
              <mat-card-content>
                <p class="description">{{ match.description }}</p>
              </mat-card-content>
            </mat-card>
          }
        </div>
      </section>
    }
  </div>
  `
})
export class AppComponent {
  private fb = inject(FormBuilder);
  private http = inject(HttpClient);

  form = this.fb.group({
    company_name: ['', Validators.required],
    company_description: ['', Validators.required],
    top_k: [10, [Validators.min(1), Validators.max(50)]], // new control
  });

  loading = signal(false);
  matches = signal<any[]>([]);
  report = signal<string | null>(null);

  onAnalyze() {
    if (this.form.invalid) return;
    this.loading.set(true);
    this.report.set(null);
    this.matches.set([]);

    const { company_name, company_description, top_k } = this.form.value;

    this.http.post<any>('http://localhost:8000/search-and-analyze', {
      company_name,
      company_description,
      top_k: Number(top_k) || 10, // ensure numeric
    })
    .subscribe({
      next: result => {
        this.report.set(result.report);
        this.matches.set(result.matches ?? []);
        this.loading.set(false);
      },
      error: err => {
        this.loading.set(false);
        alert('Error: ' + (err.error?.detail || err.message));
      }
    });
  }
}
