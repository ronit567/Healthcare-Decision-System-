"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { fetchReferrals } from "@/lib/api";
import type { Referral } from "@/lib/types";
import { Card, CardHeader, CardBody } from "@/components/card";
import { DecisionBadge, RiskBadge, StatusBadge } from "@/components/badge";
import {
  Inbox,
  Clock,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  RefreshCw,
} from "lucide-react";

export default function Home() {
  const [referrals, setReferrals] = useState<Referral[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchReferrals();
      setReferrals(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const stats = {
    total: referrals.length,
    completed: referrals.filter((r) => r.status === "completed").length,
    processing: referrals.filter((r) => r.status === "processing").length,
    failed: referrals.filter((r) => r.status === "failed").length,
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Referral Inbox</h1>
          <p className="text-sm text-muted mt-1">
            AI-processed patient referrals with admission recommendations
          </p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-primary rounded-lg hover:bg-primary/90 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <CardBody className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-blue-50 flex items-center justify-center">
              <Inbox className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.total}</p>
              <p className="text-xs text-muted">Total Referrals</p>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
              <CheckCircle2 className="w-5 h-5 text-emerald-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.completed}</p>
              <p className="text-xs text-muted">Completed</p>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-amber-50 flex items-center justify-center">
              <Clock className="w-5 h-5 text-amber-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.processing}</p>
              <p className="text-xs text-muted">Processing</p>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-lg bg-red-50 flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-600" />
            </div>
            <div>
              <p className="text-2xl font-bold">{stats.failed}</p>
              <p className="text-xs text-muted">Failed</p>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Referrals Table */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold">All Referrals</h2>
        </CardHeader>
        {loading ? (
          <CardBody>
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 text-muted animate-spin" />
              <span className="ml-2 text-muted">Loading referrals...</span>
            </div>
          </CardBody>
        ) : error ? (
          <CardBody>
            <div className="flex flex-col items-center justify-center py-12 text-red-500">
              <AlertTriangle className="w-8 h-8 mb-2" />
              <p className="text-sm font-medium">Failed to load referrals</p>
              <p className="text-xs mt-1">{error}</p>
              <button
                onClick={load}
                className="mt-4 px-4 py-2 text-xs bg-red-50 text-red-600 rounded-lg hover:bg-red-100"
              >
                Retry
              </button>
            </div>
          </CardBody>
        ) : referrals.length === 0 ? (
          <CardBody>
            <div className="flex flex-col items-center justify-center py-12 text-muted">
              <Inbox className="w-10 h-10 mb-3" />
              <p className="font-medium">No referrals yet</p>
              <p className="text-sm mt-1">
                Submit a new referral to get started
              </p>
              <Link
                href="/new"
                className="mt-4 px-4 py-2 text-sm bg-primary text-white rounded-lg hover:bg-primary/90"
              >
                New Referral
              </Link>
            </div>
          </CardBody>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted">
                  <th className="px-6 py-3 font-medium">Patient</th>
                  <th className="px-6 py-3 font-medium">Source</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Risk</th>
                  <th className="px-6 py-3 font-medium">Decision</th>
                  <th className="px-6 py-3 font-medium">Date</th>
                </tr>
              </thead>
              <tbody>
                {referrals.map((r) => (
                  <tr
                    key={r.id}
                    className="border-b border-border last:border-0 hover:bg-slate-50 transition-colors"
                  >
                    <td className="px-6 py-4">
                      <Link
                        href={`/referral/${r.id}`}
                        className="font-medium text-primary hover:underline"
                      >
                        {r.patient?.name || "Unknown"}
                      </Link>
                      {r.patient?.gender && (
                        <p className="text-xs text-muted mt-0.5">
                          {r.patient.gender}
                          {r.patient.date_of_birth
                            ? ` · DOB: ${r.patient.date_of_birth}`
                            : ""}
                        </p>
                      )}
                    </td>
                    <td className="px-6 py-4 text-muted">
                      {r.source_facility || "—"}
                    </td>
                    <td className="px-6 py-4">
                      <StatusBadge status={r.status} />
                    </td>
                    <td className="px-6 py-4">
                      {r.decision?.risk_level ? (
                        <RiskBadge level={r.decision.risk_level} />
                      ) : (
                        <span className="text-muted">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      {r.decision?.decision ? (
                        <DecisionBadge decision={r.decision.decision} />
                      ) : (
                        <span className="text-muted">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-muted text-xs">
                      {r.created_at
                        ? new Date(r.created_at).toLocaleString()
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
}
