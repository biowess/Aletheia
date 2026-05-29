import { apiClient } from './client';
import {
  Case,
  CaseListItem,
  CaseCreatePayload,
  CaseUpdatePayload
} from '../types';

/**
 * Retrieves a list of all clinical cases.
 * @param includeArchived Whether to include archived cases in the result.
 * @returns A promise resolving to an array of case list items.
 */
export async function listCases(includeArchived: boolean = false): Promise<CaseListItem[]> {
  const query = includeArchived ? '?include_archived=true' : '';
  return apiClient.get<CaseListItem[]>(`/cases${query}`);
}

/**
 * Retrieves a specific case by its ID.
 * @param id The unique identifier of the case.
 * @returns A promise resolving to the full case details.
 */
export async function getCase(id: string): Promise<Case> {
  return apiClient.get<Case>(`/cases/${id}`);
}

/**
 * Creates a new clinical case.
 * @param data The payload containing initial case data.
 * @returns A promise resolving to the created case.
 */
export async function createCase(data: CaseCreatePayload): Promise<Case> {
  return apiClient.post<Case>('/cases', data);
}

/**
 * Updates an existing clinical case.
 * @param id The unique identifier of the case to update.
 * @param data The payload containing fields to update.
 * @returns A promise resolving to the updated case.
 */
export async function updateCase(id: string, data: CaseUpdatePayload): Promise<Case> {
  return apiClient.put<Case>(`/cases/${id}`, data);
}

/**
 * Archives a clinical case.
 * @param id The unique identifier of the case to archive.
 * @returns A promise resolving to the archived case.
 */
export async function archiveCase(id: string): Promise<Case> {
  return apiClient.post<Case>(`/cases/${id}/archive`, {});
}

/**
 * Unarchives a clinical case.
 * @param id The unique identifier of the case to unarchive.
 * @returns A promise resolving to the unarchived case.
 */
export async function unarchiveCase(id: string): Promise<Case> {
  return apiClient.post<Case>(`/cases/${id}/unarchive`, {});
}

/**
 * Deletes a clinical case permanently.
 * @param id The unique identifier of the case to delete.
 * @returns A promise resolving to an object indicating success.
 */
export async function deleteCase(id: string): Promise<{ deleted: boolean }> {
  await apiClient.del<{ deleted: boolean }>(`/cases/${id}`);
  return { deleted: true };
}
