import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EquityForge — AI Equity Research Reports",
  description:
    "Transform Financial Documents into Institutional-Quality Equity Research Reports with AI.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
