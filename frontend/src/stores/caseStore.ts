import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { CaseListItem, Case } from '../types';
import { listCases, getCase } from '../api/cases';

interface CaseState {
  cases: CaseListItem[];
  activeCaseId: string | null;
  activeCase: Case | null;
  isLoading: boolean;
  error: string | null;
  
  setCases: (cases: CaseListItem[]) => void;
  setActiveCase: (activeCase: Case | null) => void;
  setActiveCaseId: (id: string | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearActiveCase: () => void;
  
  fetchCases: (includeArchived?: boolean) => Promise<void>;
  fetchCase: (id: string) => Promise<void>;
}

export const useCaseStore = create<CaseState>()(
  immer((set) => ({
    cases: [],
    activeCaseId: null,
    activeCase: null,
    isLoading: false,
    error: null,

    setCases: (cases) => set((state) => { state.cases = cases; }),
    setActiveCase: (activeCase) => set((state) => { state.activeCase = activeCase; }),
    setActiveCaseId: (id) => set((state) => { state.activeCaseId = id; }),
    setLoading: (isLoading) => set((state) => { state.isLoading = isLoading; }),
    setError: (error) => set((state) => { state.error = error; }),
    clearActiveCase: () => set((state) => {
      state.activeCaseId = null;
      state.activeCase = null;
    }),

    fetchCases: async (includeArchived = false) => {
      set((state) => {
        state.isLoading = true;
        state.error = null;
      });
      try {
        const cases = await listCases(includeArchived);
        set((state) => { state.cases = cases; });
      } catch (err: any) {
        set((state) => { state.error = err.message || 'Failed to fetch cases'; });
      } finally {
        set((state) => { state.isLoading = false; });
      }
    },

    fetchCase: async (id: string) => {
      set((state) => {
        state.isLoading = true;
        state.error = null;
      });
      try {
        const activeCase = await getCase(id);
        set((state) => {
          state.activeCase = activeCase;
          state.activeCaseId = id;
        });
      } catch (err: any) {
        set((state) => { state.error = err.message || 'Failed to fetch case'; });
      } finally {
        set((state) => { state.isLoading = false; });
      }
    }
  }))
);
