"use client";

import { usePathname, useRouter } from "next/navigation";
import { Home, BarChart3 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();

  const navItems = [
    { path: "/app/home", label: "Home", icon: Home },
    { path: "/app/progress", label: "Progress", icon: BarChart3 },
  ];

  return (
    <div className="fixed inset-0 flex flex-col bg-background overflow-hidden">
      <div className="flex-1 overflow-y-auto pb-20">{children}</div>

      <div className="fixed bottom-0 left-0 right-0 bg-background border-t">
        <div className="max-w-md mx-auto">
          <nav className="flex items-center justify-around h-16">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => router.push(item.path)}
                  className={cn(
                    "flex flex-col items-center justify-center gap-1 flex-1 h-full transition-colors",
                    isActive
                      ? "text-primary"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-xs font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>
    </div>
  );
}


