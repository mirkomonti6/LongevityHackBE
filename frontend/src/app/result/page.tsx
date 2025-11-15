"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppState } from "@/lib/app-state";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function ResultPage() {
  const router = useRouter();
  const { primaryLever, backendResponse } = useAppState();

  useEffect(() => {
    if (!primaryLever) {
      router.push("/loading");
    }
  }, [primaryLever, router]);

  if (!primaryLever) {
    return null;
  }

  const handleContinue = () => {
    router.push("/app/home");
  };

  const habitName = backendResponse?.interventionName || primaryLever.name;
  const habitDescription = backendResponse?.responseText || primaryLever.description;

  return (
    <div className="fixed inset-0 flex flex-col bg-background overflow-y-auto">
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 min-h-screen">
        <div className="w-full max-w-md space-y-8">
          <div className="space-y-4 text-center">
            <Badge variant="secondary" className="mb-2">
              Your recommended habit
            </Badge>
            <h1 className="text-3xl md:text-4xl font-bold leading-tight">
              {habitName}
            </h1>
          </div>

          <Card className="p-6 space-y-4">
            <h2 className="text-xl font-semibold">Recommendation</h2>
            <div className="text-base text-muted-foreground whitespace-pre-wrap">
              {habitDescription}
            </div>
          </Card>

          <Button
            onClick={handleContinue}
            className="w-full h-12 text-base font-semibold"
          >
            Continue
          </Button>
        </div>
      </div>
    </div>
  );
}

