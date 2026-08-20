import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ConditionEvidencePanel } from "@/components/condition-evidence";

describe("ConditionEvidencePanel", () => {
  it("keeps unknown evidence distinct from positive and warning claims", () => {
    render(<ConditionEvidencePanel evidence={[
      { kind: "positive", label: "Service history stated", detail: "Source says records exist." },
      { kind: "warning", label: "Repair stated", detail: "Bumper repaint stated." },
      { kind: "unknown", label: "Inspection not stated", detail: "No inspection evidence." },
    ]} />);

    expect(screen.getByRole("heading", { name: "Source-stated positives" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Warnings" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Unknown" })).toBeInTheDocument();
    expect(screen.queryByText(/verified/i)).not.toBeInTheDocument();
  });
});
