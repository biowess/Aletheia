export type SourceType = "pubmed" | "doi" | "journal" | "guideline";
export type Severity = "low" | "moderate" | "high" | "critical";
export type FindingStrength = "weak" | "moderate" | "strong";
export type StepCategory = "diagnostic" | "monitoring" | "treatment" | "referral" | "follow_up";
export type Urgency = "routine" | "urgent" | "emergent";
export type MissingCategory = "history" | "labs" | "medications" | "imaging" |
                               "risk_factors" | "family_history" | "physical_exam";

export interface Citation {
  id: string;
  sourceType: SourceType;
  title: string;
  authors: string[];
  journal: string;
  year: number;
  verified: true;
  pmid?: string;
  doi?: string;
  canonicalUrl: string;
  sourceDomain: string;
  abstractSnippet?: string;
  evidenceLevel: "guideline" | "meta_analysis" | "systematic_review" | "rct" | "cohort" | "case_control" | "case_report" | "expert_opinion";
  vancouverString?: string;
}

export interface ClinicalSummary {
  overview: string;
  severity: Severity;
}

export interface SupportingFinding {
  finding: string;
  explanation: string;
  strength: FindingStrength;
}

export interface ContradictoryFinding {
  finding: string;
  explanation: string;
  significance: string;
}

export interface DifferentialDiagnosis {
  diagnosis: string;
  confidence: number;
  reasoning: string;
  supporting_evidence: string[];
  contradictory_evidence: string[];
}

export interface NextStep {
  title: string;
  category: StepCategory;
  rationale: string;
  urgency: Urgency;
  expected_outcome: string;
  risks_of_delay?: string;
}

export interface MissingInformation {
  item: string;
  category: MissingCategory;
  why_it_matters: string;
  impact_on_assessment: string;
  possible_implications: string;
}

export interface ReportVersion {
  id: string;
  case_id: string;
  version_number: number;
  created_at: string;
  
  summary: ClinicalSummary;
  supporting_findings: SupportingFinding[];
  contradictory_findings: ContradictoryFinding[];
  differentials: DifferentialDiagnosis[];
  next_steps: NextStep[];
  missing_information: MissingInformation[];
  citations: Citation[];
  
  preprocessing_summary: Record<string, any>;
  ai_provider: string;
  ai_model: string;
  grounding_used: boolean;
}
