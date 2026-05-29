import { apiClient } from './client';
import { AppSetting, AppSettingsBulk } from '../types';

/**
 * Retrieves all application settings.
 * @returns A promise resolving to the bulk settings payload.
 */
export async function getAllSettings(): Promise<AppSettingsBulk> {
  return apiClient.get<AppSettingsBulk>('/settings');
}

/**
 * Retrieves a specific application setting by its key.
 * @param key The setting key to retrieve.
 * @returns A promise resolving to the application setting.
 */
export async function getSetting(key: string): Promise<AppSetting> {
  return apiClient.get<AppSetting>(`/settings/${key}`);
}

/**
 * Updates a specific application setting.
 * @param key The setting key to update.
 * @param value The new value for the setting.
 * @returns A promise resolving to the updated application setting.
 */
export async function updateSetting(key: string, value: string): Promise<AppSetting> {
  return apiClient.put<AppSetting>(`/settings/${key}`, { value });
}

/**
 * Clears the evidence cache manually.
 * @returns A promise resolving to the number of deleted entries.
 */
export async function cleanupCache(): Promise<{deleted_entries: number}> {
  return apiClient.post<{deleted_entries: number}>('/admin/maintenance/cleanup-cache', undefined);
}

/**
 * Retrieves statistics for the evidence cache.
 * @returns A promise resolving to cache statistics.
 */
export async function getCacheStats(): Promise<{total_entries: number, expired_entries: number, valid_entries: number}> {
  return apiClient.get<{total_entries: number, expired_entries: number, valid_entries: number}>('/admin/maintenance/cache-stats');
}
