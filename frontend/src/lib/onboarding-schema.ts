export type GoalOption =
  | "more-energy"
  | "longevity"
  | "better-sleep"
  | "less-stress"
  | "weight-metabolic";

export type Sex = "male" | "female" | "other" | "prefer-not-to-say";

export type MedicalCondition =
  | "diabetes"
  | "heart-disease"
  | "hypertension"
  | "none";

export type WorkActivityLevel = "sedentary" | "light" | "moderate" | "active";

export interface OnboardingData {
  age: number | null;
  sex: Sex | null;
  height: number | null;
  weight: number | null;
  sleepHours: number | null;
  movementDays: number | null;
  workActivityLevel: WorkActivityLevel | null;
  labPdfFile: File | null;
  stressLevel: number | null;
  hba1c: number | null;
  ldl: number | null;
  hdl: number | null;
  triglycerides: number | null;
  crp: number | null;
  restingHeartRate: number | null;
}

export interface StepConfig {
  id: string;
  title: string;
  description: string;
  fields: string[];
}

export const ONBOARDING_STEPS: StepConfig[] = [
  {
    id: "age",
    title: "How old are you?",
    description: "",
    fields: ["age"],
  },
  {
    id: "sex",
    title: "What's your sex?",
    description: "This helps us personalize recommendations",
    fields: ["sex"],
  },
  {
    id: "height",
    title: "What's your height?",
    description: "",
    fields: ["height"],
  },
  {
    id: "weight",
    title: "What's your weight?",
    description: "",
    fields: ["weight"],
  },
  {
    id: "sleep-hours",
    title: "How many hours do you sleep?",
    description: "On average per night",
    fields: ["sleepHours"],
  },
  {
    id: "movement-days",
    title: "How many days do you move?",
    description: "At least 20-30 minutes per week",
    fields: ["movementDays"],
  },
  {
    id: "work-activity",
    title: "What's your work activity level?",
    description: "Tell us about your daily work",
    fields: ["workActivityLevel"],
  },
  {
    id: "lab-upload",
    title: "Upload your lab report",
    description: "Optional - helps us give better recommendations",
    fields: ["labPdfFile"],
  },
  {
    id: "stress",
    title: "How stressed do you feel?",
    description: "On a scale from 1 to 10",
    fields: ["stressLevel"],
  },
];

export const INITIAL_ONBOARDING_DATA: OnboardingData = {
  age: null,
  sex: null,
  height: null,
  weight: null,
  sleepHours: null,
  movementDays: null,
  workActivityLevel: null,
  labPdfFile: null,
  stressLevel: null,
  hba1c: null,
  ldl: null,
  hdl: null,
  triglycerides: null,
  crp: null,
  restingHeartRate: null,
};

