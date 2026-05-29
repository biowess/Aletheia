import {
  AnamnesisData,
  PhysicalExamData,
  LaboratoryData,
  MorphologicalData
} from './case';

export interface ReasoningRequest {
  case_id: string;
  anamnesis: AnamnesisData;
  physical_exam: PhysicalExamData;
  laboratory_data: LaboratoryData;
  morphological_data: MorphologicalData;
  follow_up_context?: string;
  use_grounding?: boolean;
  force_cache_refresh?: boolean;
}

export interface ReasoningResponse {
  report_version_id: string;
  case_id: string;
  version_number: number;
  status: string;
  message?: string;
}
