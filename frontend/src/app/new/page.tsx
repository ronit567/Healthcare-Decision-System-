"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { submitReferral } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/card";
import { Send, Loader2 } from "lucide-react";

export default function NewReferralPage() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [form, setForm] = useState({
    patient_name: "",
    patient_dob: "",
    patient_gender: "",
    source_facility: "",
    referral_text: "",
    insurance_provider: "",
    insurance_id: "",
  });

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      const result = await submitReferral(form);
      router.push(`/referral/${result.referral_id}`);
    } catch (err: any) {
      setError(err.message);
      setSubmitting(false);
    }
  };

  const sampleReferral = `Patient: Margaret Thompson, 78-year-old female
Referring Facility: St. Mary's General Hospital
Date of Referral: 2024-03-15

Diagnosis: Left hip fracture status post ORIF (Open Reduction Internal Fixation), performed 3/12/2024.

Medical History: Type 2 Diabetes Mellitus (insulin-dependent), Hypertension, COPD (on 2L home oxygen), Mild cognitive impairment (MMSE 22/30), Osteoporosis, History of falls (3 in past 6 months).

Current Medications: Metformin 1000mg BID, Lantus 20 units at bedtime, Lisinopril 10mg daily, Tiotropium inhaler daily, Albuterol inhaler PRN, Alendronate 70mg weekly, Donepezil 5mg daily, Aspirin 81mg daily.

Functional Status: Prior to admission - ambulated with rolling walker, independent in ADLs with setup assistance. Current - non-weight bearing on left leg, requires max assist for transfers, wheelchair dependent. Oxygen requirement: 2L nasal cannula continuously.

Cognitive: Mild impairment, can follow 2-step commands, oriented x3.

Allergies: Penicillin (rash), Sulfa drugs (hives).

Insurance: Medicare Part A/B, supplemental Blue Cross plan.

Goals: Rehab to prior level of function, safe discharge home with family support.`;

  return (
    <div className="max-w-3xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">New Referral Submission</h1>
        <p className="text-sm text-muted mt-1">
          Submit a patient referral for AI-powered intake processing
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Patient Info */}
        <Card>
          <CardHeader>
            <h2 className="text-base font-semibold">Patient Information</h2>
          </CardHeader>
          <CardBody className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Patient Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={form.patient_name}
                onChange={(e) => update("patient_name", e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                placeholder="Full name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Date of Birth
              </label>
              <input
                type="text"
                value={form.patient_dob}
                onChange={(e) => update("patient_dob", e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                placeholder="YYYY-MM-DD"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">Gender</label>
              <select
                value={form.patient_gender}
                onChange={(e) => update("patient_gender", e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary bg-white"
              >
                <option value="">Select...</option>
                <option value="Female">Female</option>
                <option value="Male">Male</option>
                <option value="Other">Other</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Source Facility
              </label>
              <input
                type="text"
                value={form.source_facility}
                onChange={(e) => update("source_facility", e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                placeholder="Referring hospital/clinic"
              />
            </div>
          </CardBody>
        </Card>

        {/* Insurance */}
        <Card>
          <CardHeader>
            <h2 className="text-base font-semibold">Insurance Information</h2>
          </CardHeader>
          <CardBody className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">
                Insurance Provider
              </label>
              <input
                type="text"
                value={form.insurance_provider}
                onChange={(e) => update("insurance_provider", e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                placeholder="e.g., Medicare, Blue Cross"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">
                Insurance ID
              </label>
              <input
                type="text"
                value={form.insurance_id}
                onChange={(e) => update("insurance_id", e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary"
                placeholder="Policy/member ID"
              />
            </div>
          </CardBody>
        </Card>

        {/* Referral Text */}
        <Card>
          <CardHeader className="flex items-center justify-between">
            <h2 className="text-base font-semibold">Referral Document</h2>
            <button
              type="button"
              onClick={() => {
                setForm({
                  patient_name: "Margaret Thompson",
                  patient_dob: "1946-05-12",
                  patient_gender: "Female",
                  source_facility: "St. Mary's General Hospital",
                  referral_text: sampleReferral,
                  insurance_provider: "Medicare",
                  insurance_id: "1EG4-TE5-MK72",
                });
              }}
              className="text-xs text-primary hover:underline"
            >
              Load Sample Referral
            </button>
          </CardHeader>
          <CardBody>
            <textarea
              required
              rows={12}
              value={form.referral_text}
              onChange={(e) => update("referral_text", e.target.value)}
              className="w-full px-3 py-2 border border-border rounded-lg text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary resize-y"
              placeholder="Paste the full referral document here..."
            />
          </CardBody>
        </Card>

        {/* Error + Submit */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={submitting}
          className="flex items-center gap-2 px-6 py-3 bg-primary text-white font-medium rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {submitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing Pipeline...
            </>
          ) : (
            <>
              <Send className="w-4 h-4" />
              Submit Referral
            </>
          )}
        </button>
      </form>
    </div>
  );
}
