export type TrackingMode = "passive" | "hybrid" | "manual";
export type SignalSource = "steps" | "sleep" | "weight" | "strength_workouts" | "hrv" | "cgm" | "food_log";
export type HabitStatus = "yes" | "partly" | "no";

export type HabitDomain = "movement" | "sleep" | "metabolic" | "stress" | "nutrition" | "supplements";

export interface HabitRule {
  timeWindow?: [string, string];
  minSteps?: number;
  minSleepMinutes?: number;
  minStrengthWorkoutsPerWeek?: number;
  maxWeight?: number;
  minWeight?: number;
  targetTimeInRange?: number;
  targetCalories?: number;
  maxCalories?: number;
  weightLossPerWeekKg?: number;
  maxStressLevel?: number;
  [key: string]: any;
}

export interface HabitTemplate {
  id: string;
  domain: HabitDomain;
  label: string;
  trackingMode: TrackingMode;
  signalSource: SignalSource;
  rule: HabitRule;
}

export interface DailyMetrics {
  date: string;
  steps?: number;
  sleepMinutes?: number;
  strengthWorkouts?: number;
  weight?: number;
  hrv?: number;
  cgmTimeInRange?: number;
  lastMealTime?: string;
  calories?: number;
  stressLevel?: number;
  [key: string]: any;
}

export interface HabitDayStatus {
  date: string;
  status: HabitStatus;
  score?: number;
  reason?: string;
  metrics?: Partial<DailyMetrics>;
}

