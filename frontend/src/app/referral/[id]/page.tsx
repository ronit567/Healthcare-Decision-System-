"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchReferral, fetchWorkflowLogs, fetchLLMOutputs } from "@/lib/api";
import type { Referral, WorkflowStepLog, LLMOutput } from "@/lib/types";
import { Card, CardHeader, CardBody } from "@/components/card";
import {
  DecisionBadge,
  RiskBadge,
  StatusBadge,
  Badge,
} from "@/components/badge";
import {
  ArrowLeft,
  User,
  Shield,
  Brain,
  Stethoscope,
  Scale,
  Activity,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

export default function ReferralDetailPage() {
  const params = useParams();
  const id = params.id as string;

  const [referral, setReferral] = useState<Referral | null>(null);
  const [workflowLogs, setWorkflowLogs] = useState<WorkflowStepLog[]>([]);
  const [llmOutputs, setLLMOutputs] = useState<LLMOutput[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedStep, setExpandedStep] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const [ref, wf, llm] = await Promise.all([
          fetchReferral(id),
          fetchWorkflowLogs(id),
          fetchLLMOutputs(id),
        ]);
        setReferral(ref);
        setWorkflowLogs(wf.workflow_logs || []);
        setLLMOutputs(llm.llm_outputs || []);
      } catch (e: any) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Clock className="w-6 h-6 text-muted animate-spin" />
        <span className="ml-2 text-muted">Loading referral details...</span>
      </div>
    );
  }

  if (error || !referral) {
    return (
      <div className="flex flex-col items-center justify-center h-64 text-red-500">
        <AlertTriangle className="w-8 h-8 mb-2" />
        <p>{error || "Referral not found"}</p>
        <Link href="/" className="mt-4 text-sm text-primary hover:underline">
          Back to Inbox
        </Link>
      </div>
    );
  }

  const decision = referral.decision;
  const clinical = decision?.clinical_data;
  const insurance = decision?.insurance_status;
  const rules = decision?.rules_output;

  return (
    <div className="space-y-6">
      {/* Back link + header */}
      <div>
        <Link
          href="/"
          className="inline-flex items-center gap-1 text-sm text-muted hover:text-foreground mb-4"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Inbox
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">
              {referral.patient?.name || "Unknown Patient"}
            </h1>
            <p className="text-sm text-muted mt-1">
              Referral from {referral.source_facility || "Unknown"} ·{" "}
              {referral.created_at
                ? new Date(referral.created_at).toLocaleString()
                : ""}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <StatusBadge status={referral.status} />
            {decision?.risk_level && (
              <RiskBadge level={decision.risk_level} />
            )}
            {decision?.decision && (
              <DecisionBadge decision={decision.decision} />
            )}
          </div>
        </div>
      </div>

      {/* Decision Panel */}
      {decision && (
        <Card
          className={`border-2 ${
            decision.decision === "ACCEPT"
              ? "border-emerald-300"
              : decision.decision === "REJECT"
              ? "border-red-300"
              : "border-amber-300"
          }`}
        >
          <CardHeader className="flex items-center gap-3">
            {decision.decision === "ACCEPT" ? (
              <CheckCircle2 className="w-6 h-6 text-emerald-600" />
            ) : decision.decision === "REJECT" ? (
              <XCircle className="w-6 h-6 text-red-600" />
            ) : (
              <AlertTriangle className="w-6 h-6 text-amber-600" />
            )}
            <div>
              <h2 className="text-lg font-bold">
                Decision: {decision.decision}
              </h2>
              {decision.confidence != null && (
                <p className="text-xs text-muted">
                  Confidence: {(decision.confidence * 100).toFixed(0)}%
                </p>
              )}
            </div>
          </CardHeader>
          <CardBody className="space-y-3">
            <div>
              <h3 className="text-sm font-semibold mb-1">AI Explanation</h3>
              <p className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                {decision.explanation}
              </p>
            </div>
            {decision.llm_reasoning &&
              decision.llm_reasoning !== decision.explanation && (
                <div>
                  <h3 className="text-sm font-semibold mb-1">
                    LLM Reasoning
                  </h3>
                  <p className="text-sm text-slate-600 whitespace-pre-wrap">
                    {decision.llm_reasoning}
                  </p>
                </div>
              )}
          </CardBody>
        </Card>
      )}

      <div className="grid grid-cols-2 gap-6">
        {/* Patient Info */}
        <Card>
          <CardHeader className="flex items-center gap-2">
            <User className="w-4 h-4 text-muted" />
            <h2 className="text-base font-semibold">Patient Information</h2>
          </CardHeader>
          <CardBody>
            <dl className="space-y-2 text-sm">
              <Row label="Name" value={referral.patient?.name} />
              <Row label="DOB" value={referral.patient?.date_of_birth} />
              <Row label="Gender" value={referral.patient?.gender} />
              <Row label="Source" value={referral.source_facility} />
            </dl>
          </CardBody>
        </Card>

        {/* Insurance */}
        <Card>
          <CardHeader className="flex items-center gap-2">
            <Shield className="w-4 h-4 text-muted" />
            <h2 className="text-base font-semibold">Insurance Status</h2>
          </CardHeader>
          <CardBody>
            {insurance ? (
              <dl className="space-y-2 text-sm">
                <Row
                  label="Has Insurance"
                  value={insurance.has_insurance ? "Yes" : "No"}
                />
                <Row label="Provider" value={insurance.provider} />
                <Row
                  label="In-Network"
                  value={insurance.in_network ? "Yes" : "No"}
                />
                <Row label="Coverage" value={insurance.coverage_level} />
                <Row label="Status" value={insurance.reason} />
              </dl>
            ) : (
              <p className="text-sm text-muted">No insurance data available</p>
            )}
          </CardBody>
        </Card>

        {/* Clinical Data */}
        <Card>
          <CardHeader className="flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-muted" />
            <h2 className="text-base font-semibold">
              Extracted Clinical Data
            </h2>
          </CardHeader>
          <CardBody>
            {clinical ? (
              <dl className="space-y-2 text-sm">
                <Row label="Diagnosis" value={clinical.diagnosis} />
                <Row label="Mobility" value={clinical.mobility} />
                <Row
                  label="Oxygen Required"
                  value={clinical.oxygen_required ? "Yes" : "No"}
                />
                <Row label="Cognitive Status" value={clinical.cognitive_status} />
                <Row label="Age" value={clinical.age?.toString()} />
                <div>
                  <dt className="text-muted">Comorbidities</dt>
                  <dd className="flex flex-wrap gap-1 mt-1">
                    {clinical.comorbidities?.length > 0
                      ? clinical.comorbidities.map((c, i) => (
                          <Badge key={i} variant="gray">
                            {c}
                          </Badge>
                        ))
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-muted">Key Risks</dt>
                  <dd className="flex flex-wrap gap-1 mt-1">
                    {clinical.key_risks?.length > 0
                      ? clinical.key_risks.map((r, i) => (
                          <Badge key={i} variant="red">
                            {r}
                          </Badge>
                        ))
                      : "—"}
                  </dd>
                </div>
                <div>
                  <dt className="text-muted">Medications</dt>
                  <dd className="flex flex-wrap gap-1 mt-1">
                    {clinical.medications?.length > 0
                      ? clinical.medications.map((m, i) => (
                          <Badge key={i} variant="blue">
                            {m}
                          </Badge>
                        ))
                      : "—"}
                  </dd>
                </div>
              </dl>
            ) : (
              <p className="text-sm text-muted">
                No clinical data extracted yet
              </p>
            )}
          </CardBody>
        </Card>

        {/* Rules Engine */}
        <Card>
          <CardHeader className="flex items-center gap-2">
            <Scale className="w-4 h-4 text-muted" />
            <h2 className="text-base font-semibold">Rules Engine Output</h2>
          </CardHeader>
          <CardBody>
            {rules ? (
              <div className="space-y-3 text-sm">
                <div className="flex items-center gap-4">
                  <span className="text-muted">Rules Evaluated:</span>
                  <span className="font-medium">{rules.total_rules}</span>
                  <span className="text-muted">Triggered:</span>
                  <span className="font-medium">{rules.triggered_count}</span>
                </div>
                {rules.override_decision && (
                  <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-lg text-xs">
                    Override Decision: {rules.override_decision}
                  </div>
                )}
                {rules.triggered_rules?.map((r, i) => (
                  <div
                    key={i}
                    className="bg-slate-50 rounded-lg px-3 py-2 text-xs"
                  >
                    <span className="font-mono font-medium">{r.rule}</span>
                    <span className="mx-2 text-muted">→</span>
                    <span>{r.message}</span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted">No rules output available</p>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Workflow Execution Viewer */}
      <Card>
        <CardHeader className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-muted" />
          <h2 className="text-base font-semibold">
            Workflow Execution Trace
          </h2>
        </CardHeader>
        <CardBody>
          {workflowLogs.length > 0 ? (
            <div className="space-y-2">
              {workflowLogs.map((log, i) => (
                <div
                  key={i}
                  className="border border-border rounded-lg overflow-hidden"
                >
                  <button
                    onClick={() =>
                      setExpandedStep(
                        expandedStep === log.step_name ? null : log.step_name
                      )
                    }
                    className="w-full flex items-center gap-3 px-4 py-3 hover:bg-slate-50 transition-colors text-left"
                  >
                    <span className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">
                      {i + 1}
                    </span>
                    {log.status === "completed" ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-500 shrink-0" />
                    )}
                    <span className="text-sm font-mono font-medium flex-1">
                      {log.step_name}
                    </span>
                    <StatusBadge status={log.status} />
                    {log.duration_ms != null && (
                      <span className="text-xs text-muted">
                        {log.duration_ms.toFixed(0)}ms
                      </span>
                    )}
                    {expandedStep === log.step_name ? (
                      <ChevronDown className="w-4 h-4 text-muted" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-muted" />
                    )}
                  </button>
                  {expandedStep === log.step_name && (
                    <div className="border-t border-border px-4 py-3 bg-slate-50 space-y-3 text-xs">
                      {log.input_summary && (
                        <div>
                          <p className="font-semibold text-muted mb-1">
                            Input
                          </p>
                          <pre className="bg-white p-2 rounded border border-border overflow-x-auto max-h-40 overflow-y-auto">
                            {log.input_summary}
                          </pre>
                        </div>
                      )}
                      {log.output_summary && (
                        <div>
                          <p className="font-semibold text-muted mb-1">
                            Output
                          </p>
                          <pre className="bg-white p-2 rounded border border-border overflow-x-auto max-h-40 overflow-y-auto">
                            {log.output_summary}
                          </pre>
                        </div>
                      )}
                      {log.error && (
                        <div>
                          <p className="font-semibold text-red-500 mb-1">
                            Error
                          </p>
                          <pre className="bg-red-50 p-2 rounded border border-red-200 text-red-700 overflow-x-auto">
                            {log.error}
                          </pre>
                        </div>
                      )}
                      {log.logged_at && (
                        <p className="text-muted">
                          Logged at:{" "}
                          {new Date(log.logged_at).toLocaleString()}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted">
              No workflow logs available
            </p>
          )}
        </CardBody>
      </Card>

      {/* LLM Outputs */}
      {llmOutputs.length > 0 && (
        <Card>
          <CardHeader className="flex items-center gap-2">
            <Brain className="w-4 h-4 text-muted" />
            <h2 className="text-base font-semibold">LLM Outputs</h2>
          </CardHeader>
          <CardBody className="space-y-4">
            {llmOutputs.map((output, i) => (
              <div
                key={i}
                className="border border-border rounded-lg p-4 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-mono font-medium">
                    {output.step}
                  </span>
                  <div className="flex items-center gap-3 text-xs text-muted">
                    <span>Model: {output.model}</span>
                    {output.usage && (
                      <span>{output.usage.total_tokens} tokens</span>
                    )}
                  </div>
                </div>
                <pre className="text-xs bg-slate-50 p-3 rounded border border-border overflow-x-auto max-h-48 overflow-y-auto">
                  {typeof output.parsed_response === "object"
                    ? JSON.stringify(output.parsed_response, null, 2)
                    : output.parsed_response}
                </pre>
              </div>
            ))}
          </CardBody>
        </Card>
      )}

      {/* Raw Referral Text */}
      <Card>
        <CardHeader>
          <h2 className="text-base font-semibold">Original Referral Text</h2>
        </CardHeader>
        <CardBody>
          <pre className="text-sm whitespace-pre-wrap text-slate-700 leading-relaxed">
            {referral.referral_text}
          </pre>
        </CardBody>
      </Card>
    </div>
  );
}

function Row({
  label,
  value,
}: {
  label: string;
  value: string | null | undefined;
}) {
  return (
    <div className="flex justify-between">
      <dt className="text-muted">{label}</dt>
      <dd className="font-medium">{value || "—"}</dd>
    </div>
  );
}
