import type { ReactNode } from "react";
import { cn } from "../../utils/cn";

interface BadgeProps {
  children: ReactNode;
  variant?: "default" | "success" | "warning" | "danger" | "info";
}

const variants = {
  default: "bg-violet-500/10 text-[var(--primary)]",
  success: "bg-emerald-500/10 text-[var(--success)]",
  warning: "bg-amber-500/10 text-[var(--warning)]",
  danger: "bg-red-500/10 text-[var(--danger)]",
  info: "bg-blue-500/10 text-[var(--info)]",
};

export default function Badge({
  children,
  variant = "default",
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-3 py-1 text-xs font-medium",
        variants[variant]
      )}
    >
      {children}
    </span>
  );
}