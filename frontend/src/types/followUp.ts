import {
  AnamnesisData,
  PhysicalExamData,
  LaboratoryData,
  MorphologicalData
} from './case';

export interface FollowUpCreatePayload {
  entry_type: 'anamnesis' | 'physical_exam' | 'laboratory' | 'imaging' | 'procedure' | 'general_note' | 'other';
  title: string;
  
  anamnesis_delta?: AnamnesisData;
  physical_exam_delta?: PhysicalExamData;
  laboratory_delta?: LaboratoryData;
  morphological_delta?: MorphologicalData;
  
  free_text_note?: string;
}

export interface FollowUpEntry {
  id: string;
  case_id: string;
  created_at: string;
  
  entry_type: string;
  title: string;
  
  anamnesis_delta: Record<string, any>;
  physical_exam_delta: Record<string, any>;
  laboratory_delta: Record<string, any>;
  morphological_delta: Record<string, any>;
  
  free_text_note?: string;
  triggered_report_id?: string;
}
