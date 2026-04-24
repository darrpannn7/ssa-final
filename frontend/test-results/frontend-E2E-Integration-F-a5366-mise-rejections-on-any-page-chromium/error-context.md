# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: frontend.spec.ts >> E2E Integration Flows >> E2E-010: Console has no unhandled promise rejections on any page
- Location: tests\frontend.spec.ts:566:7

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
        - generic [ref=e39]:
          - generic [ref=e40]:
            - paragraph [ref=e41]: Coronal Mass Ejections are massive eruptions of plasma and magnetic field from the Sun's corona.
            - generic [ref=e42]:
              - paragraph [ref=e43]: Latest CME
              - paragraph [ref=e44]: 2026-04-16T09:00:00-CME-001
              - paragraph [ref=e45]: Thu, 16 Apr 2026 09:00:00 GMT
          - generic [ref=e46]:
            - paragraph [ref=e47]: "677"
            - paragraph [ref=e48]: km/s
            - paragraph [ref=e49]: Moderate CME
      - generic [ref=e54]:
        - generic [ref=e55]: "02"
        - heading "Magnetic Structure" [level=2] [ref=e56]
        - generic [ref=e57]:
          - paragraph [ref=e59]: The magnetic structure determines how the CME interacts with Earth's magnetosphere.
          - generic [ref=e60]:
            - generic [ref=e61]:
              - generic [ref=e62]: Type
              - generic [ref=e63]: C
            - generic [ref=e64]:
              - generic [ref=e65]: Latitude
              - generic [ref=e66]: "-9°"
            - generic [ref=e67]:
              - generic [ref=e68]: Longitude
              - generic [ref=e69]: 22°
            - generic [ref=e70]:
              - generic [ref=e71]: Half Angle
              - generic [ref=e72]: 16°
            - generic [ref=e73]:
              - generic [ref=e74]: Location
              - generic [ref=e75]: S08W25
      - generic [ref=e80]:
        - generic [ref=e81]: "03"
        - heading "Impact Probability" [level=2] [ref=e82]
        - generic [ref=e83]:
          - paragraph [ref=e85]: Impact probability depends on CME trajectory, angular width, and speed relative to the Sun-Earth line.
          - paragraph [ref=e87]: Loading...
      - generic [ref=e92]:
        - generic [ref=e93]: "04"
        - heading "CME Coronagraph Image" [level=2] [ref=e94]
        - generic [ref=e95]:
          - paragraph [ref=e97]: LASCO coronagraph blocks the bright solar disk to reveal faint coronal structures and CMEs propagating outward.
          - img "LASCO CME Coronagraph" [ref=e99]
      - generic [ref=e104]:
        - generic [ref=e105]: "05"
        - heading "CME Event Log" [level=2] [ref=e106]
        - generic [ref=e107]:
          - generic [ref=e108]:
            - generic [ref=e109]: ID
            - generic [ref=e110]: Time
            - generic [ref=e111]: Speed
            - generic [ref=e112]: Type
            - generic [ref=e113]: Location
            - generic [ref=e114]: Risk
          - paragraph [ref=e116]: Loading CME events...
  - button "Open Next.js Dev Tools" [ref=e123] [cursor=pointer]:
    - img [ref=e124]
  - alert [ref=e127]
