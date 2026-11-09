import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sentiment Lab | Binary NLP Analysis",
  description: "A focused DistilBERT sentiment analysis workspace with real model inference.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
