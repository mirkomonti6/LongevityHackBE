"use client";

import { useState, useEffect } from "react";
import { useAppState } from "@/lib/app-state";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ToastContainer } from "@/components/ui/toast";
import type { Adherence, Mood } from "@/lib/api-mock";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const { primaryLever, backendResponse, todayEntry, updateTodayEntry, dailyEntries } =
    useAppState();
  const router = useRouter();
  const [isSavingCheckin, setIsSavingCheckin] = useState(false);
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

  const hasSubmittedCheckinToday = todayEntry?.adherence !== null;
  const hasSubmittedMoodToday = todayEntry?.mood !== null;

  const addToast = (message: string) => {
    const id = Math.random().toString(36).substring(7);
    setToasts((prev) => [...prev, { id, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const handleAdherenceClick = async (value: Adherence) => {
    if (isSavingCheckin) return;
    setIsSavingCheckin(true);
    await updateTodayEntry({ adherence: value });
    addToast("Check-in saved for today ✅");
    setIsSavingCheckin(false);
  };

  const handleMoodClick = async (value: Mood) => {
    if (isSavingMood) return;
    setIsSavingMood(true);
    await updateTodayEntry({ mood: value });
    addToast("Thanks, your mood is logged for today.");
    setIsSavingMood(false);
  };

  const getStreakData = () => {
    const last10Days: Array<{ date: string; adherence: string | null }> = [];
    const today = new Date().toISOString().split("T")[0];

    for (let i = 0; i < 10; i++) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split("T")[0];
      const entry = dailyEntries.find((e) => e.date === dateStr);
      last10Days.push({
        date: dateStr,
        adherence: entry?.adherence || null,
      });
    }

    const completed = last10Days.filter((e) => e.adherence === "yes").length;
    return { days: last10Days.reverse(), completed, total: 10, today };
  };

  const { days, completed, today } = getStreakData();

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
              {backendResponse?.interventionName || primaryLever.name}
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
          <div className="space-y-2">
            <h2 className="text-lg font-semibold">
              Did you follow this habit today?
            </h2>
            <p className="text-sm text-muted-foreground">
              {backendResponse?.interventionName || primaryLever.name}
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant={
                todayEntry?.adherence === "yes" ? "default" : "outline"
              }
              onClick={() => handleAdherenceClick("yes")}
              className="flex-1 h-12"
              disabled={isSavingCheckin}
            >
              ✅ Yes
            </Button>
            <Button
              variant={todayEntry?.adherence === "no" ? "default" : "outline"}
              onClick={() => handleAdherenceClick("no")}
              className="flex-1 h-12"
              disabled={isSavingCheckin}
            >
              ❌ No
            </Button>
          </div>
        </Card>

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
              const isCompleted = entry.adherence === "yes";
              let fillClass = "bg-muted border border-muted-foreground/20";
              let ringClass = "";

              if (isCompleted) {
                fillClass = "bg-primary border-primary";
              } else if (isToday && !hasSubmittedCheckinToday) {
                fillClass = "bg-background border-2 border-primary";
                ringClass = "ring-2 ring-primary/20";
              } else if (isToday && hasSubmittedCheckinToday) {
                fillClass = "bg-muted border border-muted-foreground/20";
              }

              return (
                <div
                  key={entry.date}
                  className={`flex-1 h-8 rounded transition-all ${fillClass} ${ringClass} ${
                    isCompleted ? "scale-105" : ""
                  }`}
                  title={isToday ? "Today" : entry.date}
                />
              );
            })}
          </div>
          <p className="text-sm text-muted-foreground">
            {completed} / 10 days with focus completed
          </p>
        </div>
      </div>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </div>
  );
}


