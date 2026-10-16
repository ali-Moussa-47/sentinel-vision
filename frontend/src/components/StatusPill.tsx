import type { CameraState } from "../api/types";

const MAP: Record<CameraState, { color: string; label: string }> = {
  ACTIVE: { color: "var(--color-brand)", label: "En ligne" },
  DEGRADED: { color: "var(--color-warn)", label: "Dégradée" },
  OFFLINE: { color: "var(--color-alert)", label: "Hors ligne" },
};

export function StatusPill({ state }: { state: CameraState }) {
  const { color, label } = MAP[state];
  return (
    <span className="inline-flex items-center gap-2 text-sm text-muted">
      <span className="h-2.5 w-2.5 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}
