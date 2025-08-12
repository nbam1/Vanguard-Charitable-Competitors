import { Component, ChangeDetectionStrategy, signal, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { MatCardModule } from '@angular/material/card';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { NgOptimizedImage, DecimalPipe } from '@angular/common';

import { AnalysisService, AnalyzeResponse } from './analysis.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    HttpClientModule,
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatListModule,
    NgOptimizedImage,
    DecimalPipe,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './app.component.html',
})
export class AppComponent {
  private fb = inject(FormBuilder);
  private api = inject(AnalysisService);

  form = this.fb.group({
    company_name: ['', Validators.required],
    company_description: ['', Validators.required],
    top_k: [10, [Validators.min(1), Validators.max(50)]],
  });

  loading = signal(false);
  matches = signal<AnalyzeResponse['matches']>([]);
  report = signal<string | null>(null);

  onAnalyze(): void {
    if (this.form.invalid) return;

    this.loading.set(true);
    this.report.set(null);
    this.matches.set([]);

    const { company_name, company_description, top_k } = this.form.value;

    this.api
      .searchAndAnalyze({
        company_name: company_name ?? '',
        company_description: company_description ?? '',
        top_k: Number(top_k) || 10,
      })
      .subscribe({
        next: (res) => {
          this.report.set(res.report);
          this.matches.set(res.matches ?? []);
          this.loading.set(false);
        },
        error: (err) => {
          this.loading.set(false);
          alert('Error: ' + (err?.error?.detail || err.message || 'Unknown error'));
        },
      });
  }
}
