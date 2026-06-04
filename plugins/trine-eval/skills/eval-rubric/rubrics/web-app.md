# Web App Evaluation Rubric

## Dimensions and Weights

### Functionality (30%)

| Score | Description |
|-------|-------------|
| 5 | All specified features work flawlessly. Forms validate, navigation completes, state persists across page loads. Edge cases handled. |
| 4 | All core features work. Minor edge cases may be unhandled but don't affect normal usage. |
| 3 | Most features work. One or two features have noticeable bugs that affect usage but have workarounds. |
| 2 | Several features are broken or incomplete. Core user flows are disrupted. |
| 1 | Most features don't work. The application is not usable for its intended purpose. |

### Visual Design (25%)

| Score | Description |
|-------|-------------|
| 5 | Layout is polished and intentional. Typography hierarchy is clear. Spacing is uniform. Fully responsive down to 375px. No overlapping elements. |
| 4 | Layout is clean and consistent. Minor spacing or alignment issues. Responsive with small issues at edge breakpoints. |
| 3 | Layout is functional but unpolished. Some inconsistent spacing or typography. Responsive breaks at some widths. |
| 2 | Layout has significant issues. Overlapping elements, broken alignment, or non-functional at mobile widths. |
| 1 | No intentional layout. Elements are unstyled or randomly positioned. |

### Code Quality (25%)

| Score | Description |
|-------|-------------|
| 5 | Components are modular and well-structured. No duplicated logic. Error states handled. Console clean. Types used correctly (if TypeScript). |
| 4 | Good structure with minor duplication. Most error states handled. Few console warnings. |
| 3 | Reasonable structure. Some code duplication. Some unhandled error states. Console has warnings. |
| 2 | Poor structure. Significant duplication. Many unhandled states. Console errors present. |
| 1 | No structure. Monolithic code. Unhandled exceptions crash the app. |

### Robustness (20%)

| Score | Description |
|-------|-------------|
| 5 | Handles empty states, error states, loading states. Network failures show appropriate messages. No unhandled promise rejections. |
| 4 | Most states handled. Loading states present. One or two edge cases unhandled. |
| 3 | Common states handled. Missing loading indicators or incomplete error handling. |
| 2 | Many unhandled states. Errors crash the UI or show raw error messages. |
| 1 | No state handling. Errors result in white screens or frozen UI. |

## Hard Thresholds

- **No dimension below 2/5.** Any dimension scoring 1 is automatic sprint failure.
- **Functionality below 3/5 is automatic sprint failure** regardless of other scores.

## Testing Tools

- **UI interactions:** Playwright MCP or manual browser testing via dev server
- **Console errors:** Browser developer tools console output
- **Network requests:** Browser network tab or curl for API calls
- **Responsive design:** Resize browser window to 375px, 768px, 1024px widths
- **State persistence:** Reload the page and verify data persists
