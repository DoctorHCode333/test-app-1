# DID Dashboard — Prompt Engineering Plan

## Objective
Build a modern, dark-themed DID (Direct Inward Dialing) Dashboard that integrates with Genesys Cloud Platform API to fetch, display, and categorize all DIDs across the organization — showing assignment status, ownership, and DID pool mappings.

---

## Task 1: Genesys Cloud API Integration

**Prompt:**
> Using the Genesys Cloud Platform Client SDK (`purecloud-platform-client-v2`), implement API functions in `genesysCloudApi.jsx` to:
> - Instantiate `TelephonyProvidersEdgeApi`
> - Create `getDIDs()` — paginated fetch from `GET /api/v2/telephony/providers/edges/dids` with configurable `pageSize`, `pageNumber`, `sortBy`, and `sortOrder`
> - Create `getDIDPools()` — paginated fetch from `GET /api/v2/telephony/providers/edges/didpools` to retrieve all DID pool ranges
> - Create `getAllDIDs()` — orchestrator that fetches all assigned DIDs via pagination, then cross-references DID pool ranges to generate unassigned DID entries. Use a `Set` for O(1) lookup of assigned numbers. Mark synthetic entries with `isUnassigned: true`
> - Create `generatePhoneNumberRange()` — helper using `BigInt` to enumerate all phone numbers between pool start/end boundaries

---

## Task 2: Redux State Management

**Prompt:**
> Extend the existing Redux store with three new slices:
> - `SET_DID_DATA` / `setDIDData` — stores the full DID array
> - `SET_DID_LOADING` / `setDIDLoading` — boolean loading state
> - `SET_DID_ERROR` / `setDIDError` — error message string
>
> Add corresponding reducers (`didDataReducer`, `didLoadingReducer`, `didErrorReducer`) to `reducers.jsx` and register them in `combineReducers`.

---

## Task 3: DID Dashboard UI Component

**Prompt:**
> Build `DID_Dashboard.jsx` with these specifications:
> - **Dark theme** — `bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900` as base
> - **Nav bar** — Centered title "DID Dashboard" with gradient text, phone icon left of title, user avatar (PrimeReact `Avatar`) on the right. Use absolute positioning for true centering
> - **3 Statistics Cards** — Inline row using `grid grid-cols-3` wrapped in `flex justify-center`. Cards use glassmorphism (`backdrop-blur-xl`, semi-transparent backgrounds, gradient borders). Color-coded: Cyan (Total), Emerald (Assigned), Amber (Unassigned). Hover glow effects via `group-hover` transitions
> - **Data Table** — PrimeReact `DataTable` with custom dark theme CSS class `p-datatable-dark`. Columns: Phone Number (cyan mono font), Name, Status (color-coded pill badges), Owner, Owner Type, State, DID Pool (purple). Include global search, assignment filter dropdown, refresh button with gradient styling and padding (`px-5 py-2.5`)
> - **Computed stats** — `useMemo` for statistics and filtered data based on `isUnassigned` flag and `assignmentFilter` state
> - **Loading/Error states** — Centered spinner and error display with retry button

---

## Task 4: Dark Theme CSS

**Prompt:**
> Add `.p-datatable-dark` styles in `index.css` targeting: header, thead, tbody rows (alternating with hover), cells, paginator (gradient active page), dropdowns, and input fields — all using slate color palette with cyan accent borders and focus rings.

---

## Task 5: Routing

**Prompt:**
> Register route `/VOYA_CLIENT_APP/DID_Dashboard` in `App.jsx` pointing to the `DID_Dashboard` component.

---

**Key Design Decisions:** Cross-referencing DIDs API with DID Pools API to surface unassigned numbers • BigInt for phone number range generation • Redux for centralized state • Custom CSS over PrimeReact theme override for full dark-mode control
