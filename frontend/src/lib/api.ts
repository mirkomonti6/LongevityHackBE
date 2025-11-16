import type { OnboardingData } from "./onboarding-schema";
import type { HabitPlan } from "./tracking-types";

export interface BackendResponse {
  interventionName: string | null;
  responseText: string;
  plan?: HabitPlan;
}

export interface ApiInput {
  age?: number;
  sex?: "male" | "female" | "other";
  height_cm?: number;
  weight_kg?: number;
  sleep_hours_per_night?: number;
  movement_days_per_week?: number;
  work_activity_level?: string;
  stress_level_1_to_10?: number;
  lab_pdf?: {
    filename: string;
    mime_type: string;
    base64: string;
  };
  userInput?: string;
  pastMessages?: Array<{ role: string; content: string }>;
  bloodData?: Record<string, number>;
  userProfile?: Record<string, any>;
}

export interface DailyTask {
  activity: string;
  steps: number;
}

export interface Challenge {
  intervention_name: string;
  duration_days: number;
  daily_tasks: DailyTask[];
  success_criteria?: string;
  category?: string;
}

export interface ApiResponse {
  output: {
    response: string;
    intervention_name: string | null;
    challenge?: Challenge;
  };
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://52.14.71.203:8000";

export async function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      const base64 = result.split(",")[1];
      if (!base64) {
        reject(new Error("Failed to extract base64 from file"));
        return;
      }
      resolve(base64);
    };
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.readAsDataURL(file);
  });
}

export function buildBackendPayload(
  onboardingData: OnboardingData,
  labFileBase64: string | null,
  labFileName: string | null,
  labFileType?: string
): ApiInput {
  const input: ApiInput = {};

  if (onboardingData.age !== null) {
    input.age = onboardingData.age;
  }

  if (onboardingData.sex !== null) {
    const sexMap: Record<string, "male" | "female" | "other"> = {
      male: "male",
      female: "female",
      other: "other",
      "prefer-not-to-say": "other",
    };
    input.sex = sexMap[onboardingData.sex] || "other";
  }

  if (onboardingData.height !== null) {
    input.height_cm = onboardingData.height;
  }

  if (onboardingData.weight !== null) {
    input.weight_kg = onboardingData.weight;
  }

  if (onboardingData.sleepHours !== null) {
    input.sleep_hours_per_night = onboardingData.sleepHours;
  }

  if (onboardingData.movementDays !== null) {
    input.movement_days_per_week = onboardingData.movementDays;
  }

  if (onboardingData.workActivityLevel !== null) {
    input.work_activity_level = onboardingData.workActivityLevel;
  }

  if (onboardingData.stressLevel !== null) {
    input.stress_level_1_to_10 = onboardingData.stressLevel;
  }

  if (labFileBase64 && labFileName) {
    const mimeType = labFileType || (labFileName.endsWith(".png") ? "image/png" : "application/pdf");
    input.lab_pdf = {
      filename: labFileName,
      mime_type: mimeType,
      base64: labFileBase64,
    };
  }

  input.userInput = "Please analyze my health data and provide personalized recommendations.";

  input.pastMessages = [];

  const bloodData: Record<string, number> = {};
  if (onboardingData.hba1c !== null) bloodData.hba1c = onboardingData.hba1c;
  if (onboardingData.ldl !== null) bloodData.ldl = onboardingData.ldl;
  if (onboardingData.hdl !== null) bloodData.hdl = onboardingData.hdl;
  if (onboardingData.triglycerides !== null)
    bloodData.triglycerides = onboardingData.triglycerides;
  if (onboardingData.crp !== null) bloodData.crp = onboardingData.crp;

  if (Object.keys(bloodData).length > 0) {
    input.bloodData = bloodData;
  }

  return input;
}

export async function executeBiohackerAgent(
  payload: ApiInput
): Promise<BackendResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/execute`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      if (response.status === 503) {
        throw new Error(
          "Backend is still initializing. Please wait a moment and try again."
        );
      }
      const errorText = await response.text();
      throw new Error(
        `Backend error (${response.status}): ${errorText || "Unknown error"}`
      );
    }

    const data: ApiResponse = await response.json();

    // Map challenge to HabitPlan if present, otherwise create fallback plan
    let plan: HabitPlan | undefined;
    if (data.output.challenge && data.output.challenge.daily_tasks && data.output.challenge.daily_tasks.length > 0) {
      plan = {
        interventionName: data.output.challenge.intervention_name,
        durationDays: data.output.challenge.duration_days,
        days: data.output.challenge.daily_tasks.map((task, idx) => ({
          dayIndex: idx + 1,
          date: "", // Will be resolved in app-state with start date
          activity: task.activity,
          targetSteps: task.steps,
        })),
        successCriteria: data.output.challenge.success_criteria,
        category: data.output.challenge.category,
      };
    } else {
      // Fallback plan: 10-day walking habit with increasing step goals
      const fallbackSteps = [8000, 8500, 9000, 9000, 9500, 10000, 10000, 10500, 11000, 12000];
      plan = {
        interventionName: data.output.intervention_name || "Daily Walking Habit",
        durationDays: 10,
        days: fallbackSteps.map((steps, idx) => ({
          dayIndex: idx + 1,
          date: "", // Will be resolved in app-state with start date
          activity: `Day ${idx + 1}: Walk ${steps.toLocaleString()} steps today`,
          targetSteps: steps,
        })),
        successCriteria: "Build sustainable walking habits and improve daily movement",
        category: "exercise",
      };
    }

    return {
      interventionName: data.output.intervention_name || plan?.interventionName || null,
      responseText: data.output.response || "",
      plan,
    };
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error(
        `Failed to connect to backend at ${API_BASE_URL}. Please check your connection.`
      );
    }
    throw error;
  }
}

