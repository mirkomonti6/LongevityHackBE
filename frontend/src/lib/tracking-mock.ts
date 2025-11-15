import type {
  HabitTemplate,
  DailyMetrics,
  HabitDayStatus,
  HabitStatus,
} from "./tracking-types";
import type { LeverResult, LeverType } from "./api-mock";

function generateMockSteps(date: Date, targetSteps: number = 7000): number {
  const dayOfWeek = date.getDay();
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
  const baseSteps = isWeekend ? targetSteps * 0.7 : targetSteps;
  const variance = baseSteps * 0.3;
  const randomFactor = (Math.random() - 0.5) * 2;
  return Math.max(0, Math.round(baseSteps + variance * randomFactor));
}

function generateMockSleep(date: Date, targetHours: number = 7): number {
  const baseMinutes = targetHours * 60;
  const variance = 60;
  const randomFactor = (Math.random() - 0.5) * 2;
  return Math.max(300, Math.round(baseMinutes + variance * randomFactor));
}

function generateMockStrengthWorkouts(date: Date): number {
  const dayOfWeek = date.getDay();
  if (dayOfWeek === 1 || dayOfWeek === 3 || dayOfWeek === 5) {
    return Math.random() > 0.3 ? 1 : 0;
  }
  return 0;
}

function generateMockWeight(date: Date, baseWeight: number = 75): number {
  const variance = 0.5;
  const randomFactor = (Math.random() - 0.5) * 2;
  return Math.round((baseWeight + variance * randomFactor) * 10) / 10;
}

function generateMockCalories(date: Date, targetCalories: number = 2000): number {
  const dayOfWeek = date.getDay();
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
  const baseCalories = isWeekend ? targetCalories * 1.1 : targetCalories;
  const variance = baseCalories * 0.15;
  const randomFactor = (Math.random() - 0.5) * 2;
  return Math.max(1200, Math.round(baseCalories + variance * randomFactor));
}

function generateMockStressLevel(date: Date): number {
  const dayOfWeek = date.getDay();
  const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
  const baseLevel = isWeekend ? 4 : 6;
  const variance = 2;
  const randomFactor = (Math.random() - 0.5) * 2;
  return Math.max(1, Math.min(10, Math.round(baseLevel + variance * randomFactor)));
}

export function generateMockMetrics(
  days: number = 14,
  leverType?: LeverType
): DailyMetrics[] {
  const metrics: DailyMetrics[] = [];
  const today = new Date();
  let baseWeight = 75;

  for (let i = 0; i < days; i++) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toISOString().split("T")[0];

    const dayMetrics: DailyMetrics = {
      date: dateStr,
    };

    if (leverType === "movement") {
      dayMetrics.steps = generateMockSteps(date, 7000);
      dayMetrics.strengthWorkouts = generateMockStrengthWorkouts(date);
    } else if (leverType === "sleep") {
      dayMetrics.sleepMinutes = generateMockSleep(date, 7);
    } else if (leverType === "metabolic") {
      dayMetrics.steps = generateMockSteps(date, 7000);
      dayMetrics.weight = generateMockWeight(date, baseWeight);
      baseWeight = dayMetrics.weight;
      dayMetrics.calories = generateMockCalories(date, 2000);
    } else if (leverType === "stress") {
      dayMetrics.steps = generateMockSteps(date, 5000);
      dayMetrics.stressLevel = generateMockStressLevel(date);
      dayMetrics.weight = generateMockWeight(date, baseWeight);
      baseWeight = dayMetrics.weight;
    } else {
      dayMetrics.steps = generateMockSteps(date, 7000);
      dayMetrics.sleepMinutes = generateMockSleep(date, 7);
      dayMetrics.weight = generateMockWeight(date, baseWeight);
      baseWeight = dayMetrics.weight;
      dayMetrics.calories = generateMockCalories(date, 2000);
      dayMetrics.stressLevel = generateMockStressLevel(date);
      dayMetrics.strengthWorkouts = generateMockStrengthWorkouts(date);
    }

    metrics.push(dayMetrics);
  }

  return metrics.reverse();
}

function computeStepsHabitStatus(
  metrics: DailyMetrics,
  rule: HabitTemplate["rule"]
): HabitStatus {
  const steps = metrics.steps || 0;
  const minSteps = rule.minSteps || 7000;

  if (steps >= minSteps) {
    return "yes";
  } else if (steps >= minSteps * 0.7) {
    return "partly";
  }
  return "no";
}

function computeSleepHabitStatus(
  metrics: DailyMetrics,
  rule: HabitTemplate["rule"]
): HabitStatus {
  const sleepMinutes = metrics.sleepMinutes || 0;
  const minSleepMinutes = rule.minSleepMinutes || 420;

  if (sleepMinutes >= minSleepMinutes) {
    return "yes";
  } else if (sleepMinutes >= minSleepMinutes * 0.85) {
    return "partly";
  }
  return "no";
}

