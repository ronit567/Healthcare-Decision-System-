"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Inbox,
  PlusCircle,
  Activity,
  FileText,
  Heart,
} from "lucide-react";

const NAV_ITEMS = [
  { href: "/", label: "Referral Inbox", icon: Inbox },
  { href: "/new", label: "New Referral", icon: PlusCircle },
  { href: "/logs", label: "Observability Logs", icon: Activity },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 w-64 bg-sidebar text-sidebar-foreground flex flex-col z-30">
      {/* Brand */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center">
            <Heart className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-bold leading-tight">AI Referral</h1>
            <p className="text-xs text-white/50">Intake &amp; Decision System</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/"
              ? pathname === "/"
              : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                active
                  ? "bg-white/10 text-white font-medium"
                  : "text-white/60 hover:text-white hover:bg-white/5"
              }`}
            >
              <item.icon className="w-4 h-4 shrink-0" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-2 px-3">
          <FileText className="w-4 h-4 text-white/40" />
          <span className="text-xs text-white/40">v1.0.0 — ExaCare-style</span>
        </div>
      </div>
    </aside>
  );
}
