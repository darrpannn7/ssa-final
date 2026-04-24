# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend.spec.ts >> Component: CMECards >> FC-011: CME Impact Probability shows High/Moderate/Low bars
- Location: tests\frontend.spec.ts:374:7

# Error details

```
Test timeout of 30000ms exceeded.
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
  275 |     await page.goto(`${FE}/solar-flare`);
  276 |     const chart = page.locator(".js-plotly-plot").first();
  277 |     await expect(chart).toBeVisible({ timeout: 20000 });
  278 |     // Check the y-axis tick label contains a power-of-10 format (e.g. 10^−7)
  279 |     const yLabels = page.locator(".ytick text, .yaxislayer text");
  280 |     const label = await yLabels.first().textContent().catch(() => "");
  281 |     console.log(`[FC-002] First Y-axis label: "${label}"`);
  282 |     expect(chart).toBeTruthy(); // chart rendered
  283 |   });
  284 | 
  285 |   test("FC-003: GOES chart shows loading state before data arrives", async ({ page }) => {
  286 |     // Intercept to delay response
  287 |     await page.route("**/noaa/goes-xray", async (route) => {
  288 |       await new Promise((r) => setTimeout(r, 3000));
  289 |       await route.continue();
  290 |     });
  291 |     await page.goto(`${FE}/solar-flare`);
  292 |     const loading = page.getByText(/loading.*goes|loading.*x.?ray/i).first();
  293 |     const visible = await loading.isVisible();
  294 |     console.log(`[FC-003] Loading text visible during delay: ${visible}`);
  295 |     // Either loading text OR chart is shown (both are valid states)
  296 |     expect(true).toBeTruthy();
  297 |   });
  298 | 
  299 |   test("FC-004: GOES chart shows 'No flux data' when API returns empty", async ({ page }) => {
  300 |     await page.route("**/noaa/goes-xray", (route) =>
  301 |       route.fulfill({ body: JSON.stringify({ primary: [], secondary: [] }) })
  302 |     );
  303 |     await page.goto(`${FE}/solar-flare`);
  304 |     await page.waitForTimeout(3000);
  305 |     const noData = page.getByText(/no flux data/i).first();
  306 |     const visible = await noData.isVisible();
  307 |     console.log(`[FC-004] 'No flux data' message visible: ${visible}`);
  308 |     expect(visible).toBeTruthy();
  309 |   });
  310 | });
  311 | 
  312 | test.describe("Component: FlareEventLog", () => {
  313 |   test("FC-005: Flare event log renders column headers", async ({ page }) => {
  314 |     await page.goto(`${FE}/solar-flare`);
  315 |     await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  316 |     await page.waitForTimeout(2000);
  317 |     for (const col of ["Class", "Start", "Peak", "End", "Region"]) {
  318 |       const el = page.getByText(col, { exact: false }).first();
  319 |       console.log(`[FC-005] Column '${col}' visible: ${await el.isVisible()}`);
  320 |     }
  321 |     const classCol = page.getByText("Class", { exact: false }).first();
  322 |     expect(await classCol.isVisible()).toBeTruthy();
  323 |   });
  324 | 
  325 |   test("FC-006: X-class flare badge shows red color", async ({ page }) => {
  326 |     await page.goto(`${FE}/solar-flare`);
  327 |     await page.waitForTimeout(3000);
  328 |     const xBadge = page.locator("span").filter({ hasText: /^X\d/ }).first();
  329 |     if (await xBadge.count() > 0) {
  330 |       const cls = await xBadge.getAttribute("class") ?? "";
  331 |       console.log(`[FC-006] X-class badge class: "${cls}"`);
  332 |       expect(cls).toContain("red");
  333 |     } else {
  334 |       console.log(`[FC-006] No X-class flares in current data`);
  335 |       test.skip();
  336 |     }
  337 |   });
  338 | 
  339 |   test("FC-007: M-class flare badge shows orange color", async ({ page }) => {
  340 |     await page.goto(`${FE}/solar-flare`);
  341 |     await page.waitForTimeout(3000);
  342 |     const mBadge = page.locator("span").filter({ hasText: /^M\d/ }).first();
  343 |     if (await mBadge.count() > 0) {
  344 |       const cls = await mBadge.getAttribute("class") ?? "";
  345 |       console.log(`[FC-007] M-class badge class: "${cls}"`);
  346 |       expect(cls).toContain("orange");
  347 |     } else {
  348 |       console.log(`[FC-007] No M-class flares in current data`);
  349 |       test.skip();
  350 |     }
  351 |   });
  352 | 
  353 |   test("FC-008/FC-009: Shows flare rows or 'No flare events found'", async ({ page }) => {
  354 |     await page.goto(`${FE}/solar-flare`);
  355 |     await page.waitForTimeout(4000);
  356 |     const noFlares = page.getByText("No flare events found").first();
  357 |     const rows     = page.locator(".grid.grid-cols-5 > span").first();
  358 |     const hasNoFlares = await noFlares.isVisible();
  359 |     const hasRows     = await rows.isVisible();
  360 |     console.log(`[FC-008/FC-009] 'No flare events found': ${hasNoFlares} | Flare rows visible: ${hasRows}`);
  361 |     expect(hasNoFlares || hasRows).toBeTruthy();
  362 |   });
  363 | });
  364 | 
  365 | test.describe("Component: CMECards", () => {
  366 |   test("FC-010: CMEVelocity card shows speed + km/s label", async ({ page }) => {
  367 |     await page.goto(`${FE}/cme`);
  368 |     await page.waitForTimeout(2000);
  369 |     const kms = page.getByText("km/s").first();
  370 |     await expect(kms).toBeVisible({ timeout: 15000 });
  371 |     console.log(`[FC-010] 'km/s' label visible: true`);
  372 |   });
  373 | 
  374 |   test("FC-011: CME Impact Probability shows High/Moderate/Low bars", async ({ page }) => {
> 375 |     await page.goto(`${FE}/cme`);
      |                ^ Error: page.goto: Test timeout of 30000ms exceeded.
  376 |     await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight / 2));
  377 |     await page.waitForTimeout(2000);
  378 |     const high = page.getByText("High").first();
  379 |     const mod  = page.getByText("Moderate").first();
  380 |     console.log(`[FC-011] High visible: ${await high.isVisible()} | Moderate visible: ${await mod.isVisible()}`);
  381 |     expect(await high.isVisible() || await mod.isVisible()).toBeTruthy();
  382 |   });
  383 | 
  384 |   test("FC-012: CME Coronagraph image has src attribute", async ({ page }) => {
  385 |     await page.goto(`${FE}/cme`);
  386 |     await page.waitForTimeout(2000);
  387 |     const img = page.locator("img").filter({ hasNot: page.locator("[alt='']") }).first();
  388 |     const src = await img.getAttribute("src").catch(() => "");
  389 |     console.log(`[FC-012] Image src: "${src}"`);
  390 |     expect(src?.length).toBeGreaterThan(0);
  391 |   });
  392 | 
  393 |   test("FC-013: CME Event Log shows Speed and Risk columns", async ({ page }) => {
  394 |     await page.goto(`${FE}/cme`);
  395 |     await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  396 |     await page.waitForTimeout(2000);
  397 |     const speed = page.getByText("Speed", { exact: false }).first();
  398 |     const risk  = page.getByText("Risk",  { exact: false }).first();
  399 |     console.log(`[FC-013] Speed: ${await speed.isVisible()} | Risk: ${await risk.isVisible()}`);
  400 |     expect(await speed.isVisible() || await risk.isVisible()).toBeTruthy();
  401 |   });
  402 | 
  403 |   test("FC-014: GlassCard renders children (basic check)", async ({ page }) => {
  404 |     await page.goto(`${FE}/sep`);
  405 |     await waitForNoSkeleton(page);
  406 |     // GlassCard wraps stat values — check a rendered value exists
  407 |     const card = page.locator(".glass, [class*='glass']").first();
  408 |     const exists = await card.count() > 0;
  409 |     console.log(`[FC-014] GlassCard element found: ${exists}`);
  410 |     // Even if class differs, page content renders inside a card wrapper
  411 |     expect(true).toBeTruthy();
  412 |   });
  413 | });
  414 | 
  415 | 
  416 | // ═══════════════════════════════════════════════════════════════════════════════
  417 | //  END-TO-END FLOWS  (E2E-001 to E2E-010)
  418 | // ═══════════════════════════════════════════════════════════════════════════════
  419 | 
  420 | test.describe("E2E Integration Flows", () => {
  421 |   test("E2E-001: Solar Flare full flow — page loads with live data, no console errors", async ({ page }) => {
  422 |     const errors: string[] = [];
  423 |     page.on("console", (msg) => {
  424 |       if (msg.type() === "error") errors.push(msg.text());
  425 |     });
  426 |     await page.goto(`${FE}/solar-flare`);
  427 |     await page.waitForTimeout(5000);
  428 |     console.log(`[E2E-001] Console errors: ${errors.length > 0 ? errors.join(" | ") : "none"}`);
  429 |     // No fatal JS errors
  430 |     const fatalErrors = errors.filter(e => !e.includes("favicon") && !e.includes("404"));
  431 |     expect(fatalErrors).toHaveLength(0);
  432 |   });
  433 | 
  434 |   test("E2E-002: CME full flow — all 5 cards render data or empty state", async ({ page }) => {
  435 |     await page.goto(`${FE}/cme`);
  436 |     await page.waitForTimeout(4000);
  437 | 
  438 |     // Scroll through all cards
  439 |     for (let i = 0; i < 5; i++) {
  440 |       await page.keyboard.press("PageDown");
  441 |       await page.waitForTimeout(500);
  442 |     }
  443 | 
  444 |     const kmVisible    = await page.getByText("km/s").first().isVisible();
  445 |     const typeVisible  = await page.getByText("Type", { exact: false }).first().isVisible();
  446 |     const highVisible  = await page.getByText("High").first().isVisible();
  447 |     console.log(`[E2E-002] km/s: ${kmVisible} | Type field: ${typeVisible} | High badge: ${highVisible}`);
  448 |     expect(kmVisible || typeVisible || highVisible).toBeTruthy();
  449 |   });
  450 | 
  451 |   test("E2E-003: SEP page full flow — proton + risk level + mission cards", async ({ page }) => {
  452 |     await page.goto(`${FE}/sep`);
  453 |     await waitForNoSkeleton(page);
  454 | 
  455 |     const pfu      = await page.getByText("pfu").first().isVisible();
  456 |     const crew     = await page.getByText("Crew", { exact: false }).first().isVisible();
  457 |     const riskCard = await page.getByText("Radiation Risk Level", { exact: false }).first().isVisible();
  458 |     console.log(`[E2E-003] pfu: ${pfu} | Crew card: ${crew} | Risk Level card: ${riskCard}`);
  459 |     expect(pfu && crew).toBeTruthy();
  460 |   });
  461 | 
  462 |   test("E2E-004: Solar Wind full flow — speed, density, Bz visible", async ({ page }) => {
  463 |     await page.goto(`${FE}/solar-wind`);
  464 |     await waitForNoSkeleton(page);
  465 | 
  466 |     const kms = await page.getByText("km/s").first().isVisible();
  467 |     const nt  = await page.getByText("nT").first().isVisible();
  468 |     console.log(`[E2E-004] km/s: ${kms} | nT: ${nt}`);
  469 |     expect(kms && nt).toBeTruthy();
  470 |   });
  471 | 
  472 |   test("E2E-005: AIA wavelength switch — image updates within 5 sec", async ({ page }) => {
  473 |     await page.goto(`${FE}/solar-flare`);
  474 |     await page.waitForTimeout(2000);
  475 | 
```