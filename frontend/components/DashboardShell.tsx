import { type ReactNode } from "react";
import { Nav } from "./Nav";

export function DashboardShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen text-slate-200">
      <Nav />
      <main>{children}</main>
    </div>
  );
}