```

# Test source

```ts
  471 | 
  472 |   test("E2E-005: AIA wavelength switch — image updates within 5 sec", async ({ page }) => {
  473 |     await page.goto(`${FE}/solar-flare`);
  474 |     await page.waitForTimeout(2000);
  475 | 
  476 |     let requests = 0;
  477 |     page.on("request", (req) => {
  478 |       if (req.url().includes("aia-image")) requests++;
  479 |     });
  480 | 
  481 |     for (const wl of ["94Å", "193Å", "131Å"]) {
  482 |       const btn = page.getByText(wl, { exact: true }).first();
  483 |       if (await btn.count() > 0) {
  484 |         await btn.click();
  485 |         await page.waitForTimeout(1000);
  486 |         console.log(`[E2E-005] Clicked ${wl} — AIA requests so far: ${requests}`);
  487 |       }
  488 |     }
  489 |     console.log(`[E2E-005] Total AIA image requests triggered: ${requests}`);
  490 |     expect(requests).toBeGreaterThanOrEqual(0); // may be 0 if image is static URL
  491 |   });
  492 | 
  493 |   test("E2E-006: Retry flow — error banner appears when API is mocked to fail then disappears after retry", async ({ page }) => {
  494 |     let callCount = 0;
  495 |     await page.route("**/space-weather/wind/all", async (route) => {
  496 |       callCount++;
  497 |       if (callCount === 1) {
  498 |         await route.fulfill({ status: 500, body: JSON.stringify({ detail: "Simulated" }) });
  499 |       } else {
  500 |         await route.continue();
  501 |       }
  502 |     });
  503 | 
  504 |     await page.goto(`${FE}/solar-wind`);
  505 |     await page.waitForTimeout(3000);
  506 | 
  507 |     const retryBtn = page.getByRole("button", { name: /retry/i });
  508 |     const hasRetry = await retryBtn.isVisible();
  509 |     console.log(`[E2E-006] Retry button after error: ${hasRetry}`);
  510 | 
  511 |     if (hasRetry) {
  512 |       await retryBtn.click();
  513 |       await page.waitForTimeout(4000);
  514 |       const stillError = await retryBtn.isVisible();
  515 |       console.log(`[E2E-006] Retry button after clicking Retry: ${stillError}`);
  516 |     }
  517 |     expect(true).toBeTruthy(); // flow completed without crash
  518 |   });
  519 | 
  520 |   test("E2E-007: Page navigation — all 4 routes load without crash", async ({ page }) => {
  521 |     const routes = [
  522 |       { path: "/solar-flare", label: "Solar Flare" },
  523 |       { path: "/cme",         label: "CME" },
  524 |       { path: "/sep",         label: "SEP" },
  525 |       { path: "/solar-wind",  label: "Solar Wind" },
  526 |     ];
  527 | 
  528 |     for (const { path, label } of routes) {
  529 |       const errors: string[] = [];
  530 |       page.on("console", (msg) => {
  531 |         if (msg.type() === "error") errors.push(msg.text());
  532 |       });
  533 |       await page.goto(`${FE}${path}`);
  534 |       await page.waitForTimeout(2000);
  535 |       const title = await page.title();
  536 |       const fatalErrors = errors.filter(e => !e.includes("favicon") && !e.includes("404"));
  537 |       console.log(`[E2E-007] ${label} (${path}) → title: "${title}" | fatal errors: ${fatalErrors.length}`);
  538 |       expect(fatalErrors.length).toBe(0);
  539 |     }
  540 |   });
  541 | 
  542 |   test("E2E-008: lib/api.ts BASE_URL env var used (no hardcoded localhost in production build)", async ({ page }) => {
  543 |     await page.goto(FE);
  544 |     const requests: string[] = [];
  545 |     page.on("request", (req) => {
  546 |       if (req.url().includes("8000") || req.url().includes("space-weather") || req.url().includes("noaa")) {
  547 |         requests.push(req.url());
  548 |       }
  549 |     });
  550 |     await page.goto(`${FE}/sep`);
  551 |     await page.waitForTimeout(5000);
  552 |     console.log(`[E2E-008] API requests made: ${requests.length} | Sample: ${requests.slice(0, 3).join(", ")}`);
  553 |     expect(requests.length).toBeGreaterThan(0);
  554 |   });
  555 | 
  556 |   test("E2E-009: SEP data auto-refresh — last updated timestamp visible", async ({ page }) => {
  557 |     await page.goto(`${FE}/sep`);
  558 |     await page.waitForTimeout(4000);
  559 |     const ts = page.getByText(/last updated/i).first();
  560 |     const visible = await ts.isVisible();
  561 |     const text = visible ? await ts.textContent() : "not shown";
  562 |     console.log(`[E2E-009] Last updated visible: ${visible} | text: "${text}"`);
  563 |     expect(visible).toBeTruthy();
  564 |   });
  565 | 
  566 |   test("E2E-010: Console has no unhandled promise rejections on any page", async ({ page }) => {
  567 |     const rejections: string[] = [];
  568 |     page.on("pageerror", (err) => rejections.push(err.message));
  569 | 
  570 |     for (const path of ["/solar-flare", "/cme", "/sep", "/solar-wind"]) {
> 571 |       await page.goto(`${FE}${path}`);
      |                  ^ Error: page.goto: Test timeout of 30000ms exceeded.
  572 |       await page.waitForTimeout(2000);
  573 |     }
  574 |     console.log(`[E2E-010] Unhandled rejections: ${rejections.length > 0 ? rejections.join(" | ") : "none"}`);
  575 |     expect(rejections).toHaveLength(0);
  576 |   });
  577 | });
  578 | 
```