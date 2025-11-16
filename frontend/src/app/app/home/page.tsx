"use client";

import { useState, useEffect } from "react";
import { useAppState } from "@/lib/app-state";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ToastContainer } from "@/components/ui/toast";
import type { Adherence, Mood } from "@/lib/api-mock";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const { primaryLever, backendResponse, todayEntry, updateTodayEntry, dailyEntries, habitStatuses, habitTemplate, resolvedHabitPlan } =
    useAppState();
  const router = useRouter();
  const [isSavingMood, setIsSavingMood] = useState(false);
  const [toasts, setToasts] = useState<Array<{ id: string; message: string }>>(
    []
  );

  useEffect(() => {
    if (!primaryLever) {
      router.push("/");
    }
  }, [primaryLever, router]);

  if (!primaryLever) {
    return null;
  }

  const today = new Date().toISOString().split("T")[0];
  const todayStatus = habitStatuses.find((s) => s.date === today);
  const hasSubmittedMoodToday = todayEntry?.mood !== null;

  const addToast = (message: string) => {
    const id = Math.random().toString(36).substring(7);
    setToasts((prev) => [...prev, { id, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };


  const handleMoodClick = async (value: Mood) => {
    if (isSavingMood) return;
    setIsSavingMood(true);
    await updateTodayEntry({ mood: value });
    addToast("Thanks, your mood is logged for today.");
    setIsSavingMood(false);
  };

  const getStreakData = () => {
    // Use resolvedHabitPlan if available, otherwise fallback to last 10 days
    if (resolvedHabitPlan && resolvedHabitPlan.days.length > 0) {
      const planDays = resolvedHabitPlan.days.map((planDay) => {
        const status = habitStatuses.find((s) => s.date === planDay.date);
        const adherence = status?.status === "yes" || status?.status === "partly" ? "yes" : null;
        return {
          date: planDay.date,
          adherence,
          planDay,
        };
      });

      const completed = planDays.filter((e) => e.adherence === "yes").length;
      return { days: planDays, completed, total: resolvedHabitPlan.days.length };
    }

    // Fallback: last 10 days
    const last10Days: Array<{ date: string; adherence: string | null; planDay?: any }> = [];
    for (let i = 0; i < 10; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split("T")[0];
      const status = habitStatuses.find((s) => s.date === dateStr);
      const adherence = status?.status === "yes" || status?.status === "partly" ? "yes" : null;
      last10Days.push({
        date: dateStr,
        adherence,
      });
    }

    const completed = last10Days.filter((e) => e.adherence === "yes").length;
    return { days: last10Days.reverse(), completed, total: 10 };
  };

  const { days, completed } = getStreakData();
  
  // Get today's plan day
  const todayPlanDay = resolvedHabitPlan?.days.find((day) => day.date === today);

  const getMoodEmoji = (mood: Mood | null) => {
    switch (mood) {
      case "sad":
        return "😔";
      case "ok":
        return "😐";
      case "good":
        return "🙂";
      case "great":
        return "😄";
      default:
        return "";
    }
  };

  return (
    <div className="min-h-screen px-6 py-8 pb-8">
      <div className="max-w-md mx-auto space-y-8">
        <div className="space-y-2">
          <h1 className="text-2xl font-bold">Today</h1>
        </div>

        <Card className="p-6 space-y-4">
          <div className="space-y-1">
            <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
              Your current habit
            </p>
            <p className="text-2xl font-bold">
              {resolvedHabitPlan?.interventionName || backendResponse?.interventionName || primaryLever.name}
            </p>
          </div>
          <p className="text-sm text-muted-foreground">
            {backendResponse?.responseText
              ? backendResponse.responseText.split(".")[0] + "."
              : primaryLever.description.split(".")[0] + "."}
          </p>
          <div className="pt-2 space-y-1">
            <p className="text-xs text-muted-foreground">
              Estimated longevity impact
            </p>
            <p className="text-2xl font-semibold">
              {primaryLever.impactScore} / 100
            </p>
            <p className="text-[11px] text-muted-foreground">
              Approximate impact score based on your profile.
            </p>
          </div>
        </Card>

        <Card className="p-6 space-y-4">
          <div className="space-y-3">
            <h2 className="text-lg font-semibold">
              Today's Progress
            </h2>
            {(() => {
              const todayStatus = habitStatuses.find((s) => s.date === today);
              if (!todayStatus) {
                return (
                  <div className="space-y-2">
                    <p className="text-sm text-muted-foreground">
                      Tracking data is being collected...
                    </p>
                  </div>
                );
              }

              const statusEmoji = todayStatus.status === "yes" ? "✅" : todayStatus.status === "partly" ? "⚠️" : "❌";
              const statusText = todayStatus.status === "yes" ? "On track" : todayStatus.status === "partly" ? "Almost there" : "Needs attention";
              const statusColor = todayStatus.status === "yes" ? "text-green-600" : todayStatus.status === "partly" ? "text-yellow-600" : "text-red-600";

              return (
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{statusEmoji}</span>
                    <div>
                      <p className={`font-semibold ${statusColor}`}>
                        {statusText}
                      </p>
                      {todayStatus.reason && (
                        <p className="text-sm text-muted-foreground mt-1">
                          {todayStatus.reason}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="pt-2 border-t">
                    <p className="text-xs text-muted-foreground">
                      Data automatically tracked from your connected devices
                    </p>
                  </div>
                </div>
              );
            })()}
          </div>
        </Card>

        {todayPlanDay && (
          <Card className="p-6 space-y-4">
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">
                Today's Plan
              </h2>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-muted-foreground mb-1">
                    Target steps
                  </p>
                  <p className="text-3xl font-bold">
                    {todayPlanDay.targetSteps.toLocaleString()}
                  </p>
                </div>
                <div className="pt-2 border-t">
                  <p className="text-sm text-muted-foreground">
                    {todayPlanDay.activity.split(":")[1]?.trim() || todayPlanDay.activity}
                  </p>
                </div>
              </div>
            </div>
          </Card>
        )}

        <Card className="p-6 space-y-4">
          <h2 className="text-lg font-semibold">How do you feel today?</h2>
          <div className="flex gap-3">
            {(
              [
                { mood: "sad" as Mood, emoji: "😔" },
                { mood: "ok" as Mood, emoji: "😐" },
                { mood: "good" as Mood, emoji: "🙂" },
                { mood: "great" as Mood, emoji: "😄" },
              ] as const
            ).map(({ mood, emoji }) => (
              <Button
                key={mood}
                variant={todayEntry?.mood === mood ? "default" : "outline"}
                onClick={() => handleMoodClick(mood)}
                className="flex-1 h-12 text-2xl"
                disabled={isSavingMood}
              >
                {emoji}
              </Button>
            ))}
          </div>
        </Card>

        <div className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide">
            Streak
          </h2>
          <div className="flex gap-2">
            {days.map((entry) => {
              const isToday = entry.date === today;
              const status = habitStatuses.find((s) => s.date === entry.date);
              const isCompleted = status?.status === "yes" || status?.status === "partly";
              let fillClass = "bg-muted border border-muted-foreground/20";
              let ringClass = "";

              if (isCompleted) {
                fillClass = "bg-primary border-primary";
              } else if (isToday) {
                fillClass = "bg-background border-2 border-primary";
                ringClass = "ring-2 ring-primary/20";
              }

              const planDay = entry.planDay;
              const tooltipText = planDay 
                ? `Day ${planDay.dayIndex} – Target ${planDay.targetSteps.toLocaleString()} steps`
                : (isToday ? "Today" : entry.date);

              return (
                <div
                  key={entry.date}
                  className={`flex-1 h-8 rounded transition-all ${fillClass} ${ringClass} ${
                    isCompleted ? "scale-105" : ""
                  }`}
                  title={tooltipText}
                />
              );
            })}
          </div>
          <p className="text-sm text-muted-foreground">
            {completed} / {resolvedHabitPlan?.days.length || 10} days with focus completed
          </p>
        </div>

        {resolvedHabitPlan && resolvedHabitPlan.days.length > 0 && (
          <Card className="p-6 space-y-4">
            <div className="space-y-3">
              <h2 className="text-lg font-semibold">
                10-Day Plan
              </h2>
              <div className="flex gap-2">
                {resolvedHabitPlan.days.map((planDay) => {
                  const isToday = planDay.date === today;
                  const status = habitStatuses.find((s) => s.date === planDay.date);
                  const isCompleted = status?.status === "yes" || status?.status === "partly";
                  let fillClass = "bg-muted border border-muted-foreground/20";
                  let ringClass = "";

                  if (isCompleted) {
                    fillClass = "bg-primary border-primary";
                  } else if (isToday) {
                    fillClass = "bg-background border-2 border-primary";
                    ringClass = "ring-2 ring-primary/20";
                  }

                  return (
                    <div
                      key={planDay.date}
                      className={`flex-1 h-10 rounded transition-all ${fillClass} ${ringClass} ${
                        isCompleted ? "scale-105" : ""
                      } flex items-center justify-center text-xs font-medium`}
                      title={`Day ${planDay.dayIndex} – ${planDay.targetSteps.toLocaleString()} steps: ${planDay.activity}`}
                    >
                      {planDay.dayIndex}
                    </div>
                  );
                })}
              </div>
            </div>
          </Card>
        )}
      </div>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}


