# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend.spec.ts >> CME Page >> FP-009: CME Velocity card shows speed in km/s
- Location: tests\frontend.spec.ts:122:7

# Error details

```
Test timeout of 30000ms exceeded while running "beforeEach" hook.
```

```
Error: page.goto: Test timeout of 30000ms exceeded.
Call log:
  - navigating to "http://localhost:3000/cme", waiting until "load"

```

# Page snapshot

```yaml
- generic [active] [ref=e1]:
  - navigation [ref=e3]:
    - generic [ref=e4]:
      - link "Overview" [ref=e5] [cursor=pointer]:
        - /url: /
        - button "Overview" [ref=e6]:
          - generic [ref=e8]: Overview
      - link "Solar Flare" [ref=e9] [cursor=pointer]:
        - /url: /solar-flare
        - button "Solar Flare" [ref=e10]:
          - generic [ref=e12]: Solar Flare
      - link "CME" [ref=e13] [cursor=pointer]:
        - /url: /cme
        - button "CME" [ref=e14]:
          - generic [ref=e16]: CME
      - link "Solar Wind" [ref=e17] [cursor=pointer]:
        - /url: /solar-wind
        - button "Solar Wind" [ref=e18]:
          - generic [ref=e20]: Solar Wind
      - link "SEP" [ref=e21] [cursor=pointer]:
        - /url: /sep
        - button "SEP" [ref=e22]:
          - generic [ref=e24]: SEP
      - link "LLM" [ref=e25] [cursor=pointer]:
        - /url: /llm
        - button "LLM" [ref=e26]:
          - generic [ref=e28]: LLM
  - main [ref=e29]:
    - heading "CME" [level=1] [ref=e31]
    - generic [ref=e32]:
      - generic [ref=e36]:
        - generic [ref=e37]: "01"
        - heading "CME Velocity" [level=2] [ref=e38]
        - generic [ref=e40]:
          - paragraph [ref=e41]: Coronal Mass Ejections are massive eruptions of plasma and magnetic field from the Sun's corona.
          - paragraph [ref=e42]: Loading CME data...
      - generic [ref=e47]:
        - generic [ref=e48]: "02"
        - heading "Magnetic Structure" [level=2] [ref=e49]
        - generic [ref=e50]:
          - paragraph [ref=e52]: The magnetic structure determines how the CME interacts with Earth's magnetosphere.
          - paragraph [ref=e54]: Loading...
      - generic [ref=e59]:
        - generic [ref=e60]: "03"
        - heading "Impact Probability" [level=2] [ref=e61]
        - generic [ref=e62]:
          - paragraph [ref=e64]: Impact probability depends on CME trajectory, angular width, and speed relative to the Sun-Earth line.
          - paragraph [ref=e66]: Loading...
      - generic [ref=e71]:
        - generic [ref=e72]: "04"
        - heading "CME Coronagraph Image" [level=2] [ref=e73]
        - generic [ref=e74]:
          - paragraph [ref=e76]: LASCO coronagraph blocks the bright solar disk to reveal faint coronal structures and CMEs propagating outward.
          - img "LASCO CME Coronagraph" [ref=e78]
      - generic [ref=e83]:
        - generic [ref=e84]: "05"
        - heading "CME Event Log" [level=2] [ref=e85]
        - generic [ref=e86]:
          - generic [ref=e87]:
            - generic [ref=e88]: ID
            - generic [ref=e89]: Time
            - generic [ref=e90]: Speed
            - generic [ref=e91]: Type
            - generic [ref=e92]: Location
            - generic [ref=e93]: Risk
          - paragraph [ref=e95]: Loading CME events...
  - button "Open Next.js Dev Tools" [ref=e102] [cursor=pointer]:
    - img [ref=e103]
  - alert [ref=e106]
```

# Test source

