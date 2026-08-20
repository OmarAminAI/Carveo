import type { Metadata } from "next";
import { AssistantWorkspace } from "@/components/assistant-workspace";

export const metadata: Metadata = { title: "AI car search", description: "Describe the UAE used car you need and edit the interpreted search requirements." };

export default async function FindPage({ searchParams }: { searchParams: Promise<{ prompt?: string }> }) {
  const { prompt = "" } = await searchParams;
  return <main><AssistantWorkspace initialPrompt={prompt} /></main>;
}
