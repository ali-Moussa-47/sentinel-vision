import { Car, ScanFace } from "lucide-react";
import type { SurveillanceEvent } from "../api/types";
import { relativeTime } from "../lib/format";

export function EventCard({ event }: { event: SurveillanceEvent }) {
  const watched = event.type === "plate_watched";
  const Icon = watched ? Car : ScanFace;
  const accent = watched ? "var(--color-alert)" : "var(--color-brand)";
  const tint = watched ? "rgba(239,83,80,0.12)" : "rgba(106,187,102,0.12)";
  return (
    <article className="overflow-hidden rounded-2xl border border-line bg-panel">
      <div className="flex aspect-video items-center justify-center bg-elevated">
        {event.imageUrl ? (
          <img src={event.imageUrl} alt={event.label} className="h-full w-full object-cover" />
        ) : (
          <Icon className="h-10 w-10 text-muted" />
        )}
      </div>
      <div className="space-y-2 p-4">
        <div className="flex items-center justify-between">
          <span
            className="rounded-full px-2.5 py-1 text-xs font-medium"
            style={{ color: accent, background: tint }}
          >
            {watched ? "PLAQUE SURVEILLÉE" : "CORRESPONDANCE"}
          </span>
          <span className="text-xs text-muted">{relativeTime(event.timestamp)}</span>
        </div>
        <h3 className="font-mono text-lg font-semibold tracking-wider">{event.label}</h3>
        <p className="text-sm text-muted">
          {event.camera} · similarité {event.confidence.toFixed(2)}
        </p>
      </div>
    </article>
  );
}
