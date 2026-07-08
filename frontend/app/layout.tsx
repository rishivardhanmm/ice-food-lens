import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";

export const metadata: Metadata = {
  title: "FoodLens AI",
  description: "AI-assisted food nutrition estimation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen text-slate-900">
        <nav className="border-b bg-white">
          <div className="mx-auto flex max-w-6xl items-center gap-6 px-4 py-3">
            <span className="text-lg font-semibold text-brand-700">FoodLens AI</span>
            <Link href="/" className="text-sm text-slate-600 hover:text-brand-600">Upload</Link>
            <Link href="/dataset-builder" className="text-sm text-slate-600 hover:text-brand-600">Dataset Builder</Link>
            <Link href="/evaluation" className="text-sm text-slate-600 hover:text-brand-600">Evaluation</Link>
          </div>
        </nav>
        <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
