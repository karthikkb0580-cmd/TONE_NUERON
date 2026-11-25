import { forwardRef, useId } from "react";
import type { InputHTMLAttributes } from "react";
import { cn } from "../../utils/cn";

interface InputProps
  extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  function Input(
    { label, error, className, id, ...props },
    ref
  ) {
    const generatedId = useId();
    const inputId = id || generatedId;
    const errorId = `${inputId}-error`;

    return (
      <div className="flex w-full flex-col gap-2">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium"
          >
            {label}
          </label>
        )}

        <input
          {...props}
          ref={ref}
          id={inputId}
          aria-invalid={Boolean(error)}
          aria-describedby={error ? errorId : undefined}
          className={cn(
            "h-12 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 text-sm outline-none transition-colors placeholder:text-[var(--muted)] focus:border-[var(--primary)]",
            error && "border-red-500",
            className
          )}
        />

        {error && (
          <span
            id={errorId}
            className="text-xs text-[var(--danger)]"
          >
            {error}
          </span>
        )}
      </div>
    );
  }
);

export default Input;