```ts
  18  | // ═══════════════════════════════════════════════════════════════════════════════
  19  | 
  20  | test.describe("Home Page", () => {
  21  |   test("FP-001: Home page renders STELAR hero text", async ({ page }) => {
  22  |     await page.goto(FE);
  23  |     const heading = page.locator("h1");
  24  |     await expect(heading).toContainText("STELAR");
  25  |     console.log(`[FP-001] h1 text: "${await heading.textContent()}"`);
  26  |   });
  27  | 
  28  |   test("FP-002: Starfield canvas background renders", async ({ page }) => {
  29  |     await page.goto(FE);
  30  |     const canvas = page.locator("canvas");
  31  |     const count = await canvas.count();
  32  |     console.log(`[FP-002] Canvas elements found: ${count}`);
  33  |     expect(count).toBeGreaterThan(0);
  34  |   });
  35  | 
  36  |   test("FP-003: Navbar / nav links visible", async ({ page }) => {
  37  |     await page.goto(FE);
  38  |     const nav = page.locator("nav, header");
  39  |     await expect(nav.first()).toBeVisible();
  40  |     console.log(`[FP-003] Nav element visible: true`);
  41  |   });
  42  | });
  43  | 
  44  | 
  45  | // ═══════════════════════════════════════════════════════════════════════════════
  46  | //  SOLAR FLARE PAGE  (FP-004 to FP-008)
  47  | // ═══════════════════════════════════════════════════════════════════════════════
  48  | 
  49  | test.describe("Solar Flare Page", () => {
  50  |   test.beforeEach(async ({ page }) => {
  51  |     await page.goto(`${FE}/solar-flare`);
  52  |   });
  53  | 
  54  |   test("FP-004: Magnetogram image card renders", async ({ page }) => {
  55  |     // The magnetogram card contains an img pointing to the backend
  56  |     const img = page.locator("img[src*='magnetogram']").first();
  57  |     await expect(img).toBeVisible({ timeout: 20000 });
  58  |     const src = await img.getAttribute("src");
  59  |     console.log(`[FP-004] Magnetogram img src: ${src}`);
  60  |     expect(src).toContain("magnetogram");
  61  |   });
  62  | 
  63  |   test("FP-005: GOES X-ray Flux Plotly chart renders", async ({ page }) => {
  64  |     // Plotly renders a <div class="plotly-graph-div">
  65  |     const chart = page.locator(".plotly-graph-div, .js-plotly-plot").first();
  66  |     await expect(chart).toBeVisible({ timeout: 20000 });
  67  |     console.log(`[FP-005] Plotly chart visible: true`);
  68  |   });
  69  | 
  70  |   test("FP-006: AIA EUV wavelength selector — all 4 options clickable", async ({ page }) => {
  71  |     const wavelengths = ["94Å", "131Å", "171Å", "193Å"];
  72  |     for (const wl of wavelengths) {
  73  |       const btn = page.locator(`button:has-text("${wl}"), [data-wavelength="${wl}"]`).first();
  74  |       const btnByText = page.getByText(wl, { exact: true }).first();
  75  |       const target = (await btn.count()) > 0 ? btn : btnByText;
  76  |       if (await target.count() > 0) {
  77  |         await target.click();
  78  |         console.log(`[FP-006] Clicked wavelength: ${wl}`);
  79  |         await page.waitForTimeout(500);
  80  |       } else {
  81  |         console.log(`[FP-006] Wavelength button "${wl}" not found — may be inside scroll`);
  82  |       }
  83  |     }
  84  |   });
  85  | 
  86  |   test("FP-007: Recent Flare Events table renders columns", async ({ page }) => {
  87  |     // Scroll into section with flare events table
  88  |     await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  89  |     await page.waitForTimeout(2000);
  90  |     const classCol = page.getByText("Class", { exact: false }).first();
  91  |     const peakCol = page.getByText("Peak", { exact: false }).first();
  92  |     console.log(`[FP-007] 'Class' column visible: ${await classCol.isVisible()}`);
  93  |     console.log(`[FP-007] 'Peak' column visible: ${await peakCol.isVisible()}`);
  94  |     expect(await classCol.isVisible() || await peakCol.isVisible()).toBeTruthy();
  95  |   });
  96  | 
  97  |   test("FP-008: X-class flare badge shows red color", async ({ page }) => {
  98  |     // Check that any badge containing X has red styling
  99  |     const xBadge = page.locator("span").filter({ hasText: /^X/ }).first();
  100 |     if (await xBadge.count() > 0) {
  101 |       const cls = await xBadge.getAttribute("class") ?? "";
  102 |       console.log(`[FP-008] X-class badge class: "${cls}"`);
  103 |       expect(cls).toContain("red");
  104 |     } else {
  105 |       console.log(`[FP-008] No X-class flares in current data — skipping badge color check`);
  106 |       test.skip();
  107 |     }
  108 |   });
  109 | });
  110 | 
  111 | 
  112 | // ═══════════════════════════════════════════════════════════════════════════════
  113 | //  CME PAGE  (FP-009 to FP-013)
  114 | // ═══════════════════════════════════════════════════════════════════════════════
  115 | 
  116 | test.describe("CME Page", () => {
  117 |   test.beforeEach(async ({ page }) => {
> 118 |     await page.goto(`${FE}/cme`);
      |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  119 |     await page.waitForTimeout(2000);
  120 |   });
  121 | 
  122 |   test("FP-009: CME Velocity card shows speed in km/s", async ({ page }) => {
  123 |     const kms = page.getByText("km/s").first();
  124 |     await expect(kms).toBeVisible({ timeout: 15000 });
  125 |     const label = await kms.textContent();
  126 |     console.log(`[FP-009] km/s label visible: "${label}"`);
  127 |   });
  128 | 
  129 |   test("FP-010: Magnetic Structure card shows Type field", async ({ page }) => {
  130 |     const typeLabel = page.getByText("Type").first();
  131 |     await expect(typeLabel).toBeVisible({ timeout: 15000 });
  132 |     console.log(`[FP-010] 'Type' field visible: true`);
  133 |   });
  134 | 
  135 |   test("FP-011: Impact Probability bar chart shows High/Moderate/Low", async ({ page }) => {
  136 |     await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
  137 |     await page.waitForTimeout(1500);
  138 |     const high = page.getByText("High").first();
  139 |     const low  = page.getByText("Low").first();
  140 |     console.log(`[FP-011] High visible: ${await high.isVisible()} | Low visible: ${await low.isVisible()}`);
  141 |     expect(await high.isVisible() || await low.isVisible()).toBeTruthy();
  142 |   });
  143 | 
  144 |   test("FP-012: CME Coronagraph image loads", async ({ page }) => {
  145 |     const img = page.locator("img[src*='cme'], img[src*='soho'], img[src*='nascom']").first();
  146 |     await expect(img).toBeVisible({ timeout: 20000 });
  147 |     const src = await img.getAttribute("src");
  148 |     console.log(`[FP-012] Coronagraph img src: ${src}`);
  149 |     expect(src).toBeTruthy();
  150 |   });
  151 | 
  152 |   test("FP-013: CME Event Log table shows Speed column", async ({ page }) => {
  153 |     await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  154 |     await page.waitForTimeout(1500);
  155 |     const speedCol = page.getByText("Speed", { exact: false }).first();
  156 |     const riskCol  = page.getByText("Risk",  { exact: false }).first();
  157 |     console.log(`[FP-013] Speed col visible: ${await speedCol.isVisible()} | Risk col visible: ${await riskCol.isVisible()}`);
  158 |     expect(await speedCol.isVisible() || await riskCol.isVisible()).toBeTruthy();
  159 |   });
  160 | });
  161 | 
  162 | 
  163 | // ═══════════════════════════════════════════════════════════════════════════════
  164 | //  SEP PAGE  (FP-014 to FP-017)
  165 | // ═══════════════════════════════════════════════════════════════════════════════
  166 | 
  167 | test.describe("SEP Page", () => {
  168 |   test.beforeEach(async ({ page }) => {
  169 |     await page.goto(`${FE}/sep`);
  170 |   });
  171 | 
  172 |   test("FP-014: Proton Flux stat card renders with pfu unit", async ({ page }) => {
  173 |     await waitForNoSkeleton(page);
  174 |     const pfu = page.getByText("pfu").first();
  175 |     await expect(pfu).toBeVisible({ timeout: 15000 });
  176 |     const protonTitle = page.getByText("Proton Flux", { exact: false }).first();
  177 |     console.log(`[FP-014] 'pfu' visible: true | 'Proton Flux' visible: ${await protonTitle.isVisible()}`);
  178 |   });
  179 | 
  180 |   test("FP-015: Radiation Risk by Mission Type shows 3 cards", async ({ page }) => {
  181 |     await waitForNoSkeleton(page);
  182 |     const crew      = page.getByText("Crew", { exact: false }).first();
  183 |     const satellite = page.getByText("Satellite", { exact: false }).first();
  184 |     const deep      = page.getByText("Deep Space", { exact: false }).first();
  185 |     console.log(`[FP-015] Crew: ${await crew.isVisible()} | Satellite: ${await satellite.isVisible()} | DeepSpace: ${await deep.isVisible()}`);
  186 |     expect(await crew.isVisible()).toBeTruthy();
  187 |     expect(await satellite.isVisible()).toBeTruthy();
  188 |     expect(await deep.isVisible()).toBeTruthy();
  189 |   });
  190 | 
  191 |   test("FP-016: Risk Level card shows current risk level text", async ({ page }) => {
  192 |     await waitForNoSkeleton(page);
  193 |     const validLevels = ["quiet", "low", "moderate", "high", "severe", "extreme"];
  194 |     let found = false;
  195 |     for (const lvl of validLevels) {
  196 |       const el = page.getByText(lvl, { exact: false }).first();
  197 |       if (await el.isVisible()) {
  198 |         console.log(`[FP-016] Risk level shown: "${lvl}"`);
  199 |         found = true;
  200 |         break;
  201 |       }
  202 |     }
  203 |     expect(found).toBeTruthy();
  204 |   });
  205 | 
  206 |   test("FP-017: Data refreshes — last updated timestamp visible", async ({ page }) => {
  207 |     await waitForNoSkeleton(page);
  208 |     const updated = page.getByText("Last updated", { exact: false }).first();
  209 |     await expect(updated).toBeVisible({ timeout: 15000 });
  210 |     const text = await updated.textContent();
  211 |     console.log(`[FP-017] Last updated text: "${text}"`);
  212 |   });
  213 | });
  214 | 
  215 | 
  216 | // ═══════════════════════════════════════════════════════════════════════════════
  217 | //  SOLAR WIND PAGE  (FP-018 to FP-020)
  218 | // ═══════════════════════════════════════════════════════════════════════════════
```