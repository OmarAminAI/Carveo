import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { BrowseLink, BrowseNavigation, BrowseResults, BrowseSort, FilterForm } from "./browse-navigation";
import { MobileFilterDrawer } from "./mobile-filter-drawer";
import { parseListingQuery } from "@/domain/query";
const { replace } = vi.hoisted(() => ({ replace: vi.fn() }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ replace }) }));
const current = "model=Camry&sort=lowest-price&view=list&pageSize=24&page=3";
const query = parseListingQuery(new URLSearchParams(current));
afterEach(() => { cleanup(); vi.resetAllMocks(); vi.useRealTimers(); });
describe("responsive filters", () => {
  it("updates desktop checkbox filters immediately while retaining other URL choices", () => {
    render(<BrowseNavigation><FilterForm query={query} currentParams={current} /></BrowseNavigation>);
    fireEvent.click(screen.getByLabelText("Toyota"));
    const params = new URL(replace.mock.calls[0][0], "https://carveo.test").searchParams;
    expect(Object.fromEntries(params)).toMatchObject({ make: "Toyota", model: "Camry", sort: "lowest-price", view: "list", pageSize: "24" });
    expect(params.has("page")).toBe(false);
    expect(replace.mock.calls[0][1]).toEqual({ scroll: false });
  });
  it("updates sort without Apply and preserves the current view and filters", () => {
    render(<BrowseNavigation><BrowseSort sort={query.sort} currentParams={current} /></BrowseNavigation>);
    fireEvent.change(screen.getByLabelText("Sort"), { target: { value: "newest" } });
    expect(Object.fromEntries(new URL(replace.mock.calls[0][0], "https://carveo.test").searchParams)).toEqual({ model: "Camry", sort: "newest", view: "list", pageSize: "24" });
  });
  it("cancels queued typing when another control starts navigation", async () => {
    vi.useFakeTimers();
    let finish!: () => void;
    replace.mockImplementationOnce(() => new Promise<void>((resolve) => { finish = resolve; }));
    render(<BrowseNavigation><FilterForm query={query} currentParams={current} /><BrowseSort sort={query.sort} currentParams={current} /></BrowseNavigation>);
    fireEvent.change(screen.getByPlaceholderText("Model, trim or city"), { target: { value: "Camry" } });
    fireEvent.change(screen.getByLabelText("Sort"), { target: { value: "newest" } });
    act(() => vi.advanceTimersByTime(400));
    expect(replace).toHaveBeenCalledTimes(1);
    await act(async () => finish());
  });
  it.each(["view=grid&page=3", "view=list&page=2"])("routes %s through the shared transition and cancels typing before navigation starts", async (destination) => {
    vi.useFakeTimers();
    let finish!: () => void;
    replace.mockImplementationOnce(() => {
      // Exercise the synchronous boundary before React can flush pending effects.
      vi.advanceTimersByTime(400);
      return new Promise<void>((resolve) => { finish = resolve; });
    });
    render(<BrowseNavigation><FilterForm query={query} currentParams={current} /><BrowseLink params={destination}>Change results</BrowseLink></BrowseNavigation>);
    fireEvent.change(screen.getByPlaceholderText("Model, trim or city"), { target: { value: "Camry" } });
    fireEvent.click(screen.getByRole("link", { name: "Change results" }));
    const calls = [...replace.mock.calls];
    await act(async () => finish());
    expect(calls).toEqual([[`/en-ae/cars?${destination}`, { scroll: false }]]);
  });
  it("prevents view navigation from replacing pending filters with stale query state", async () => {
    let finish!: () => void;
    replace.mockImplementationOnce(() => new Promise<void>((resolve) => { finish = resolve; }));
    render(<BrowseNavigation><FilterForm query={query} currentParams={current} /><BrowseLink params="view=grid">Grid view</BrowseLink></BrowseNavigation>);
    fireEvent.click(screen.getByLabelText("Toyota"));
    const viewControl = screen.getByText("Grid view");
    expect(viewControl).toHaveAttribute("aria-disabled", "true");
    fireEvent.click(viewControl);
    await act(async () => finish());
    expect(replace).toHaveBeenCalledTimes(1);
    expect(replace.mock.calls[0][0]).toContain("make=Toyota");
  });
  it("blocks stale result interaction while a navigation is pending", async () => {
    let finish!: () => void;
    replace.mockImplementationOnce(() => new Promise<void>((resolve) => { finish = resolve; }));
    render(<BrowseNavigation><FilterForm query={query} currentParams={current} /><BrowseResults summary="12 cars"><a href="/car">Open car</a></BrowseResults></BrowseNavigation>);
    fireEvent.click(screen.getByLabelText("Toyota"));
    expect(screen.getByRole("region", { name: "Car results" })).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Open car").parentElement).toHaveAttribute("inert");
    await act(async () => finish());
    expect(screen.getByRole("status")).toHaveTextContent("12 cars");
    expect(screen.getByText("Open car").parentElement).not.toHaveAttribute("inert");
  });
  it("retains filter values that have no visible control", () => {
    const params = "make=Audi&model=A4&view=list";
    render(<BrowseNavigation><FilterForm query={parseListingQuery(new URLSearchParams(params))} currentParams={params} /></BrowseNavigation>);
    fireEvent.click(screen.getByLabelText("Toyota"));
    expect(new URL(replace.mock.calls[0][0], "https://carveo.test").searchParams.getAll("make")).toEqual(["Audi", "Toyota"]);
  });
  it("debounces typing and cancels a queued change when the authoritative URL changes", () => {
    vi.useFakeTimers();
    const { rerender } = render(<BrowseNavigation><FilterForm key={current} query={query} currentParams={current} /></BrowseNavigation>);
    fireEvent.change(screen.getByPlaceholderText("Model, trim or city"), { target: { value: "Camry" } });
    expect(replace).not.toHaveBeenCalled();
    act(() => vi.advanceTimersByTime(400));
    expect(replace.mock.calls[0][0]).toContain("q=Camry");
    fireEvent.change(screen.getByPlaceholderText("Model, trim or city"), { target: { value: "Toyota" } });
    rerender(<BrowseNavigation><FilterForm key="back" query={parseListingQuery(new URLSearchParams())} currentParams="" /></BrowseNavigation>);
    act(() => vi.advanceTimersByTime(400));
    expect(replace).toHaveBeenCalledTimes(1);
    expect(screen.getByPlaceholderText("Model, trim or city")).toHaveValue("");
  });
  it("keeps mobile changes as drafts, discards them on close and applies only on submit", async () => {
    render(<BrowseNavigation><MobileFilterDrawer query={query} currentParams={current} /></BrowseNavigation>);
    fireEvent.click(screen.getByRole("button", { name: "Filters" }));
    fireEvent.click(await screen.findByLabelText("Toyota"));
    expect(replace).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Close filters" }));
    fireEvent.click(screen.getByRole("button", { name: "Filters" }));
    expect(await screen.findByLabelText("Toyota")).not.toBeChecked();
    fireEvent.click(screen.getByLabelText("Nissan"));
    fireEvent.click(screen.getByRole("button", { name: "Show results" }));
    const params = new URL(replace.mock.calls[0][0], "https://carveo.test").searchParams;
    expect(params.get("make")).toBe("Nissan");
    expect(params.get("model")).toBe("Camry");
    expect(params.get("view")).toBe("list");
    expect(params.has("page")).toBe(false);
  });
});
