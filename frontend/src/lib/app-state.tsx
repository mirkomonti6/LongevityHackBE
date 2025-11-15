"use client";

import { createContext, useContext, useState, useEffect, useCallback } from "react";
import type { OnboardingData } from "./onboarding-schema";
import type { LeverResult, DailyEntry } from "./api-mock";
import type { BackendResponse } from "./api";
import {
  fetchPrimaryLever,
  saveDailyEntry,
  fetchDailyEntries,
  getTodayEntry,
} from "./api-mock";

interface AppState {
  onboardingData: OnboardingData | null;
  primaryLever: LeverResult | null;
  dailyEntries: DailyEntry[];
  todayEntry: DailyEntry | null;
  isLoading: boolean;
  backendResponse: BackendResponse | null;
}

interface AppStateContextValue extends AppState {
  setOnboardingData: (data: OnboardingData) => void;
  setPrimaryLever: (lever: LeverResult) => void;
  setBackendResponse: (response: BackendResponse) => void;
  updateTodayEntry: (entry: Partial<DailyEntry>) => Promise<void>;
  refreshEntries: () => Promise<void>;
}

const AppStateContext = createContext<AppStateContextValue | undefined>(
  undefined
);

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [onboardingData, setOnboardingDataState] = useState<OnboardingData | null>(null);
  const [primaryLever, setPrimaryLeverState] = useState<LeverResult | null>(null);
  const [dailyEntries, setDailyEntries] = useState<DailyEntry[]>([]);
  const [todayEntry, setTodayEntry] = useState<DailyEntry | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [backendResponse, setBackendResponseState] = useState<BackendResponse | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("longevity_app_onboarding_data");
    if (stored) {
      try {
        const data = JSON.parse(stored);
        setOnboardingDataState(data);
      } catch {
      }
    }

    const storedLever = localStorage.getItem("longevity_app_primary_lever");
    if (storedLever) {
      try {
        const lever = JSON.parse(storedLever);
        setPrimaryLeverState(lever);
      } catch {
      }
    }

    const storedBackendResponse = localStorage.getItem("longevity_app_backend_response");
    if (storedBackendResponse) {
      try {
        const response = JSON.parse(storedBackendResponse);
        setBackendResponseState(response);
      } catch {
      }
    }

    refreshEntries();
  }, []);

  const refreshEntries = useCallback(async () => {
    const entries = await fetchDailyEntries();
    setDailyEntries(entries);
    const today = await getTodayEntry();
    setTodayEntry(today);
  }, []);

  const setOnboardingData = useCallback((data: OnboardingData) => {
    setOnboardingDataState(data);
    localStorage.setItem("longevity_app_onboarding_data", JSON.stringify(data));
  }, []);

  const setPrimaryLever = useCallback((lever: LeverResult) => {
    setPrimaryLeverState(lever);
    localStorage.setItem("longevity_app_primary_lever", JSON.stringify(lever));
  }, []);

  const setBackendResponse = useCallback((response: BackendResponse) => {
    setBackendResponseState(response);
    localStorage.setItem("longevity_app_backend_response", JSON.stringify(response));
  }, []);

  const updateTodayEntry = useCallback(
    async (partial: Partial<DailyEntry>) => {
      const today = new Date().toISOString().split("T")[0];
      const current = todayEntry || {
        date: today,
        adherence: null,
        mood: null,
      };

      const updated: DailyEntry = {
        ...current,
        ...partial,
        date: today,
      };

      await saveDailyEntry(updated);
      await refreshEntries();
    },
    [todayEntry, refreshEntries]
  );

  return (
    <AppStateContext.Provider
      value={{
        onboardingData,
        primaryLever,
        dailyEntries,
        todayEntry,
        isLoading,
        backendResponse,
        setOnboardingData,
        setPrimaryLever,
        setBackendResponse,
        updateTodayEntry,
        refreshEntries,
      }}
    >
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error("useAppState must be used within AppStateProvider");
  }
  return context;
}

