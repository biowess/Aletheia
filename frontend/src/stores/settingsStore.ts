import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { AppSetting } from '../types';
import { getAllSettings, updateSetting as apiUpdateSetting } from '../api/settings';

interface SettingsState {
  settings: AppSetting[];
  isLoading: boolean;
  
  fetchSettings: () => Promise<void>;
  updateSetting: (key: string, value: string) => Promise<void>;
}

export const useSettingsStore = create<SettingsState>()(
  immer((set) => ({
    settings: [],
    isLoading: false,

    fetchSettings: async () => {
      set((state) => {
        state.isLoading = true;
      });
      try {
        const response = await getAllSettings();
        set((state) => { state.settings = response.settings; });
      } catch (err: any) {
        // Handle error if needed
      } finally {
        set((state) => { state.isLoading = false; });
      }
    },

    updateSetting: async (key: string, value: string) => {
      set((state) => {
        state.isLoading = true;
      });
      try {
        const updatedSetting = await apiUpdateSetting(key, value);
        set((state) => {
          const index = state.settings.findIndex((s: AppSetting) => s.key === key);
          if (index !== -1) {
            state.settings[index] = updatedSetting;
          } else {
            state.settings.push(updatedSetting);
          }
        });
      } catch (err: any) {
        // Handle error if needed
      } finally {
        set((state) => { state.isLoading = false; });
      }
    }
  }))
);
