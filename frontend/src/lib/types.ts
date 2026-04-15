export interface Patient {
  id: string;
  name: string;
  date_of_birth: string | null;
  gender: string | null;
  insurance_provider: string | null;
  insurance_id: string | null;
  created_at: string | null;
}

export interface ClinicalData {
  diagnosis: string;
  mobility: string;
  comorbidities: string[];
  oxygen_required: boolean;
  cognitive_status: string;
  key_risks: string[];
  medications: string[];
  allergies: string[];
  age: number | null;
}

export interface RiskAssessment {
  risk_level: "low" | "medium" | "high";
  confidence: number;
  reasoning: string;
  risk_factors: string[];
  recommended_care_level: string;
}

export interface InsuranceStatus {
  has_insurance: boolean;
  provider: string | null;
  insurance_id: string | null;
  verified: boolean;
  in_network: boolean;
  coverage_level: string;
  reason: string;
}

export interface RulesOutput {
  all_results: RuleResult[];
  triggered_rules: RuleResult[];
  triggered_count: number;
  total_rules: number;
  override_decision: string | null;
  priority_adjustment: number;
}

export interface RuleResult {
  rule: string;
  triggered: boolean;
  effect?: string;
  message?: string;
  override_decision?: string;
  priority_boost?: number;
}

export interface Decision {
  id: string;
  referral_id: string;
  decision: "ACCEPT" | "REJECT" | "REVIEW";
  risk_level: string | null;
  risk_score: number | null;
  confidence: number | null;
  explanation: string | null;
  clinical_data: ClinicalData | null;
  insurance_status: InsuranceStatus | null;
  rules_output: RulesOutput | null;
  llm_reasoning: string | null;
  created_at: string | null;
}

export interface WorkflowRun {
  id: string;
  referral_id: string;
  status: string;
  current_step: string | null;
  started_at: string | null;
  completed_at: string | null;
  error: string | null;
}

export interface Referral {
  id: string;
  patient_id: string;
  source_facility: string | null;
  referral_text: string;
  status: string;
  created_at: string | null;
  patient?: Patient;
  decision?: Decision;
  workflow_run?: WorkflowRun;
}

export interface WorkflowStepLog {
  step_name: string;
  status: string;
  input_summary: string | null;
  output_summary: string | null;
  error: string | null;
  duration_ms: number | null;
  logged_at: string | null;
  workflow_id?: string;
}

export interface LLMOutput {
  id: string;
  referral_id: string;
  step: string;
  model: string;
  usage: { prompt_tokens: number; completion_tokens: number; total_tokens: number };
  raw_response: string;
  parsed_response: Record<string, unknown>;
  timestamp: string;
}

export interface ReferralSubmission {
  patient_name: string;
  patient_dob?: string;
  patient_gender?: string;
  source_facility?: string;
  referral_text: string;
  insurance_provider?: string;
  insurance_id?: string;
}
