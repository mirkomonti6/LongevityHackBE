"use client";

import { useEffect, useState } from "react";
import { cn } from "@/lib/utils";

interface ToastProps {
  message: string;
  duration?: number;
  onClose?: () => void;
}

export function Toast({ message, duration = 3000, onClose }: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      setTimeout(() => onClose?.(), 300);
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  if (!isVisible) return null;

  return (
    <div
      className={cn(
        "bg-foreground text-background px-4 py-3 rounded-lg shadow-lg",
        "text-sm font-medium min-w-[200px] text-center",
        "animate-in fade-in slide-in-from-bottom-4 duration-300"
      )}
    >
      {message}
    </div>
  );
}

interface ToastContainerProps {
  toasts: Array<{ id: string; message: string }>;
  onRemove: (id: string) => void;
}

export function ToastContainer({ toasts, onRemove }: ToastContainerProps) {
  return (
    <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 flex flex-col gap-2 items-center pointer-events-none">
      {toasts.map((toast, index) => (
        <div
          key={toast.id}
          className="pointer-events-auto"
          style={{ order: -index }}
        >
          <Toast
            message={toast.message}
            onClose={() => onRemove(toast.id)}
          />
        </div>
      ))}
    </div>
  );
}

