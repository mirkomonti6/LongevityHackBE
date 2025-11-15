import type { OnboardingData } from "./onboarding-schema";

export type LeverType = "sleep" | "movement" | "metabolic" | "stress";

export interface LeverResult {
  type: LeverType;
  name: string;
  description: string;
  impactScore: number;
}

export type Adherence = "yes" | "no";
export type Mood = "sad" | "ok" | "good" | "great";

export interface DailyEntry {
  date: string;
  adherence: Adherence | null;
  mood: Mood | null;
}

const STORAGE_KEY_DAILY_ENTRIES = "longevity_app_daily_entries";
const STORAGE_KEY_PRIMARY_LEVER = "longevity_app_primary_lever";

function getSleepLever(data: OnboardingData): LeverResult {
  return {
    type: "sleep",
    name: "Sleep & Recovery",
    description:
      "Getting at least 7 hours of consistent sleep per night is likely your biggest lever for better energy and long-term health right now.",
    impactScore: 28,
  };
}

function getMovementLever(data: OnboardingData): LeverResult {
  return {
    type: "movement",
    name: "Daily Movement",
    description:
      "Regular movement throughout the week is essential for maintaining metabolic health and longevity. Aim for at least 20-30 minutes of activity most days.",
    impactScore: 24,
  };
}

function getMetabolicLever(data: OnboardingData): LeverResult {
  return {
    type: "metabolic",
    name: "Metabolic Health",
    description:
      "Optimizing your metabolic markers through nutrition and lifestyle changes can significantly impact your long-term health and energy levels.",
    impactScore: 31,
  };
}

function getStressLever(data: OnboardingData): LeverResult {
  return {
    type: "stress",
    name: "Stress Management",
    description:
      "Managing daily stress levels is crucial for maintaining hormonal balance and overall well-being. Finding effective stress reduction techniques can be transformative.",
    impactScore: 22,
  };
}

export async function fetchPrimaryLever(
  onboardingData: OnboardingData
): Promise<LeverResult> {
  await new Promise((resolve) => setTimeout(resolve, 1200));

  const stored = localStorage.getItem(STORAGE_KEY_PRIMARY_LEVER);
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch {
    }
  }

  let lever: LeverResult;

  if (onboardingData.sleepHours !== null && onboardingData.sleepHours < 7) {
    lever = getSleepLever(onboardingData);
  } else if (
    onboardingData.movementDays !== null &&
    onboardingData.movementDays < 4
  ) {
    lever = getMovementLever(onboardingData);
  } else if (
    onboardingData.stressLevel !== null &&
    onboardingData.stressLevel >= 7
  ) {
    lever = getStressLever(onboardingData);
  } else {
    lever = getMetabolicLever(onboardingData);
  }

  localStorage.setItem(STORAGE_KEY_PRIMARY_LEVER, JSON.stringify(lever));
  return lever;
}

export async function saveDailyEntry(entry: DailyEntry): Promise<void> {
  const entries = await fetchDailyEntries();
  const existingIndex = entries.findIndex((e) => e.date === entry.date);

  if (existingIndex >= 0) {
    entries[existingIndex] = entry;
  } else {
    entries.push(entry);
  }

  entries.sort((a, b) => b.date.localeCompare(a.date));
  localStorage.setItem(STORAGE_KEY_DAILY_ENTRIES, JSON.stringify(entries));
}

export async function fetchDailyEntries(): Promise<DailyEntry[]> {
  const stored = localStorage.getItem(STORAGE_KEY_DAILY_ENTRIES);
  if (!stored) {
    return [];
  }

  try {
    return JSON.parse(stored);
  } catch {
    return [];
  }
}

export async function getTodayEntry(): Promise<DailyEntry | null> {
  const today = new Date().toISOString().split("T")[0];
  const entries = await fetchDailyEntries();
  return entries.find((e) => e.date === today) || null;
}

