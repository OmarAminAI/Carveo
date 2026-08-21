import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

vi.mock("@clerk/nextjs", () => ({
  Show: ({ children, when }: { children: React.ReactNode; when: string }) => (
    <div data-testid={`auth-${when}`}>{children}</div>
  ),
  SignInButton: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  SignUpButton: ({ children }: { children: React.ReactNode }) => <>{children}</>,
  UserButton: () => <button aria-label="User account" />,
}));

import { AuthControls } from "@/components/auth-controls";

describe("AuthControls", () => {
  it("offers clear account actions to signed-out buyers", () => {
    render(<AuthControls />);

    const signedOut = screen.getByTestId("auth-signed-out");
    expect(signedOut).toHaveTextContent("Sign in");
    expect(signedOut).toHaveTextContent("Create account");
  });

  it("shows the account menu to signed-in buyers", () => {
    render(<AuthControls />);

    expect(screen.getByTestId("auth-signed-in")).toContainElement(
      screen.getByRole("button", { name: "User account" }),
    );
  });
});
