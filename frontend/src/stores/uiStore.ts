import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

interface UiState {
  activeTab: 'workspace' | 'timeline' | 'versions';
  sidebarCollapsed: boolean;
  bottomPanelVisible: boolean;
  
  setActiveTab: (tab: 'workspace' | 'timeline' | 'versions') => void;
  toggleSidebar: () => void;
  toggleBottomPanel: () => void;
}

export const useUiStore = create<UiState>()(
  immer((set) => ({
    activeTab: 'workspace',
    sidebarCollapsed: false,
    bottomPanelVisible: false,

    setActiveTab: (tab) => set((state) => { state.activeTab = tab; }),
    toggleSidebar: () => set((state) => { state.sidebarCollapsed = !state.sidebarCollapsed; }),
    toggleBottomPanel: () => set((state) => { state.bottomPanelVisible = !state.bottomPanelVisible; }),
  }))
);
