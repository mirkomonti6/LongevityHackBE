"use client";

import { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react";
import type { OnboardingData } from "./onboarding-schema";
import type { LeverResult, DailyEntry } from "./api-mock";
import type { BackendResponse } from "./api";
import {
  fetchPrimaryLever,
  saveDailyEntry,
  fetchDailyEntries,
  getTodayEntry,
} from "./api-mock";
import {
  generateMockMetrics,
  computeHabitStatuses,
  createHabitFromLever,
  getTodayStatus,
} from "./tracking-mock";
import type { HabitDayStatus, HabitTemplate } from "./tracking-types";

interface AppState {
  onboardingData: OnboardingData | null;
  primaryLever: LeverResult | null;
  dailyEntries: DailyEntry[];
  todayEntry: DailyEntry | null;
  isLoading: boolean;
  backendResponse: BackendResponse | null;
  habitStatuses: HabitDayStatus[];
  habitTemplate: HabitTemplate | null;
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
  }, []);

  const habitTemplate = useMemo(() => {
    if (!primaryLever) return null;
    return createHabitFromLever(primaryLever, backendResponse?.interventionName || null);
  }, [primaryLever, backendResponse]);

  const mockMetrics = useMemo(() => {
    if (!primaryLever) return [];
    return generateMockMetrics(14, primaryLever.type);
  }, [primaryLever]);

  const habitStatuses = useMemo(() => {
    if (!habitTemplate || mockMetrics.length === 0) return [];
    return computeHabitStatuses(habitTemplate, mockMetrics);
  }, [habitTemplate, mockMetrics]);

  const refreshEntries = useCallback(async () => {
    if (!habitTemplate || habitStatuses.length === 0) {
      const entries = await fetchDailyEntries();
      setDailyEntries(entries);
      const today = await getTodayEntry();
      setTodayEntry(today);
      return;
    }

    const todayStatus = getTodayStatus(habitStatuses);
    const today = new Date().toISOString().split("T")[0];

    const manualEntries = await fetchDailyEntries();
    const manualTodayEntry = manualEntries.find((e) => e.date === today);

    const autoEntries: DailyEntry[] = habitStatuses.map((status) => {
      const manualEntry = manualEntries.find((e) => e.date === status.date);
      const adherence = manualEntry?.adherence || (status.status === "yes" ? "yes" : status.status === "partly" ? "yes" : "no");
      
      return {
        date: status.date,
        adherence: adherence as "yes" | "no" | null,
        mood: manualEntry?.mood || null,
      };
    });

    setDailyEntries(autoEntries);

    const todayEntryData: DailyEntry = {
      date: today,
      adherence: manualTodayEntry?.adherence || (todayStatus?.status === "yes" ? "yes" : todayStatus?.status === "partly" ? "yes" : "no"),
      mood: manualTodayEntry?.mood || null,
    };

    setTodayEntry(todayEntryData);
  }, [habitTemplate, habitStatuses]);

  useEffect(() => {
    refreshEntries();
  }, [refreshEntries]);

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
        habitStatuses,
        habitTemplate,
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

