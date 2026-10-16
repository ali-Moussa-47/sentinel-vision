import { Activity, LayoutGrid, ListChecks } from "lucide-react";
import type { ComponentType, ReactNode } from "react";

export type Tab = "events" | "watchlist" | "status";

const NAV: { id: Tab; label: string; icon: ComponentType<{ className?: string }> }[] = [
  { id: "events", label: "Événements", icon: LayoutGrid },
  { id: "watchlist", label: "Surveillance", icon: ListChecks },
  { id: "status", label: "Caméras", icon: Activity },
];

export function Layout({
  tab,
  onTab,
  header,
  children,
}: {
  tab: Tab;
  onTab: (tab: Tab) => void;
  header: ReactNode;
  children: ReactNode;
}) {
  return (
    <div className="flex h-full">
      <aside className="flex w-60 flex-col border-r border-line bg-panel p-4">
        <div className="mb-8 flex items-center gap-2 px-2 py-1">
          <span className="h-3 w-3 rounded-full bg-brand" />
          <span className="font-semibold tracking-tight">Sentinel Vision</span>
        </div>
        <nav className="space-y-1">
          {NAV.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              type="button"
              onClick={() => onTab(id)}
              className={`flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm transition ${
                tab === id ? "bg-elevated text-ink" : "text-muted hover:text-ink"
              }`}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <header className="flex items-center justify-between border-b border-line px-8 py-5">
          {header}
        </header>
        <div className="p-8">{children}</div>
      </main>
    </div>
  );
}
