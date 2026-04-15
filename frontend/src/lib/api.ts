const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

export async function fetchReferrals() {
  return request<any[]>("/referrals");
}

export async function fetchReferral(id: string) {
  return request<any>(`/referrals/${id}`);
}

export async function submitReferral(data: {
  patient_name: string;
  patient_dob?: string;
  patient_gender?: string;
  source_facility?: string;
  referral_text: string;
  insurance_provider?: string;
  insurance_id?: string;
}) {
  return request<any>("/referrals", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function fetchWorkflowLogs(referralId: string) {
  return request<{ referral_id: string; workflow_logs: any[] }>(
    `/referrals/${referralId}/workflow`
  );
}

export async function fetchLLMOutputs(referralId: string) {
  return request<{ referral_id: string; llm_outputs: any[] }>(
    `/referrals/${referralId}/llm-outputs`
  );
}

export async function fetchAllLogs() {
  return request<{ logs: any[]; total: number }>("/logs");
}
