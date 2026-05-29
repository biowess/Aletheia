import { apiClient } from './client';
import { ReasoningRequest, ReasoningResponse, ReportVersion } from '../types';

/**
 * Generates a new reasoning report for a case based on current data.
 * @param data The request payload containing case data and configuration.
 * @returns A promise resolving to the reasoning response (often acknowledging generation start or returning result).
 */
export async function generateReport(data: ReasoningRequest): Promise<ReasoningResponse> {
  return apiClient.post<ReasoningResponse>('/reasoning/generate', data);
}

/**
 * Retrieves all report versions for a specific case.
 * @param caseId The unique identifier of the case.
 * @returns A promise resolving to an array of report versions.
 */
export async function listReports(caseId: string): Promise<ReportVersion[]> {
  return apiClient.get<ReportVersion[]>(`/reasoning/cases/${caseId}/reports`);
}

/**
 * Retrieves a specific report version by its ID.
 * @param reportId The unique identifier of the report.
 * @returns A promise resolving to the report version details.
 */
export async function getReport(reportId: string): Promise<ReportVersion> {
  return apiClient.get<ReportVersion>(`/reasoning/reports/${reportId}`);
}