function computeStrengthWorkoutsHabitStatus(
  metrics: DailyMetrics,
  rule: HabitTemplate["rule"],
  weekMetrics: DailyMetrics[]
): HabitStatus {
  const minPerWeek = rule.minStrengthWorkoutsPerWeek || 3;
  const weekWorkouts = weekMetrics.reduce(
    (sum, m) => sum + (m.strengthWorkouts || 0),
    0
  );

  if (weekWorkouts >= minPerWeek) {
    return "yes";
  } else if (weekWorkouts >= minPerWeek * 0.6) {
    return "partly";
  }
  return "no";
}

function computeWeightHabitStatus(
  metrics: DailyMetrics,
  rule: HabitTemplate["rule"],
  weekMetrics: DailyMetrics[]
): HabitStatus {
  const weightLossPerWeek = rule.weightLossPerWeekKg || 0.5;
  const weights = weekMetrics
    .filter((m) => m.weight !== undefined)
    .map((m) => m.weight!)
    .sort((a, b) => a - b);

  if (weights.length < 3) {
    return "partly";
  }

  const startWeight = weights[0];
  const endWeight = weights[weights.length - 1];
  const actualLoss = startWeight - endWeight;
  const targetLoss = weightLossPerWeek;

  if (actualLoss >= targetLoss * 0.8) {
    return "yes";
  } else if (actualLoss >= targetLoss * 0.5) {
    return "partly";
  }
  return "no";
}

function computeCaloriesHabitStatus(
  metrics: DailyMetrics,
  rule: HabitTemplate["rule"]
): HabitStatus {
  const calories = metrics.calories || 0;
  const targetCalories = rule.targetCalories || 2000;
  const maxCalories = rule.maxCalories || targetCalories * 1.1;

  if (calories >= targetCalories * 0.9 && calories <= maxCalories) {
    return "yes";
  } else if (calories >= targetCalories * 0.8 && calories <= maxCalories * 1.1) {
    return "partly";
  }
  return "no";
}

function computeStressHabitStatus(
  metrics: DailyMetrics,
  rule: HabitTemplate["rule"],
  weekMetrics: DailyMetrics[]
): HabitStatus {
  const maxStress = rule.maxStressLevel || 6;
  const stressLevels = weekMetrics
    .filter((m) => m.stressLevel !== undefined)
    .map((m) => m.stressLevel!);

  if (stressLevels.length === 0) {
    return "partly";
  }

  const avgStress = stressLevels.reduce((sum, s) => sum + s, 0) / stressLevels.length;
  const daysOverLimit = stressLevels.filter((s) => s > maxStress).length;

  if (avgStress <= maxStress && daysOverLimit <= 2) {
    return "yes";
  } else if (avgStress <= maxStress * 1.1 && daysOverLimit <= 3) {
    return "partly";
  }
  return "no";
}

export function computeHabitStatus(
  habit: HabitTemplate,
  metrics: DailyMetrics,
  weekMetrics: DailyMetrics[] = []
): HabitDayStatus {
  let status: HabitStatus = "no";
  let reason: string | undefined;

  switch (habit.signalSource) {
    case "steps":
      status = computeStepsHabitStatus(metrics, habit.rule);
      reason = `You walked ${metrics.steps || 0} steps (target: ${habit.rule.minSteps || 7000})`;
      break;

    case "sleep":
      status = computeSleepHabitStatus(metrics, habit.rule);
      const hours = Math.round((metrics.sleepMinutes || 0) / 60 * 10) / 10;
      reason = `You slept ${hours}h (target: ${(habit.rule.minSleepMinutes || 420) / 60}h)`;
      break;

    case "strength_workouts":
      status = computeStrengthWorkoutsHabitStatus(metrics, habit.rule, weekMetrics);
      const weekTotal = weekMetrics.reduce((sum, m) => sum + (m.strengthWorkouts || 0), 0);
      reason = `You did ${weekTotal} strength workouts this week (target: ${habit.rule.minStrengthWorkoutsPerWeek || 3})`;
      break;

    case "weight":
      status = computeWeightHabitStatus(metrics, habit.rule, weekMetrics);
      const weights = weekMetrics.filter((m) => m.weight !== undefined).map((m) => m.weight!);
      if (weights.length >= 3) {
        const startWeight = Math.min(...weights);
        const endWeight = Math.max(...weights);
        const loss = startWeight - endWeight;
        reason = `Weight trend this week: ${loss > 0 ? `-${loss.toFixed(1)}kg` : `+${Math.abs(loss).toFixed(1)}kg`} (target: -${habit.rule.weightLossPerWeekKg || 0.5}kg/week)`;
      } else {
        reason = `Weight tracking: ${weights.length} measurements this week (need 3+ for trend)`;
      }
      break;

    case "food_log":
      status = computeCaloriesHabitStatus(metrics, habit.rule);
      reason = `You consumed ${metrics.calories || 0} calories (target: ${habit.rule.targetCalories || 2000})`;
      break;

    case "hrv":
      status = computeStressHabitStatus(metrics, habit.rule, weekMetrics);
      const stressLevels = weekMetrics.filter((m) => m.stressLevel !== undefined).map((m) => m.stressLevel!);
      if (stressLevels.length > 0) {
        const avgStress = stressLevels.reduce((sum, s) => sum + s, 0) / stressLevels.length;
        reason = `Average stress level this week: ${avgStress.toFixed(1)}/10 (target: ≤${habit.rule.maxStressLevel || 6})`;
      } else {
        reason = `Stress tracking: No data available`;
      }
      break;

    default:
      status = "no";
      reason = "Tracking not yet implemented for this habit type";
  }

  const score = status === "yes" ? 100 : status === "partly" ? 50 : 0;

  return {
    date: metrics.date,
    status,
    score,
    reason,
    metrics: {
      steps: metrics.steps,
      sleepMinutes: metrics.sleepMinutes,
      strengthWorkouts: metrics.strengthWorkouts,
      weight: metrics.weight,
      calories: metrics.calories,
      stressLevel: metrics.stressLevel,
    },
  };
}

