import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { fixtureCatalogue } from "@/data/fixture-catalogue";
import { VehicleCard } from "@/components/vehicle-card";
import { ProfileProvider } from "@/profile/profile-provider";

const renderCard = (listing: Parameters<typeof VehicleCard>[0]["listing"]) => render(<ProfileProvider><VehicleCard listing={listing} /></ProfileProvider>);

describe("VehicleCard", () => {
  it("shows transparent evidence and fixture source information", () => {
    const listing = fixtureCatalogue.find((item) => item.conditionEvidence[0].kind === "unknown")!;
    renderCard(listing);

    expect(screen.getByText("Condition not stated")).toBeInTheDocument();
    expect(screen.getByText("Carveo approved fixture")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: new RegExp(listing.title) })).toHaveAttribute("href", `/en-ae/cars/${listing.id}`);
  });

  it("renders the comparable sample size with a deal position", () => {
    const listing = { ...fixtureCatalogue[0], dealPosition: { label: "Below typical" as const, typicalPrice: 280000, differenceAmount: -21000, differencePercent: -8, sampleSize: 6 } };
    renderCard(listing);

    expect(screen.getByText("Below typical")).toBeInTheDocument();
    expect(screen.getByText(/6 comparable listings/)).toBeInTheDocument();
  });

  it("encodes the originating catalogue URL for return navigation", () => {
    const listing = fixtureCatalogue[0];
    render(<ProfileProvider><VehicleCard listing={listing} returnHref="/en-ae/cars?make=Toyota&page=2" /></ProfileProvider>);

    expect(screen.getByRole("link", { name: new RegExp(listing.title) })).toHaveAttribute(
      "href",
      `/en-ae/cars/${listing.id}?from=${encodeURIComponent("/en-ae/cars?make=Toyota&page=2")}`,
    );
  });
});
