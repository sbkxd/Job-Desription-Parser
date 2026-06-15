import { JobIntelligenceReport } from '../types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export class ApiService {
  /**
   * Run parser pipeline on a job description URL
   */
  static async analyzeUrl(url: string): Promise<JobIntelligenceReport> {
    const response = await fetch(`${API_BASE_URL}/pipeline/run/url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `Server returned ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Run parser pipeline on an uploaded PDF file
   */
  static async analyzeFile(file: File): Promise<JobIntelligenceReport> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/pipeline/run/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `Server returned ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Check connection and health of backend
   */
  static async checkHealth(): Promise<{ status: string; environment: string }> {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Backend is unreachable or unhealthy');
    }

    return response.json();
  }
}
