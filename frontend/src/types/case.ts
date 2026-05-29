export interface AnamnesisData {
  chief_complaint?: string;
  history_of_present_illness?: string;
  past_medical_history?: string;
  medications?: string;
  allergies?: string;
  family_history?: string;
  social_history?: string;
  travel_history?: string;
  constitutional_symptoms?: string;
}

export interface PhysicalExamData {
  general_appearance?: string;
  heent?: string;
  neck?: string;
  cardiovascular?: string;
  respiratory?: string;
  abdominal?: string;
  neurologic?: string;
  psychiatric?: string;
  vascular?: string;
  genitourinary?: string;
  endocrine?: string;
  dermatologic?: string;
  lymphatic?: string;
  musculoskeletal?: string;
  breast?: string;
  pelvic?: string;
  rectal?: string;
}

export interface LaboratoryData {
  cbc?: string;
  differential?: string;
  coagulation?: string;
  chemistry?: string;
  inflammatory_markers?: string;
  iron_studies?: string;
  hemolysis_markers?: string;
  endocrine_panels?: string;
}

export interface MorphologicalData {
  xray?: string;
  ct?: string;
  mri?: string;
  ultrasound?: string;
  pathology?: string;
  peripheral_smear?: string;
  biopsy?: string;
  flow_cytometry?: string;
}

export interface CaseCreatePayload {
  title: string;
  anamnesis: AnamnesisData;
  physical_exam: PhysicalExamData;
  laboratory_data: LaboratoryData;
  morphological_data: MorphologicalData;
  tags: string[];
  notes?: string;
}

export interface CaseUpdatePayload {
  title?: string;
  anamnesis?: AnamnesisData;
  physical_exam?: PhysicalExamData;
  laboratory_data?: LaboratoryData;
  morphological_data?: MorphologicalData;
  tags?: string[];
  notes?: string;
}

export interface Case {
  id: string;
  title: string;
  anamnesis: AnamnesisData;
  physical_exam: PhysicalExamData;
  laboratory_data: LaboratoryData;
  morphological_data: MorphologicalData;
  tags: string[];
  notes?: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

export interface CaseListItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
  tags: string[];
}
