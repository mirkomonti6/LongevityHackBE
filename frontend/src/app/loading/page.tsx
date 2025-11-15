"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppState } from "@/lib/app-state";
import { fetchPrimaryLever } from "@/lib/api-mock";

export default function LoadingPage() {
  const router = useRouter();
  const { onboardingData, setPrimaryLever } = useAppState();

  useEffect(() => {
    if (!onboardingData) {
      router.push("/");
      return;
    }

    const loadLever = async () => {
      try {
        const lever = await fetchPrimaryLever(onboardingData);
        setPrimaryLever(lever);
        router.push("/result");
      } catch (error) {
        console.error("Failed to fetch primary lever:", error);
        router.push("/result");
      }
    };

    loadLever();
  }, [onboardingData, setPrimaryLever, router]);

  return (
    <div className="fixed inset-0 flex flex-col bg-background overflow-y-auto">
      <div className="flex-1 flex flex-col items-center justify-center px-6 py-12 min-h-screen">
        <div className="w-full max-w-md space-y-8 text-center">
          <div className="space-y-6">
            <p className="text-sm text-muted-foreground uppercase tracking-wide">
              Analyzing your data…
            </p>
            <h1 className="text-3xl md:text-4xl font-bold leading-tight">
              Finding your #1 longevity lever
            </h1>
            <p className="text-base md:text-lg text-muted-foreground">
              We compare your answers and bloodwork with longevity research to
              pick one key improvement.
            </p>
          </div>

          <div className="flex justify-center py-8">
            <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          </div>

          <p className="text-sm text-muted-foreground">
            This may take a few seconds.
          </p>
        </div>
      </div>
    </div>
  );
}

