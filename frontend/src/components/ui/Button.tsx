import type { ButtonHTMLAttributes } from "react";
import { LoaderCircle } from "lucide-react";
import { cn } from "../../utils/cn";

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline" | "ghost" | "danger";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
}

const variants = {
  primary:
    "bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)]",
  secondary:
    "bg-[var(--secondary)] text-[var(--secondary-foreground)]",
  outline:
    "border border-[var(--border)] hover:bg-[var(--surface-hover)]",
  ghost:
    "hover:bg-[var(--surface-hover)]",
  danger:
    "bg-red-600 text-white hover:bg-red-700",
};

const sizes = {
  sm: "h-9 px-3 text-sm",
  md: "h-11 px-5 text-sm",
  lg: "h-13 px-7 text-base",
};

export default function Button({
  children,
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  className,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      {...props}
      type={type}
      disabled={disabled || loading}
      aria-busy={loading}
      className={cn(
        "inline-flex items-center justify-center gap-2 rounded-xl font-medium transition-all active:scale-95",
        variants[variant],
        sizes[size],
        className
      )}
    >
      {loading && (
        <LoaderCircle
          size={17}
          className="animate-spin"
        />
      )}

      {children}
    </button>
  );
}