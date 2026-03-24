import { cn } from "@/lib/utils";

interface BadgeProps {
  label: string;
  color?: string;
  variant?: "filled" | "outline" | "subtle";
  size?: "sm" | "md";
}

export function Badge({
  label,
  color,
  variant = "subtle",
  size = "sm",
}: BadgeProps) {
  const baseClasses =
    "inline-flex items-center font-medium rounded-full whitespace-nowrap";
  const sizeClasses = size === "sm" ? "px-2.5 py-0.5 text-xs" : "px-3 py-1 text-sm";

  if (color && variant === "filled") {
    return (
      <span
        className={cn(baseClasses, sizeClasses, "text-white")}
        style={{ backgroundColor: color }}
      >
        {label}
      </span>
    );
  }

  if (color && variant === "subtle") {
    return (
      <span
        className={cn(baseClasses, sizeClasses)}
        style={{
          backgroundColor: `${color}18`,
          color: color,
        }}
      >
        {label}
      </span>
    );
  }

  if (color && variant === "outline") {
    return (
      <span
        className={cn(baseClasses, sizeClasses, "border")}
        style={{
          borderColor: `${color}40`,
          color: color,
        }}
      >
        {label}
      </span>
    );
  }

  return (
    <span
      className={cn(
        baseClasses,
        sizeClasses,
        "bg-slate-100 text-slate-700",
      )}
    >
      {label}
    </span>
  );
}
