import { useQuery } from "@tanstack/react-query";
import { api } from "../api/client";
import { StatusPill } from "../components/StatusPill";

export function StatusPage() {
  const { data } = useQuery({ queryKey: ["cameras"], queryFn: api.cameras });
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 xl:grid-cols-3">
      {data?.map((camera) => (
        <div key={camera.name} className="rounded-2xl border border-line bg-panel p-5">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold tracking-tight">{camera.name}</h3>
            <StatusPill state={camera.state} />
          </div>
          <p className="mt-3 text-sm text-muted">{camera.fps.toFixed(1)} FPS</p>
        </div>
      ))}
    </div>
  );
}
