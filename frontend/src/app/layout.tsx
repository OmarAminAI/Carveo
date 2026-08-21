import { ClerkProvider } from "@clerk/nextjs";
import { shadcn } from "@clerk/ui/themes";
import type { Metadata } from "next";
import "@fontsource/barlow-condensed/500.css";
import "@fontsource/barlow-condensed/600.css";
import "geist/font/sans";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Carveo", template: "%s | Carveo" },
  description: "Search and compare used cars across the UAE.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" dir="ltr" data-scroll-behavior="smooth">
      <body>
        <ClerkProvider appearance={{ theme: shadcn }}>{children}</ClerkProvider>
      </body>
    </html>
  );
}
