"use client";

import { Button } from "@/components/ui/button";
import { useRef, ChangeEvent } from "react";
import { Upload, FileText, X } from "lucide-react";
import type { OnboardingData } from "@/lib/onboarding-schema";

interface StepLabUploadProps {
  data: OnboardingData;
  onSetLabFile: (file: File | null) => void;
}

export function StepLabUpload({ data, onSetLabFile }: StepLabUploadProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    if (file && (file.type === "application/pdf" || file.type === "image/png")) {
      onSetLabFile(file);
    } else if (file) {
      alert("Please upload a PDF or PNG file");
    } else {
      onSetLabFile(null);
    }
  };

  const handleRemoveFile = () => {
    onSetLabFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="space-y-6">
      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.png,image/png"
        onChange={handleFileChange}
        className="hidden"
        id="lab-pdf-input"
      />

      {!data.labPdfFile ? (
        <label htmlFor="lab-pdf-input">
          <div className="border-2 border-dashed border-muted-foreground/30 rounded-lg p-8 hover:border-muted-foreground/50 hover:bg-muted/30 transition-colors cursor-pointer">
            <div className="flex flex-col items-center gap-3 text-center">
              <div className="w-12 h-12 rounded-full bg-muted flex items-center justify-center">
                <Upload className="w-6 h-6 text-muted-foreground" />
              </div>
              <div className="space-y-1">
                <p className="text-base font-medium">Upload PDF</p>
                <p className="text-xs text-muted-foreground">
                  Click to browse or drag and drop
                </p>
              </div>
            </div>
          </div>
        </label>
      ) : (
        <div className="rounded-lg border border-border bg-muted/30 p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded bg-primary/10 flex items-center justify-center flex-shrink-0">
              <FileText className="w-5 h-5 text-primary" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {data.labPdfFile.name}
              </p>
              <p className="text-xs text-muted-foreground">
                {(data.labPdfFile.size / 1024).toFixed(1)} KB
              </p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              onClick={handleRemoveFile}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

