import { LoaderCircle } from "lucide-react";

interface SpinnerProps {
  size?: number;
  label?: string;
}

export default function Spinner({
  size = 28,
  label = "Loading",
}: SpinnerProps) {
  return (
    <div
      role="status"
      className="flex flex-col items-center justify-center gap-3"
    >
      <LoaderCircle
        size={size}
        className="animate-spin text-[var(--primary)]"
      />

      <span className="text-sm text-[var(--muted)]">
        {label}
      </span>
    </div>
  );
}