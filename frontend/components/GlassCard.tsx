import clsx from "clsx";
import { type ReactNode } from "react";

export function GlassCard({
  children,
  className
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={clsx("glass rounded-2xl shadow-glass", className)}>{children}</div>;
}

