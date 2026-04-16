import { type ReactNode } from "react";

type Variant = "green" | "red" | "amber" | "blue" | "gray";

const VARIANT_CLASSES: Record<Variant, string> = {
  green: "bg-emerald-100 text-emerald-700",
  red: "bg-red-100 text-red-700",
  amber: "bg-amber-100 text-amber-700",
  blue: "bg-blue-100 text-blue-700",
  gray: "bg-slate-100 text-slate-600",
};

export function Badge({
  variant = "gray",
  children,
}: {
  variant?: Variant;
  children: ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${VARIANT_CLASSES[variant]}`}
    >
      {children}
    </span>
  );
}

export function DecisionBadge({ decision }: { decision: string }) {
  const map: Record<string, Variant> = {
    ACCEPT: "green",
    REJECT: "red",
    REVIEW: "amber",
  };
  return <Badge variant={map[decision] || "gray"}>{decision}</Badge>;
}

export function RiskBadge({ level }: { level: string }) {
  const map: Record<string, Variant> = {
    low: "green",
    medium: "amber",
    high: "red",
  };
  return <Badge variant={map[level] || "gray"}>{level?.toUpperCase()} RISK</Badge>;
}

export function StatusBadge({ status }: { status: string }) {
  const map: Record<string, Variant> = {
    completed: "green",
    processing: "blue",
    pending: "gray",
    failed: "red",
    running: "blue",
  };
  return <Badge variant={map[status] || "gray"}>{status}</Badge>;
}
