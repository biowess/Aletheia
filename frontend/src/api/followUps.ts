import { apiClient } from './client';
import { FollowUpEntry, FollowUpCreatePayload } from '../types';

/**
 * Retrieves all follow-up entries for a specific case.
 * @param caseId The unique identifier of the case.
 * @returns A promise resolving to an array of follow-up entries.
 */
export async function listFollowUps(caseId: string): Promise<FollowUpEntry[]> {
  return apiClient.get<FollowUpEntry[]>(`/cases/${caseId}/follow-ups`);
}

/**
 * Creates a new follow-up entry for a specific case.
 * @param caseId The unique identifier of the case.
 * @param data The payload containing the follow-up data.
 * @returns A promise resolving to the created follow-up entry.
 */
export async function createFollowUp(caseId: string, data: FollowUpCreatePayload): Promise<FollowUpEntry> {
  return apiClient.post<FollowUpEntry>(`/cases/${caseId}/follow-ups`, data);
}