export function computeHabitStatuses(
  habit: HabitTemplate,
  metricsSeries: DailyMetrics[]
): HabitDayStatus[] {
  const statuses: HabitDayStatus[] = [];

  for (let i = 0; i < metricsSeries.length; i++) {
    const metrics = metricsSeries[i];
    const weekStart = Math.max(0, i - 6);
    const weekMetrics = metricsSeries.slice(weekStart, i + 1);

    const status = computeHabitStatus(habit, metrics, weekMetrics);
    statuses.push(status);
  }

  return statuses;
}

export function createHabitFromLever(
  lever: LeverResult,
  interventionName?: string | null
): HabitTemplate {
  const label = interventionName || lever.name;

  switch (lever.type) {
    case "movement":
      return {
        id: "movement_habit",
        domain: "movement",
        label,
        trackingMode: "passive",
        signalSource: "steps",
        rule: {
          minSteps: 7000,
        },
      };

    case "sleep":
      return {
        id: "sleep_habit",
        domain: "sleep",
        label,
        trackingMode: "passive",
        signalSource: "sleep",
        rule: {
          minSleepMinutes: 420,
        },
      };

    case "metabolic":
      if (label.toLowerCase().includes("weight") || label.toLowerCase().includes("gewichts")) {
        return {
          id: "metabolic_weight_habit",
          domain: "metabolic",
          label,
          trackingMode: "passive",
          signalSource: "weight",
          rule: {
            weightLossPerWeekKg: 0.5,
          },
        };
      }
      if (label.toLowerCase().includes("calorie") || label.toLowerCase().includes("nutrition")) {
        return {
          id: "metabolic_nutrition_habit",
          domain: "nutrition",
          label,
          trackingMode: "passive",
          signalSource: "food_log",
          rule: {
            targetCalories: 2000,
            maxCalories: 2200,
          },
        };
      }
      return {
        id: "metabolic_habit",
        domain: "movement",
        label,
        trackingMode: "passive",
        signalSource: "steps",
        rule: {
          minSteps: 7000,
        },
      };

    case "stress":
      return {
        id: "stress_habit",
        domain: "stress",
        label,
        trackingMode: "passive",
        signalSource: "hrv",
        rule: {
          maxStressLevel: 6,
        },
      };

    default:
      return {
        id: "default_habit",
        domain: "movement",
        label,
        trackingMode: "passive",
        signalSource: "steps",
        rule: {
          minSteps: 7000,
        },
      };
  }
}

export function getTodayStatus(
  statuses: HabitDayStatus[]
): HabitDayStatus | null {
  const today = new Date().toISOString().split("T")[0];
  return statuses.find((s) => s.date === today) || null;
}

export function getStreakCount(statuses: HabitDayStatus[]): number {
  let streak = 0;
  const today = new Date().toISOString().split("T")[0];
  const todayIndex = statuses.findIndex((s) => s.date === today);

  if (todayIndex === -1) return 0;

  for (let i = todayIndex; i >= 0; i--) {
    if (statuses[i].status === "yes" || statuses[i].status === "partly") {
      streak++;
    } else {
      break;
    }
  }

  return streak;
}

