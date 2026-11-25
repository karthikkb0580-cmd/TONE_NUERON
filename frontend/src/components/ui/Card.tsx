import type { HTMLAttributes } from "react";
import { cn } from "../../utils/cn";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  hoverable?: boolean;
}

export default function Card({
  children,
  className,
  hoverable = false,
  ...props
}: CardProps) {
  return (
    <div
      {...props}
      className={cn(
        "rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-[var(--shadow)] transition-all",
        hoverable &&
          "hover:-translate-y-1 hover:border-[var(--primary)]",
        className
      )}
    >
      {children}
    </div>
  );
}