import type { HabitTemplate, DailyMetrics } from "./tracking-types";
import { generateMockMetrics } from "./tracking-mock";

export interface MetricsProvider {
  fetchMetricsForHabit(
    habit: HabitTemplate,
    startDate: string,
    endDate: string
  ): Promise<DailyMetrics[]>;
}

export class MockMetricsProvider implements MetricsProvider {
  async fetchMetricsForHabit(
    habit: HabitTemplate,
    startDate: string,
    endDate: string
  ): Promise<DailyMetrics[]> {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const days = Math.ceil((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24)) + 1;
    
    const allMetrics = generateMockMetrics(days, habit.domain === "movement" ? "movement" : habit.domain === "sleep" ? "sleep" : undefined);
    
    return allMetrics.filter(
      (m) => m.date >= startDate && m.date <= endDate
    );
  }
}

export class AppleHealthKitProvider implements MetricsProvider {
  async fetchMetricsForHabit(
    habit: HabitTemplate,
    startDate: string,
    endDate: string
  ): Promise<DailyMetrics[]> {
    throw new Error("Apple HealthKit integration not yet implemented");
  }
}

export class GoogleFitProvider implements MetricsProvider {
  async fetchMetricsForHabit(
    habit: HabitTemplate,
    startDate: string,
    endDate: string
  ): Promise<DailyMetrics[]> {
    throw new Error("Google Fit integration not yet implemented");
  }
}

let currentProvider: MetricsProvider = new MockMetricsProvider();

export function setMetricsProvider(provider: MetricsProvider): void {
  currentProvider = provider;
}

export function getMetricsProvider(): MetricsProvider {
  return currentProvider;
}

export async function fetchMetricsForHabit(
  habit: HabitTemplate,
  startDate: string,
  endDate: string
): Promise<DailyMetrics[]> {
  return currentProvider.fetchMetricsForHabit(habit, startDate, endDate);
}

