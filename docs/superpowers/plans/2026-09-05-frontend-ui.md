# Frontend UI Implementation Plan

> **For agentic workers:** Use executing-plans or subagent-driven-development to implement task-by-task. Track completed steps below.

**Goal:** Make choosing a car easier through clearer visual hierarchy and responsive interaction.
**Architecture:** Retain server-rendered catalogue pages and existing repository/profile contracts. Isolate filter navigation in client components; preserve URL state and use Next navigation transitions. Reuse the existing profile selection store for a responsive comparison tray.
**Tech Stack:** Next.js 16, React 19, Tailwind 4, Base UI, Vitest, Playwright.
**Spec:** ../specs/2026-09-05-frontend-ui-design-discussion.md

## Global constraints

- Mobile first, with a fully considered desktop layout.
- Refine the existing black-and-yellow identity.
- Preserve scroll position during updates, avoid replaying entrance animations, and respect reduced-motion preferences.
- Preserve existing backend changes and catalogue/profile contracts.
- Preserve truthful fixture and condition disclosures without cluttering vehicle cards.

## Task 1: Responsive browsing and filters

Files: `frontend/src/app/en-ae/cars/page.tsx`, `frontend/src/components/filter-fields.tsx`, `frontend/src/components/mobile-filter-drawer.tsx`; new client filter/navigation components and focused tests as needed.

- [x] Test desktop change navigation without Apply, mobile draft cancellation/application, and preservation of sort/view/unrendered query values.
- [x] Implement client navigation with `router.replace(href, { scroll: false })` inside a transition. Checkboxes/selects update immediately; text input uses a short debounce. Clear timers on teardown. Keep server search authoritative.
- [x] Present pending status and prevent stale-result interaction while navigation is pending. Mobile drawer retains explicit Show results and discards unapplied drafts on close.
- [x] Improve browse heading, responsive toolbar, filter grouping, reset affordance and result summary; preserve query params in view/pagination links.
- [x] Verify focused tests and type checking.

## Task 2: Vehicle presentation and persistent selection

Files: `vehicle-card.tsx`, `deal-position.tsx`, `compare-button.tsx`, `shortlist-button.tsx`, `compare-tray.tsx`, detail page and `globals.css` under `frontend/src`.

- [x] Refine cards with larger price typography, uncluttered essentials, compact deal position and direct detail affordance. Support a true horizontal list presentation on desktop.
- [x] Add accessible pressed states to selection controls. Test removing selections from the tray at mobile widths.
- [x] Show selected vehicle names from supplied catalogue data, with an honest fallback for unavailable records; retain four-car limit and removal access on every screen size.
- [x] Improve detail typography and gallery presentation. Combine mobile detail actions with the comparison tray so fixed controls cannot overlap.
- [x] Add restrained transform/opacity transitions, fine-pointer hover treatment, keyboard focus styling, safe-area spacing, and reduced-motion overrides.

## Task 3: Comparison clarity

Files: `frontend/src/components/comparison-workspace.tsx` and its existing tests; comparison page.

- [x] Test priority order and unknown-condition handling in comparison rows.
- [x] Lead with price, mileage, year and condition. Mark differences with a subtle signal tint and text indicator; mute equal attributes. Maintain differences-only control.
- [x] Make mobile comparison directly comparable with a contained horizontally scrolling table and clear navigation cue; preserve removal and empty-state recovery.

## Task 4: Verification and review

- [x] Run frontend unit tests and type checking.
- [~] Exercise browse/filter/detail/compare on desktop and mobile with fixture-backed Playwright tests; in-app browser checks covered the journeys and no-overflow/focus behavior. The sandboxed Playwright runtime denied access to `localhost`, so its full run could not execute here.
- [x] Capture and inspect representative desktop, 390px mobile, comparison, and 320px detail screenshots in the in-app browser.
- [x] Request independent code review and resolve material findings.
- [x] Run `graphify update .` with the existing `uv` environment at 01:35 Cairo: AST-only refresh of 100 code files, 1,757 nodes, and 3,891 edges. No installation was needed; the run created the dated `2026-09-06` graph backup and `.graphify_python` marker.

## Progress

Implementation and review are complete. Existing unrelated backend changes remain preserved. Browser coverage was completed in the in-app browser; the sandboxed Playwright runner's local-network restriction is documented above.

## Verification record — 2026-09-06

- `bun --cwd frontend vitest run`: 21 files and 69 tests passed.
- `bun --cwd frontend --bun tsc --noEmit --incremental false`: completed successfully.
- The fixture-backed frontend production build completed successfully.
- `bun --cwd frontend playwright test --list`: discovered 16 browser tests. The complete browser run was not executed because this environment denies Playwright access to the local fixture server (`ERR_NETWORK_ACCESS_DENIED`).
- Desktop, 390px mobile, comparison, 320px detail, filter, and comparison-tray journeys were inspected in the in-app browser. No horizontal overflow was observed; gallery and control focus behavior were checked there. Reduced-motion CSS was reviewed in source, but real browser media emulation was unavailable in this environment.
