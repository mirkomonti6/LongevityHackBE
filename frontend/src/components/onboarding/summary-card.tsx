"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import type { OnboardingData } from "@/lib/onboarding-schema";

type Domain = "sleep" | "movement" | "metabolic" | "stress";

interface DomainAnalysis {
  domain: Domain;
  score: number;
  habit: string;
  impact: string;
  yearsGained: number;
}

const DOMAIN_LABELS: Record<Domain, string> = {
  sleep: "Sleep & Recovery",
  movement: "Movement",
  metabolic: "Metabolic Health",
  stress: "Stress & Mental Load",
};

function analyzeDomains(data: OnboardingData): DomainAnalysis[] {
  const analyses: DomainAnalysis[] = [];

  if (data.sleepHours !== null) {
    const sleepScore = data.sleepHours < 7 ? 4 : data.sleepHours < 8 ? 2 : 1;

    analyses.push({
      domain: "sleep",
      score: sleepScore,
      habit: "Improve sleep hygiene",
      impact: "Better sleep duration can reduce inflammation and improve cognitive function.",
      yearsGained: sleepScore >= 3 ? 3.2 : sleepScore >= 2 ? 2.1 : 1.5,
    });
  }

  if (data.movementDays !== null) {
    const movementScore = data.movementDays < 2 ? 4 : data.movementDays < 4 ? 2 : 1;

    analyses.push({
      domain: "movement",
      score: movementScore,
      habit: "Establish regular movement",
      impact: "More movement improves cardiovascular health, insulin sensitivity, and muscle mass.",
      yearsGained: movementScore >= 3 ? 2.8 : movementScore >= 2 ? 1.9 : 1.2,
    });
  }

  if (data.labPdfFile !== null || data.hba1c !== null || data.ldl !== null) {
    let metabolicScore = 0;
    if (data.hba1c !== null && data.hba1c > 5.7) metabolicScore += 2;
    if (data.ldl !== null && data.ldl > 130) metabolicScore += 2;
    if (data.labPdfFile !== null) metabolicScore += 1;
    if (metabolicScore === 0) metabolicScore = 1;

    analyses.push({
      domain: "metabolic",
      score: metabolicScore,
      habit: "Optimize metabolic health",
      impact: "Improved blood sugar and lipid levels significantly reduce the risk of chronic diseases.",
      yearsGained: metabolicScore >= 4 ? 3.5 : metabolicScore >= 2 ? 2.3 : 1.6,
    });
  }

  if (data.stressLevel !== null) {
    const stressScore = data.stressLevel >= 8 ? 4 : data.stressLevel >= 6 ? 2 : 1;

    analyses.push({
      domain: "stress",
      score: stressScore,
      habit: "Improve stress management",
      impact: "Chronic stress increases inflammation and accelerates the aging process.",
      yearsGained: stressScore >= 3 ? 2.5 : stressScore >= 2 ? 1.7 : 1.0,
    });
  }

  return analyses;
}

function getKeyFactor(analyses: DomainAnalysis[]): DomainAnalysis | null {
  if (analyses.length === 0) return null;
  return analyses.reduce((max, current) =>
    current.score > max.score ? current : max
  );
}

interface SummaryCardProps {
  data: OnboardingData;
}

export function SummaryCard({ data }: SummaryCardProps) {
  const analyses = analyzeDomains(data);
  const keyFactor = getKeyFactor(analyses);

  if (!keyFactor) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Analysis complete</CardTitle>
          <CardDescription>
            Thank you for your information! We're analyzing your data and will
            provide you with a personalized recommendation soon.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button className="w-full" disabled>
            Continue to Dashboard (coming soon)
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-0 shadow-lg">
      <CardHeader className="text-center pb-4">
        <CardTitle className="text-2xl md:text-3xl">
          Your focus for the next few weeks
        </CardTitle>
        <CardDescription className="text-base">
          Based on your answers, we've identified the area that could have the
          most impact for you.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-3 text-center">
          <Badge variant="secondary" className="text-sm">
            {DOMAIN_LABELS[keyFactor.domain]}
          </Badge>
          <h3 className="text-xl md:text-2xl font-semibold">
            {keyFactor.habit}
          </h3>
          <p className="text-sm text-muted-foreground">{keyFactor.impact}</p>
        </div>

        <div className="rounded-lg border bg-muted/50 p-6 text-center">
          <div className="flex items-baseline justify-center gap-2">
            <span className="text-4xl md:text-5xl font-bold text-primary">
              +{keyFactor.yearsGained.toFixed(1)}
            </span>
            <span className="text-base text-muted-foreground">years</span>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Potential lifespan extension if you consistently implement this
            habit over the next 5 years.
          </p>
        </div>

        {data.labPdfFile && (
          <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
            <p className="text-xs text-muted-foreground">
              <span className="font-medium">Lab report uploaded:</span>{" "}
              {data.labPdfFile.name}. Your recommendation includes analysis of
              your blood values.
            </p>
          </div>
        )}

        {analyses.filter((a) => a.domain !== keyFactor.domain).length > 0 && (
          <div className="space-y-2">
            <p className="text-sm font-medium text-center">Other areas:</p>
            <div className="flex flex-wrap justify-center gap-2">
              {analyses
                .filter((a) => a.domain !== keyFactor.domain)
                .map((analysis) => (
                  <Badge key={analysis.domain} variant="outline">
                    {DOMAIN_LABELS[analysis.domain]}
                  </Badge>
                ))}
            </div>
          </div>
        )}

        <Button className="w-full h-12 text-base" disabled>
          Continue to Dashboard (coming soon)
        </Button>
      </CardContent>
    </Card>
  );
}

