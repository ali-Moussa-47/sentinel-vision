export type EventType = "plate_watched" | "face_match";

export interface SurveillanceEvent {
  id: string;
  timestamp: string;
  type: EventType;
  label: string;
  confidence: number;
  camera: string;
  imageUrl?: string;
}

export type CameraState = "ACTIVE" | "DEGRADED" | "OFFLINE";

export interface CameraStatus {
  name: string;
  state: CameraState;
  fps: number;
  lastEventAt?: string;
}

export interface WatchedPlate {
  value: string;
}
