# Frontend UI design discussion

Status: approved and implemented; verification outcomes are recorded in the companion implementation plan.

## Agreed direction

- Primary outcome: make choosing a car easier for buyers.
- Meaning of “more dynamic”: fluid interactions and subtle motion.
- Evaluate visual changes by how they help buyers browse, narrow options, and compare cars.
- Initial scope: browsing, filters, vehicle details, and comparison.
- Visual direction: refine the existing black-and-yellow identity.
- Screen priority: mobile first, with a fully considered desktop layout.
- Vehicle cards: emphasize photo, price, model/year, mileage, and location, with a compact deal indicator. Place detailed evidence on the vehicle detail page.
- Filters: update results immediately on desktop. On mobile, use a filter sheet with an explicit Show results action, keeping the list stable while buyers select filters.
- Comparison access: show a compact sticky tray after the first car is selected; display selected cars and provide remove and open-comparison actions.
- Vehicle detail: lead with photos and essential facts, followed by price context, condition, and source evidence. Keep Save and Compare easily accessible on mobile.
- Comparison hierarchy: highlight differences in price, mileage, year, and condition. Make matching information visually quieter and mark missing information explicitly.
- Motion: use short, subtle transitions for filters, selection, and the comparison tray. Preserve scroll position during updates, avoid replaying entrance animations, and respect reduced-motion preferences.

## Consolidated design

Retain Carveo's angular automotive character and black-and-yellow palette. Improve visual appeal through clearer typography hierarchy, more consistent spacing, prominent vehicle photography, and selective yellow accents on primary actions and selected states. The separate violet/glass Authkit reference does not guide this redesign.

The first pass covers the existing browsing-to-comparison journey. Shared vehicle-card improvements can appear wherever those cards are reused; redesigning the homepage composition is outside this first pass.

Desktop filters commit each change immediately; mobile filters maintain draft selections until Show results is activated. Closing without applying leaves current results unchanged. Result updates need clear loading feedback and protection against older responses replacing newer selections.

The comparison tray must fit small screens and avoid covering page content or the detail page's Save and Compare controls. Existing comparison limits and saved-selection behavior remain constraints to inspect during implementation.

## Proposed acceptance checks

- Buyers can browse, filter, inspect a vehicle, select cars, remove selections, and compare on mobile and desktop.
- Card essentials remain readable at narrow widths; controls do not overlap or cause unintended horizontal page scrolling.
- Desktop filters update without an Apply step; mobile changes affect results only after Show results.
- Result updates preserve scroll position and communicate loading, empty, and error states without misleading stale content.
- Comparison highlights available differences and labels unavailable values without implying that missing evidence is positive evidence.
- Sticky controls remain accessible without obscuring content or each other.
- Keyboard focus, accessible control names, contrast, and reduced-motion behavior are verified.
- Transitions provide feedback without delaying actions or replaying decorative entrances on result updates.

## Documentation disposition

This brief records product and visual design choices. No new domain-specific glossary terms were introduced. No architectural decision requiring an ADR has been established; implementation should assess any consequential trade-off when it arises.
