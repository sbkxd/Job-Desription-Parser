import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Providers from "./providers";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "JD Skill Intelligence Platform | AI-Powered Skill Extraction",
  description: "Extract required and preferred skills, seniority, experience range, and normalized ESCO taxonomy mappings from job descriptions using Mistral AI and LangGraph orchestration.",
  keywords: ["Job Description Parser", "Skill Extraction", "ESCO Mapping", "Talent Intelligence", "AI Recruitment"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col bg-background text-text-primary selection:bg-accent-primary/20 selection:text-accent-primary">
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
