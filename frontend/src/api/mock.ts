import type { CameraStatus, SurveillanceEvent, WatchedPlate } from "./types";

const delay = <T>(value: T): Promise<T> =>
  new Promise((resolve) => setTimeout(() => resolve(value), 220));

const minutesAgo = (minutes: number): string =>
  new Date(Date.now() - minutes * 60_000).toISOString();

const events: SurveillanceEvent[] = [
  { id: "e1", timestamp: minutesAgo(3), type: "plate_watched", label: "18C1250H", confidence: 0.99, camera: "portail-entree" },
  { id: "e2", timestamp: minutesAgo(21), type: "face_match", label: "Moussa", confidence: 0.72, camera: "portail-entree" },
  { id: "e3", timestamp: minutesAgo(94), type: "plate_watched", label: "7777TD", confidence: 0.93, camera: "cour-arriere" },
];

let plates: WatchedPlate[] = [{ value: "18C1250H" }, { value: "7777TD" }];

const cameras: CameraStatus[] = [
  { name: "portail-entree", state: "ACTIVE", fps: 11.4, lastEventAt: minutesAgo(3) },
  { name: "cour-arriere", state: "DEGRADED", fps: 4.1 },
  { name: "entrepot", state: "OFFLINE", fps: 0 },
];

export const getEvents = (): Promise<SurveillanceEvent[]> => delay([...events]);
export const getCameras = (): Promise<CameraStatus[]> => delay([...cameras]);
export const getWatchlist = (): Promise<WatchedPlate[]> => delay([...plates]);

export const addPlate = (value: string): Promise<WatchedPlate[]> => {
  const normalized = value.toUpperCase().replace(/[^A-Z0-9]/g, "");
  if (normalized && !plates.some((plate) => plate.value === normalized)) {
    plates = [{ value: normalized }, ...plates];
  }
  return delay([...plates]);
};

export const removePlate = (value: string): Promise<WatchedPlate[]> => {
  plates = plates.filter((plate) => plate.value !== value);
  return delay([...plates]);
};
