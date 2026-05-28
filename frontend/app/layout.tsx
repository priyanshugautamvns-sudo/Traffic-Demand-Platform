import type { Metadata } from "next";
import "./globals.css";
import { DashboardShell } from "@/components/DashboardShell";
import type { ReactNode } from "react";

export const metadata: Metadata = {
  title: "Traffic Demand AI",
  description: "Flipkart hackathon traffic demand prediction platform"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <DashboardShell>{children}</DashboardShell>
      </body>
    </html>
  );
}
