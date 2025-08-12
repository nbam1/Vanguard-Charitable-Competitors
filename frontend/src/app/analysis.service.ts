import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';

export interface AnalyzePayload {
  company_name: string;
  company_description: string;
  top_k: number;
}

export interface Match {
  id: string;
  score: number;
  name: string;
  description: string;
  url: string;
}

export interface AnalyzeResponse {
  matches: Match[];
  report: string;
}

@Injectable({ providedIn: 'root' })
export class AnalysisService {
  private http = inject(HttpClient);

  // Change this for prod (or wire up Angular environments)
  private API_URL = 'http://localhost:8000';

  searchAndAnalyze(payload: AnalyzePayload) {
    return this.http.post<AnalyzeResponse>(`${this.API_URL}/search-and-analyze`, payload);
  }
}
