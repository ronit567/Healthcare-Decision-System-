"use client";

import { useEffect, useState } from "react";
import { fetchAllLogs } from "@/lib/api";
import { Card, CardHeader, CardBody } from "@/components/card";
import { StatusBadge } from "@/components/badge";
import { Activity, RefreshCw, Search } from "lucide-react";

export default function LogsPage() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");

  const load = async () => {
    setLoading(true);
    try {
      const data = await fetchAllLogs();
      setLogs(data.logs || []);
    } catch {
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = filter
    ? logs.filter(
        (l) =>
          l.step_name?.toLowerCase().includes(filter.toLowerCase()) ||
          l.status?.toLowerCase().includes(filter.toLowerCase()) ||
          l.workflow_id?.toLowerCase().includes(filter.toLowerCase())
      )
    : logs;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Observability Logs</h1>
          <p className="text-sm text-muted mt-1">
            Step-by-step execution logs, LLM prompts, and pipeline traces
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

      <Card>
        <CardHeader className="flex items-center gap-3">
          <Activity className="w-4 h-4 text-muted" />
          <h2 className="text-base font-semibold flex-1">
            Execution Logs ({filtered.length})
          </h2>
          <div className="relative">
            <Search className="w-4 h-4 text-muted absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Filter logs..."
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="pl-9 pr-3 py-1.5 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
            />
          </div>
        </CardHeader>
        {loading ? (
          <CardBody>
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="w-6 h-6 text-muted animate-spin" />
              <span className="ml-2 text-muted">Loading logs...</span>
            </div>
          </CardBody>
        ) : filtered.length === 0 ? (
          <CardBody>
            <p className="text-center py-12 text-muted">No logs found</p>
          </CardBody>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-muted">
                  <th className="px-6 py-3 font-medium">Workflow ID</th>
                  <th className="px-6 py-3 font-medium">Step</th>
                  <th className="px-6 py-3 font-medium">Status</th>
                  <th className="px-6 py-3 font-medium">Duration</th>
                  <th className="px-6 py-3 font-medium">Timestamp</th>
                  <th className="px-6 py-3 font-medium">Error</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((log, i) => (
                  <tr
                    key={i}
                    className="border-b border-border last:border-0 hover:bg-slate-50"
                  >
                    <td className="px-6 py-3 font-mono text-xs text-muted">
                      {log.workflow_id?.slice(0, 8)}...
                    </td>
                    <td className="px-6 py-3 font-mono text-xs font-medium">
                      {log.step_name}
                    </td>
                    <td className="px-6 py-3">
                      <StatusBadge status={log.status} />
                    </td>
                    <td className="px-6 py-3 text-xs text-muted">
                      {log.duration_ms != null
                        ? `${log.duration_ms.toFixed(0)}ms`
                        : "—"}
                    </td>
                    <td className="px-6 py-3 text-xs text-muted">
                      {log.logged_at
                        ? new Date(log.logged_at).toLocaleString()
                        : "—"}
                    </td>
                    <td className="px-6 py-3 text-xs text-red-500 max-w-xs truncate">
                      {log.error || "—"}
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
