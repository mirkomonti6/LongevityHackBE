import type { OnboardingData } from "./onboarding-schema";

export interface BackendResponse {
  interventionName: string | null;
  responseText: string;
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

export interface ApiResponse {
  output: {
    response: string;
    intervention_name: string | null;
  };
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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

    return {
      interventionName: data.output.intervention_name || null,
      responseText: data.output.response || "",
    };
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("fetch")) {
      throw new Error(
        "Failed to connect to backend. Make sure the server is running on http://localhost:8000"
      );
    }
    throw error;
  }
}

