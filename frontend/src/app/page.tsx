"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { OnboardingWizard } from "@/components/onboarding/onboarding-wizard";
import { useAppState } from "@/lib/app-state";

export default function Home() {
  const router = useRouter();
  const { primaryLever } = useAppState();

  useEffect(() => {
    if (primaryLever) {
      router.push("/app/home");
    }
  }, [primaryLever, router]);

  return <OnboardingWizard />;
}
