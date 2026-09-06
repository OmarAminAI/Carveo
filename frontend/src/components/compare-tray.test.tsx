import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { ProfileProvider } from "@/profile/profile-provider";
import { CompareTray } from "@/components/compare-tray";
import { CompareButton } from "@/components/compare-button";
import { fixtureCatalogue } from "@/data/fixture-catalogue";

vi.mock("@clerk/nextjs", () => ({ useAuth: () => ({ isLoaded: true, isSignedIn: false }) }));
afterEach(cleanup);
beforeEach(() => localStorage.clear());

it("identifies selected cars and removes them through the tray", async () => {
  const car = fixtureCatalogue[0];
  const user = userEvent.setup();
  render(<ProfileProvider><CompareButton listingId={car.id} /><CompareTray listings={[car]} /></ProfileProvider>);
  await user.click(screen.getByRole("button", { name: "Compare" }));
  expect(screen.getByRole("button", { name: "Added" })).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByText(`${car.year} ${car.make} ${car.model}`)).toBeVisible();
  await user.click(screen.getByRole("button", { name: `Remove ${car.year} ${car.make} ${car.model} from comparison` }));
  expect(screen.queryByRole("complementary", { name: "Selected cars" })).not.toBeInTheDocument();
});
