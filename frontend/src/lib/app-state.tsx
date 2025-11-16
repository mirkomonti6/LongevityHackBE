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
import type { HabitDayStatus, HabitTemplate, HabitPlan } from "./tracking-types";

interface AppState {
  onboardingData: OnboardingData | null;
  primaryLever: LeverResult | null;
  dailyEntries: DailyEntry[];
  todayEntry: DailyEntry | null;
  isLoading: boolean;
  backendResponse: BackendResponse | null;
  habitStatuses: HabitDayStatus[];
  habitTemplate: HabitTemplate | null;
  habitPlan: HabitPlan | null;
  habitPlanStartDate: string | null;
  resolvedHabitPlan: HabitPlan | null;
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
  const [habitPlan, setHabitPlanState] = useState<HabitPlan | null>(null);
  const [habitPlanStartDate, setHabitPlanStartDateState] = useState<string | null>(null);

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

    const storedHabitPlan = localStorage.getItem("longevity_app_habit_plan");
    if (storedHabitPlan) {
      try {
        const plan = JSON.parse(storedHabitPlan);
        setHabitPlanState(plan);
      } catch {
      }
    }

    const storedHabitPlanStartDate = localStorage.getItem("longevity_app_habit_plan_start_date");
    if (storedHabitPlanStartDate) {
      setHabitPlanStartDateState(storedHabitPlanStartDate);
    }
  }, []);

  // Resolve habit plan with concrete dates
  const resolvedHabitPlan = useMemo(() => {
    if (!habitPlan || !habitPlanStartDate) return null;
    
    const startDate = new Date(habitPlanStartDate);
    const resolvedDays = habitPlan.days.map((day) => {
      const dayDate = new Date(startDate);
      dayDate.setDate(startDate.getDate() + (day.dayIndex - 1));
      return {
        ...day,
        date: dayDate.toISOString().split("T")[0],
      };
    });

    return {
      ...habitPlan,
      days: resolvedDays,
    };
  }, [habitPlan, habitPlanStartDate]);

  const habitTemplate = useMemo(() => {
    if (!primaryLever) return null;
    return createHabitFromLever(primaryLever, backendResponse?.interventionName || null);
  }, [primaryLever, backendResponse]);

  const mockMetrics = useMemo(() => {
    if (!primaryLever) return [];
    
    // If we have a resolved plan, use its dates and generate metrics for exactly those days
    if (resolvedHabitPlan && resolvedHabitPlan.days.length > 0) {
      const planDates = resolvedHabitPlan.days.map((day) => day.date);
      return generateMockMetrics(resolvedHabitPlan.days.length, primaryLever.type, planDates);
    }
    
    return generateMockMetrics(14, primaryLever.type);
  }, [primaryLever, resolvedHabitPlan]);

  const habitStatuses = useMemo(() => {
    if (!habitTemplate || mockMetrics.length === 0) return [];
    return computeHabitStatuses(habitTemplate, mockMetrics, resolvedHabitPlan || undefined);
  }, [habitTemplate, mockMetrics, resolvedHabitPlan]);

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

    // Handle habit plan from response
    if (response.plan) {
      setHabitPlanState(response.plan);
      localStorage.setItem("longevity_app_habit_plan", JSON.stringify(response.plan));

      // Set start date if not already set (relative to today - choice 1b)
      const currentStartDate = localStorage.getItem("longevity_app_habit_plan_start_date");
      if (!currentStartDate) {
        const today = new Date().toISOString().split("T")[0];
        setHabitPlanStartDateState(today);
        localStorage.setItem("longevity_app_habit_plan_start_date", today);
      }
    }
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
        habitPlan,
        habitPlanStartDate,
        resolvedHabitPlan,
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

