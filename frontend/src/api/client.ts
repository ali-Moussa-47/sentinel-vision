import * as mock from "./mock";
import type { CameraStatus, SurveillanceEvent, WatchedPlate } from "./types";

const BASE = import.meta.env.VITE_API_URL as string | undefined;

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
}

export const api = {
  usingMock: !BASE,

  events: (): Promise<SurveillanceEvent[]> =>
    BASE ? request("/api/events") : mock.getEvents(),

  cameras: (): Promise<CameraStatus[]> =>
    BASE ? request("/api/cameras") : mock.getCameras(),

  watchlist: (): Promise<WatchedPlate[]> =>
    BASE ? request("/api/plates") : mock.getWatchlist(),

  addPlate: (value: string): Promise<WatchedPlate[]> =>
    BASE
      ? request("/api/plates", { method: "POST", body: JSON.stringify({ value }) })
      : mock.addPlate(value),

  removePlate: (value: string): Promise<WatchedPlate[]> =>
    BASE
      ? request(`/api/plates/${encodeURIComponent(value)}`, { method: "DELETE" })
      : mock.removePlate(value),
};
