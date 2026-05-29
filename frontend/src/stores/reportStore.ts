import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import { ReportVersion, ReasoningRequest } from '../types';
import { listReports, generateReport as apiGenerateReport } from '../api/reasoning';

interface ReportState {
  reports: ReportVersion[];
  activeReport: ReportVersion | null;
  isGenerating: boolean;
  generationError: string | null;
  
  setReports: (reports: ReportVersion[]) => void;
  setActiveReport: (activeReport: ReportVersion | null) => void;
  setGenerating: (isGenerating: boolean) => void;
  setGenerationError: (error: string | null) => void;
  
  fetchReports: (caseId: string) => Promise<void>;
  generateReport: (request: ReasoningRequest, onSuccess?: (report: ReportVersion) => void) => Promise<void>;
}

export const useReportStore = create<ReportState>()(
  immer((set) => ({
    reports: [],
    activeReport: null,
    isGenerating: false,
    generationError: null,

    setReports: (reports) => set((state) => { state.reports = reports; }),
    setActiveReport: (activeReport) => set((state) => { state.activeReport = activeReport; }),
    setGenerating: (isGenerating) => set((state) => { state.isGenerating = isGenerating; }),
    setGenerationError: (error) => set((state) => { state.generationError = error; }),

    fetchReports: async (caseId: string) => {
      set((state) => {
        state.generationError = null;
      });
      try {
        const reports = await listReports(caseId);
        const sorted = [...reports].sort((a, b) => b.version_number - a.version_number);
        set((state) => {
          state.reports = sorted;
          state.activeReport = sorted.length > 0 ? sorted[0] : null;
        });
      } catch (err: any) {
        // Here we could handle fetch error, but requirements say setting generationError or handling isLoading
      }
    },

    generateReport: async (request: ReasoningRequest, onSuccess?: (report: ReportVersion) => void) => {
      set((state) => {
        state.isGenerating = true;
        state.generationError = null;
      });
      try {
        await apiGenerateReport(request);
        const freshReports = await listReports(request.case_id);
        const sorted = [...freshReports].sort((a, b) => b.version_number - a.version_number);
        set((state) => {
          state.reports = sorted;
          state.activeReport = sorted.length > 0 ? sorted[0] : null;
        });
        if (sorted.length > 0 && onSuccess) {
          onSuccess(sorted[0]);
        }
      } catch (err: any) {
        set((state) => {
          state.generationError = err.message || 'Failed to generate report. Please try again.';
        });
      } finally {
        set((state) => { state.isGenerating = false; });
      }
    }
  }))
);
