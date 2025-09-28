import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sentiment Analysis",
  description: "Simple UI that calls a Flask sentiment API",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}