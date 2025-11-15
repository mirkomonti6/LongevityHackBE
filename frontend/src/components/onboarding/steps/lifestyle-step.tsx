"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import type { OnboardingData, SportType, WorkActivityLevel } from "@/lib/onboarding-schema";

const SPORT_TYPES: { value: SportType; label: string }[] = [
  { value: "running", label: "Running" },
  { value: "cycling", label: "Cycling" },
  { value: "swimming", label: "Swimming" },
  { value: "strength-training", label: "Strength Training" },
  { value: "yoga", label: "Yoga" },
  { value: "team-sports", label: "Team Sports" },
  { value: "walking", label: "Walking" },
  { value: "other", label: "Other" },
  { value: "none", label: "None" },
];

const WORK_ACTIVITY_LEVELS: { value: WorkActivityLevel; label: string }[] = [
  { value: "sedentary", label: "Sedentary (mostly sitting)" },
  { value: "light", label: "Light activity (standing, walking)" },
  { value: "moderate", label: "Moderate activity (regular movement)" },
  { value: "active", label: "Active (physically demanding)" },
];

interface LifestyleStepProps {
  data: OnboardingData;
  onUpdateField: <K extends keyof OnboardingData>(
    field: K,
    value: OnboardingData[K]
  ) => void;
  onToggleSportType: (sport: SportType) => void;
}

export function LifestyleStep({
  data,
  onUpdateField,
  onToggleSportType,
}: LifestyleStepProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Lifestyle</CardTitle>
        <CardDescription>
          What does your current daily life look like? Be honest – this helps us
          find the best recommendation.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-8">
        <div className="space-y-4">
          <div className="flex justify-between">
            <Label htmlFor="sleep-hours">Average sleep duration</Label>
            <span className="text-sm text-muted-foreground">
              {data.sleepHours ?? 7}h
            </span>
          </div>
          <Slider
            id="sleep-hours"
            min={4}
            max={9}
            step={0.5}
            value={[data.sleepHours ?? 7]}
            onValueChange={([value]) => onUpdateField("sleepHours", value)}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How many hours do you sleep on average per night?
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between">
            <Label htmlFor="sleep-quality">Sleep quality</Label>
            <span className="text-sm text-muted-foreground">
              {data.sleepQuality ?? 5}/10
            </span>
          </div>
          <Slider
            id="sleep-quality"
            min={1}
            max={10}
            step={1}
            value={[data.sleepQuality ?? 5]}
            onValueChange={([value]) => onUpdateField("sleepQuality", value)}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How would you rate your sleep quality? (1 = very poor, 10 =
            excellent)
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between">
            <Label htmlFor="movement-days">Movement per week</Label>
            <span className="text-sm text-muted-foreground">
              {data.movementDays ?? 3} days
            </span>
          </div>
          <Slider
            id="movement-days"
            min={0}
            max={7}
            step={1}
            value={[data.movementDays ?? 3]}
            onValueChange={([value]) => onUpdateField("movementDays", value)}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How many days per week do you move at least 20–30 minutes?
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between">
            <Label htmlFor="stress-level">Stress level</Label>
            <span className="text-sm text-muted-foreground">
              {data.stressLevel ?? 5}/10
            </span>
          </div>
          <Slider
            id="stress-level"
            min={1}
            max={10}
            step={1}
            value={[data.stressLevel ?? 5]}
            onValueChange={([value]) => onUpdateField("stressLevel", value)}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How stressed did you feel in the last week? (1 = not at all, 10 =
            very stressed)
          </p>
        </div>

        <div className="space-y-4">
          <div className="flex justify-between">
            <Label htmlFor="energy-level">Energy level</Label>
            <span className="text-sm text-muted-foreground">
              {data.energyLevel ?? 5}/10
            </span>
          </div>
          <Slider
            id="energy-level"
            min={1}
            max={10}
            step={1}
            value={[data.energyLevel ?? 5]}
            onValueChange={([value]) => onUpdateField("energyLevel", value)}
            className="w-full"
          />
          <p className="text-xs text-muted-foreground">
            How was your energy level last week? (1 = very low, 10 = very
            high)
          </p>
        </div>

        <div className="space-y-4 pt-4 border-t">
          <Label className="text-base font-semibold">Sports & Exercise</Label>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label className="text-sm">What types of sports or exercise do you do?</Label>
              <div className="grid grid-cols-2 gap-2">
                {SPORT_TYPES.map((sport) => (
                  <div key={sport.value} className="flex items-center space-x-2">
                    <Checkbox
                      id={sport.value}
                      checked={data.sportTypes.includes(sport.value)}
                      onCheckedChange={() => onToggleSportType(sport.value)}
                    />
                    <Label
                      htmlFor={sport.value}
                      className="text-sm font-normal cursor-pointer"
                    >
                      {sport.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>

            {data.sportTypes.length > 0 && !data.sportTypes.includes("none") && (
              <>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <Label htmlFor="sport-frequency">How often do you exercise?</Label>
                    <span className="text-sm text-muted-foreground">
                      {data.sportFrequency ?? 2} times/week
                    </span>
                  </div>
                  <Slider
                    id="sport-frequency"
                    min={1}
                    max={7}
                    step={1}
                    value={[data.sportFrequency ?? 2]}
                    onValueChange={([value]) =>
                      onUpdateField("sportFrequency", value)
                    }
                    className="w-full"
                  />
                </div>

                <div className="space-y-4">
                  <div className="flex justify-between">
                    <Label htmlFor="sport-intensity">Exercise intensity</Label>
                    <span className="text-sm text-muted-foreground">
                      {data.sportIntensity ?? 5}/10
                    </span>
                  </div>
                  <Slider
                    id="sport-intensity"
                    min={1}
                    max={10}
                    step={1}
                    value={[data.sportIntensity ?? 5]}
                    onValueChange={([value]) =>
                      onUpdateField("sportIntensity", value)
                    }
                    className="w-full"
                  />
                  <p className="text-xs text-muted-foreground">
                    How intense are your workouts? (1 = very light, 10 = very
                    intense)
                  </p>
                </div>
              </>
            )}
          </div>
        </div>

        <div className="space-y-4 pt-4 border-t">
          <Label className="text-base font-semibold">Work & Daily Activity</Label>
          <div className="space-y-4">
            <div className="space-y-3">
              <Label>What's your work activity level?</Label>
              <RadioGroup
                value={data.workActivityLevel ?? ""}
                onValueChange={(value) =>
                  onUpdateField("workActivityLevel", value as WorkActivityLevel)
                }
              >
                {WORK_ACTIVITY_LEVELS.map((level) => (
                  <div key={level.value} className="flex items-center space-x-2">
                    <RadioGroupItem value={level.value} id={level.value} />
                    <Label htmlFor={level.value} className="font-normal">
                      {level.label}
                    </Label>
                  </div>
                ))}
              </RadioGroup>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between">
                <Label htmlFor="work-from-home">Work from home</Label>
                <span className="text-sm text-muted-foreground">
                  {data.workFromHome ?? 0}%
                </span>
              </div>
              <Slider
                id="work-from-home"
                min={0}
                max={100}
                step={10}
                value={[data.workFromHome ?? 0]}
                onValueChange={([value]) => onUpdateField("workFromHome", value)}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                What percentage of your work time do you spend working from
                home?
              </p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

