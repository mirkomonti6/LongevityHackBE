"use client";

import { useAppState } from "@/lib/app-state";
import { Card } from "@/components/ui/card";

export default function ProgressPage() {
  const { dailyEntries, backendResponse, primaryLever } = useAppState();

  const getStreakData = () => {
    const last10Days = dailyEntries.slice(0, 10);
    const completed = last10Days.filter((e) => e.adherence === "yes").length;
    return { completed, total: 10 };
  };

  const { completed } = getStreakData();

  const getAdherenceEmoji = (adherence: string | null) => {
    switch (adherence) {
      case "yes":
        return "✅";
      case "no":
        return "❌";
      default:
        return "—";
    }
  };

  const getMoodEmoji = (mood: string | null) => {
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
        return "—";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
    });
  };

  const habitName = backendResponse?.interventionName || primaryLever?.name || "Your Habit";
  const habitDescription = backendResponse?.responseText || primaryLever?.description || "";

  return (
    <div className="min-h-screen px-6 py-8 pb-24">
      <div className="max-w-md mx-auto space-y-8">
        <div className="space-y-2">
          <h1 className="text-3xl md:text-4xl font-bold">Progress</h1>
          <p className="text-muted-foreground">
            Streak: {completed} / 10 days
          </p>
        </div>

        {habitName && (
          <Card className="p-6 space-y-4">
            <div className="space-y-1">
              <p className="text-xs font-semibold uppercase tracking-wide text-muted-foreground">
                Your current habit
              </p>
              <p className="text-xl font-bold">{habitName}</p>
            </div>
            {habitDescription && (
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">
                {habitDescription}
              </p>
            )}
          </Card>
        )}

        <div className="space-y-3">
          {dailyEntries.length === 0 ? (
            <Card className="p-6 text-center text-muted-foreground">
              No entries yet. Start tracking your progress on the Home screen.
            </Card>
          ) : (
            dailyEntries.map((entry) => (
              <Card key={entry.date} className="p-4">
                <div className="flex items-center justify-between">
                  <div className="space-y-1">
                    <p className="font-medium">{formatDate(entry.date)}</p>
                    <div className="flex items-center gap-3 text-sm text-muted-foreground">
                      <span>
                        {getAdherenceEmoji(entry.adherence)}{" "}
                        {entry.adherence || "Not set"}
                      </span>
                      <span>{getMoodEmoji(entry.mood)}</span>
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </div>
  );
}


