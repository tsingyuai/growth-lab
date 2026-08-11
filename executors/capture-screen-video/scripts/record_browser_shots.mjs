#!/usr/bin/env node

import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, renameSync, rmSync, writeFileSync } from "node:fs";
import { basename, dirname, isAbsolute, join, relative, resolve } from "node:path";
import { pathToFileURL } from "node:url";
import { spawnSync } from "node:child_process";

const ACTION_TYPES = new Set(["click", "click-if-visible", "fill", "type", "type-append", "hover", "press", "wait", "wait-for-visible", "wait-for-hidden", "wait-for-url", "wait-for-text", "scroll-to-end"]);
const REQUIREMENT_STATES = new Set(["visible", "hidden", "enabled", "disabled", "checked", "unchecked", "focused"]);

function parseArgs(argv) {
  const result = { confirmCapture: false };
  for (let index = 2; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--confirm-capture") result.confirmCapture = true;
    else if (arg === "--plan") result.plan = argv[++index];
    else if (arg === "--out") result.out = argv[++index];
    else if (arg === "--playwright-module") result.playwrightModule = argv[++index];
    else if (arg === "--browser-executable") result.browserExecutable = argv[++index];
    else if (arg === "--ffmpeg") result.ffmpeg = argv[++index];
    else throw new Error(`Unknown argument: ${arg}`);
  }
  if (!result.plan || !result.out) throw new Error("--plan and --out are required");
  if (!result.confirmCapture) throw new Error("--confirm-capture is required");
  return result;
}

export function validatePlan(plan) {
  if (!plan || plan.schema_version !== 1) throw new Error("browser capture plan schema_version must be 1");
  if (typeof plan.source_url !== "string" || !plan.source_url) throw new Error("source_url is required");
  const width = Number(plan.viewport?.width);
  const height = Number(plan.viewport?.height);
  if (!Number.isInteger(width) || width < 640 || width > 2560 || !Number.isInteger(height) || height < 480 || height > 1600) {
    throw new Error("viewport is invalid");
  }
  if (!Array.isArray(plan.shots) || plan.shots.length < 1 || plan.shots.length > 12) throw new Error("shots must contain 1 to 12 items");
  const shotIds = new Set();
  for (const shot of plan.shots) {
    if (!/^[a-z0-9][a-z0-9-]{0,31}$/.test(shot.id || "") || shotIds.has(shot.id)) throw new Error("shot id is invalid or duplicated");
    shotIds.add(shot.id);
    if (!(Number(shot.duration_seconds) >= 1 && Number(shot.duration_seconds) <= 180)) throw new Error(`shot ${shot.id} duration is invalid`);
    if (shot.duration_mode && !["adaptive", "exact"].includes(shot.duration_mode)) throw new Error(`shot ${shot.id} duration mode is invalid`);
    if (shot.tail_hold_ms !== undefined && !(Number(shot.tail_hold_ms) >= 250 && Number(shot.tail_hold_ms) <= 5000)) throw new Error(`shot ${shot.id} tail hold is invalid`);
    if (!Array.isArray(shot.actions) || !Array.isArray(shot.requirements) || shot.requirements.length < 1) throw new Error(`shot ${shot.id} actions or requirements are missing`);
    const allActionIds = new Set();
    const requirementActionIds = new Set(["start"]);
    for (const action of [...(shot.setup_actions || []), ...shot.actions]) {
      if (!/^[a-z0-9][a-z0-9-]{0,47}$/.test(action.id || "") || allActionIds.has(action.id)) throw new Error(`shot ${shot.id} action id is invalid or duplicated`);
      if (!ACTION_TYPES.has(action.type)) throw new Error(`shot ${shot.id} action type is invalid`);
      if (!["wait", "wait-for-url", "wait-for-text", "scroll-to-end"].includes(action.type) && !action.selector) throw new Error(`shot ${shot.id} action ${action.id} needs a selector`);
      if (["wait-for-url", "wait-for-text"].includes(action.type) && (typeof action.value !== "string" || !action.value)) throw new Error(`shot ${shot.id} action ${action.id} needs a text value`);
      if (action.timeout_ms !== undefined && !(Number(action.timeout_ms) >= 250 && Number(action.timeout_ms) <= 120000)) throw new Error(`shot ${shot.id} action ${action.id} timeout is invalid`);
      allActionIds.add(action.id);
    }
    for (const action of shot.actions) requirementActionIds.add(action.id);
    const requirementIds = new Set();
    for (const requirement of shot.requirements) {
      if (!/^[a-z0-9][a-z0-9-]{0,47}$/.test(requirement.id || "") || requirementIds.has(requirement.id)) throw new Error(`shot ${shot.id} requirement id is invalid or duplicated`);
      if (!requirementActionIds.has(requirement.after_action)) throw new Error(`shot ${shot.id} requirement ${requirement.id} references an unknown recorded action`);
      if (!requirement.selector || !REQUIREMENT_STATES.has(requirement.state)) throw new Error(`shot ${shot.id} requirement ${requirement.id} is invalid`);
      requirementIds.add(requirement.id);
    }
  }
  return plan;
}

function sha256File(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function relativePath(from, target) {
  return relative(from, target).replaceAll("\\", "/");
}

async function loadPlaywright(modulePath) {
  if (!modulePath) return import("playwright");
  const specifier = modulePath.startsWith("file:") ? modulePath : pathToFileURL(resolve(modulePath)).href;
  return import(specifier);
}

async function injectCursor(page) {
  await page.evaluate(() => {
    document.getElementById("growth-lab-capture-cursor")?.remove();
    const cursor = document.createElement("div");
    cursor.id = "growth-lab-capture-cursor";
    Object.assign(cursor.style, {
      position: "fixed", left: "24px", top: "24px", width: "28px", height: "36px",
      background: "#11131a", border: "3px solid white",
      clipPath: "polygon(0 0,0 82%,25% 62%,42% 100%,58% 92%,42% 56%,76% 56%)",
      filter: "drop-shadow(0 2px 2px rgba(0,0,0,.35))", pointerEvents: "none",
      zIndex: "2147483647", transition: "left 140ms ease-out,top 140ms ease-out",
    });
    document.body.appendChild(cursor);
  });
}

async function moveCursor(page, locator) {
  const box = await locator.boundingBox();
  if (!box) throw new Error("action target has no visible bounds");
  const x = box.x + box.width / 2;
  const y = box.y + box.height / 2;
  await page.evaluate(({ x, y }) => {
    const cursor = document.getElementById("growth-lab-capture-cursor");
    if (cursor) {
      cursor.style.left = `${x}px`;
      cursor.style.top = `${y}px`;
    }
  }, { x, y });
  await page.mouse.move(x, y, { steps: 8 });
  await page.waitForTimeout(120);
  return { x, y };
}

async function runAction(page, action, showCursor) {
  if (action.type === "wait") {
    await page.waitForTimeout(Number(action.value || action.wait_after_ms || 0));
    return;
  }
  if (action.type === "wait-for-url") {
    const timeoutMs = Number(action.timeout_ms || 30000);
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline && !page.url().includes(String(action.value))) await page.waitForTimeout(100);
    if (!page.url().includes(String(action.value))) throw new Error(`wait-for-url exceeded ${timeoutMs}ms: ${page.url()}`);
    if (Number(action.wait_after_ms || 0) > 0) await page.waitForTimeout(Number(action.wait_after_ms));
    return;
  }
  if (action.type === "wait-for-text") {
    const timeoutMs = Number(action.timeout_ms || 30000);
    const deadline = Date.now() + timeoutMs;
    let found = false;
    while (Date.now() < deadline && !found) {
      try { found = await page.evaluate(text => (document.body?.innerText || "").includes(text), String(action.value)); }
      catch { found = false; }
      if (!found) await page.waitForTimeout(100);
    }
    if (!found) throw new Error(`wait-for-text exceeded ${timeoutMs}ms: ${action.value}`);
    if (Number(action.wait_after_ms || 0) > 0) await page.waitForTimeout(Number(action.wait_after_ms));
    return;
  }
  if (action.type === "scroll-to-end") {
    const timeoutMs = Number(action.timeout_ms || 60000);
    const delayMs = Number(action.delay_ms || 350);
    const deadline = Date.now() + timeoutMs;
    let unchangedSteps = 0;
    let previousY = -1;
    while (Date.now() < deadline) {
      const metrics = await page.evaluate(() => ({
        y: window.scrollY,
        viewport: window.innerHeight,
        height: document.documentElement.scrollHeight,
      }));
      if (metrics.y + metrics.viewport >= metrics.height - 2) break;
      const step = Math.min(Number(action.value || Math.floor(metrics.viewport * 0.7)), metrics.height - metrics.viewport - metrics.y);
      await page.mouse.wheel(0, step);
      await page.waitForTimeout(delayMs);
      const currentY = await page.evaluate(() => window.scrollY);
      unchangedSteps = currentY === previousY ? unchangedSteps + 1 : 0;
      previousY = currentY;
      if (unchangedSteps >= 3) throw new Error("scroll-to-end made no progress");
    }
    const atBottom = await page.evaluate(() => window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2);
    if (!atBottom) throw new Error(`scroll-to-end exceeded ${timeoutMs}ms`);
    if (Number(action.wait_after_ms || 0) > 0) await page.waitForTimeout(Number(action.wait_after_ms));
    return;
  }
  const locator = page.locator(action.selector).first();
  if (action.type === "wait-for-visible" || action.type === "wait-for-hidden") {
    await locator.waitFor({
      state: action.type === "wait-for-visible" ? "visible" : "hidden",
      timeout: Number(action.timeout_ms || 60000),
    });
    if (Number(action.wait_after_ms || 0) > 0) await page.waitForTimeout(Number(action.wait_after_ms));
    return;
  }
  if (action.type === "click-if-visible") {
    try {
      await locator.waitFor({ state: "visible", timeout: 2000 });
      await locator.click();
    } catch {
      // Optional setup controls may not exist in every responsive layout.
    }
    if (Number(action.wait_after_ms || 0) > 0) await page.waitForTimeout(Number(action.wait_after_ms));
    return;
  }
  await locator.waitFor({ state: "visible", timeout: 8000 });
  let cursorPoint;
  if (showCursor && ["click", "hover", "type", "type-append", "press"].includes(action.type)) cursorPoint = await moveCursor(page, locator);
  if (action.type === "click") {
    if (cursorPoint) await page.mouse.click(cursorPoint.x, cursorPoint.y);
    else await locator.click();
  }
  else if (action.type === "fill") await locator.fill(String(action.value ?? ""));
  else if (action.type === "type") {
    await locator.click();
    await locator.fill("");
    await locator.pressSequentially(String(action.value ?? ""), { delay: Number(action.delay_ms || 35) });
  } else if (action.type === "type-append") {
    await locator.click();
    await locator.pressSequentially(String(action.value ?? ""), { delay: Number(action.delay_ms || 35) });
  } else if (action.type === "hover") await locator.hover();
  else if (action.type === "press") await locator.press(String(action.value || ""));
  if (Number(action.wait_after_ms || 0) > 0) await page.waitForTimeout(Number(action.wait_after_ms));
}

async function checkRequirement(page, requirement) {
  const locator = page.locator(requirement.selector).first();
  let pass = false;
  if (requirement.state === "visible") pass = await locator.isVisible();
  else if (requirement.state === "hidden") pass = await locator.isHidden();
  else if (requirement.state === "enabled") pass = await locator.isEnabled();
  else if (requirement.state === "disabled") pass = await locator.isDisabled();
  else if (requirement.state === "focused") {
    pass = await locator.evaluate(element => element === document.activeElement);
  }
  else {
    let checked = false;
    try { checked = await locator.isChecked(); }
    catch {
      const state = (await locator.getAttribute("aria-checked")) || (await locator.getAttribute("data-state"));
      checked = state === "true" || state === "checked";
    }
    pass = requirement.state === "checked" ? checked : !checked;
  }
  if (!pass) throw new Error(`requirement ${requirement.id} failed state ${requirement.state}`);
  if (requirement.state === "hidden") {
    return { text: "hidden", focus_box: null };
  }
  const text = (await locator.textContent()) || "";
  if (requirement.text_contains && !text.includes(requirement.text_contains)) {
    throw new Error(`requirement ${requirement.id} missing text: ${requirement.text_contains}`);
  }
  let value = "";
  if (requirement.value_contains) {
    try { value = await locator.inputValue(); }
    catch { value = (await locator.getAttribute("value")) || ""; }
    if (!value.includes(requirement.value_contains)) {
      throw new Error(`requirement ${requirement.id} missing value: ${requirement.value_contains}`);
    }
  }
  return { text: text.trim() || value, focus_box: await locator.boundingBox() };
}

async function collectRequirements(page, requirements, evidenceDir, shotStart, evidence) {
  if (!requirements.length) return;
  const holdStarted = Date.now();
  const before = await Promise.all(requirements.map(requirement => checkRequirement(page, requirement)));
  const holdMs = Math.max(...requirements.map(requirement => Number(requirement.minimum_hold_ms || 0)));
  const actionId = requirements[0].after_action.replaceAll(/[^a-z0-9-]/g, "-");
  const file = join(evidenceDir, `${actionId}-requirements.png`);
  const settleMs = Math.min(200, holdMs);
  if (settleMs > 0) await page.waitForTimeout(settleMs);
  await page.screenshot({ path: file, fullPage: false });
  const remainingHold = holdMs - (Date.now() - holdStarted);
  if (remainingHold > 0) await page.waitForTimeout(remainingHold);
  const after = await Promise.all(requirements.map(requirement => checkRequirement(page, requirement)));
  const observedHold = (Date.now() - holdStarted) / 1000;
  for (let index = 0; index < requirements.length; index += 1) {
    const requirement = requirements[index];
    evidence.push({
      requirement_id: requirement.id,
      status: "pass",
      evidence_file: basename(file),
      evidence_timestamp_seconds: Number(((Date.now() - shotStart) / 1000).toFixed(3)),
      observed_hold_seconds: Number(observedHold.toFixed(3)),
      observed_state: after[index].text || requirement.state,
      focus_box: before[index].focus_box,
    });
  }
}

function runFfmpeg(ffmpeg, args, label) {
  const result = spawnSync(ffmpeg, args, { encoding: "utf8", windowsHide: true });
  if (result.status !== 0) throw new Error(`${label}: ${(result.stderr || result.stdout || "").slice(-1600)}`);
  return result;
}

function inspectVideo(ffmpeg, video) {
  runFfmpeg(ffmpeg, ["-v", "error", "-i", video, "-map", "0:v:0", "-f", "null", process.platform === "win32" ? "NUL" : "/dev/null"], "video decode failed");
  const probe = spawnSync(ffmpeg, ["-hide_banner", "-i", video], { encoding: "utf8", windowsHide: true });
  const text = `${probe.stderr || ""}${probe.stdout || ""}`;
  const duration = text.match(/Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)/);
  const size = text.match(/Video:.*?\b(\d{2,5})x(\d{2,5})\b/s);
  const fps = text.match(/([\d.]+)\s+fps/);
  if (!duration || !size) throw new Error("unable to inspect browser capture");
  return {
    duration_seconds: Number((Number(duration[1]) * 3600 + Number(duration[2]) * 60 + Number(duration[3])).toFixed(3)),
    width: Number(size[1]), height: Number(size[2]), fps: Number(fps?.[1] || 0), has_audio: false,
  };
}

function ffmpegVersion(ffmpeg) {
  const result = runFfmpeg(ffmpeg, ["-version"], "ffmpeg unavailable");
  return result.stdout.split(/\r?\n/)[0].trim();
}

async function recordAttempt(browser, plan, shot, outDir, attempt, ffmpeg, ffmpegVersionLine) {
  const attemptDir = join(outDir, "attempts", shot.id, String(attempt));
  const rawDir = join(attemptDir, "raw");
  const evidenceDir = join(attemptDir, "evidence");
  mkdirSync(rawDir, { recursive: true });
  mkdirSync(evidenceDir, { recursive: true });
  const context = await browser.newContext({ viewport: plan.viewport, recordVideo: { dir: rawDir, size: plan.viewport } });
  let rawVideo;
  try {
    const page = await context.newPage();
    const video = page.video();
    const contextStart = Date.now();
    const pageErrors = [];
    page.on("pageerror", error => pageErrors.push(error.message));
    await page.goto(plan.source_url, { waitUntil: "domcontentloaded", timeout: 30000 });
    for (const selector of shot.readiness_selectors || []) await page.locator(selector).first().waitFor({ state: "visible", timeout: 15000 });
    for (const action of shot.setup_actions || []) await runAction(page, action, false);
    if (pageErrors.length) throw new Error(`page errors before capture: ${pageErrors.join(" | ")}`);
    await injectCursor(page);
    const shotStart = Date.now();
    const evidence = [];
    await collectRequirements(page, shot.requirements.filter(item => item.after_action === "start"), evidenceDir, shotStart, evidence);
    for (const action of shot.actions) {
      await runAction(page, action, true);
      await collectRequirements(page, shot.requirements.filter(item => item.after_action === action.id), evidenceDir, shotStart, evidence);
    }
    const durationMode = shot.duration_mode || "adaptive";
    const durationLimit = Number(shot.duration_seconds);
    const tailHoldMs = Number(shot.tail_hold_ms || 750);
    await page.waitForTimeout(tailHoldMs);
    let targetDuration = Math.max(1, (Date.now() - shotStart) / 1000);
    if (targetDuration > durationLimit + 0.15) throw new Error(`shot actions need ${targetDuration.toFixed(2)}s but duration limit is ${durationLimit}s`);
    if (durationMode === "exact") {
      await page.waitForTimeout(Math.max(0, durationLimit * 1000 - (Date.now() - shotStart)));
      targetDuration = durationLimit;
    }
    if (evidence.length !== shot.requirements.length) throw new Error("not every requirement produced evidence");
    if (pageErrors.length) throw new Error(`page errors during capture: ${pageErrors.join(" | ")}`);
    const shotOffset = Math.max(0, (shotStart - contextStart) / 1000);
    const preRoll = 0;
    const trimStart = shotOffset;
    await context.close();
    rawVideo = await video.path();

    const output = join(outDir, `${shot.id}.mp4`);
    const partial = join(outDir, `.${shot.id}.partial.mp4`);
    rmSync(partial, { force: true });
    runFfmpeg(ffmpeg, [
      "-y", "-ss", trimStart.toFixed(3), "-i", rawVideo, "-t", targetDuration.toFixed(3),
      "-an", "-vf", `tpad=stop_mode=clone:stop_duration=1,fps=30,scale=${plan.viewport.width}:${plan.viewport.height},format=yuv420p`,
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-movflags", "+faststart", partial,
    ], `transcode ${shot.id} failed`);
    const metadata = inspectVideo(ffmpeg, partial);
    if (metadata.duration_seconds < targetDuration - 0.25) throw new Error("transcoded shot is too short");
    rmSync(output, { force: true });
    renameSync(partial, output);

    const evidenceFile = join(outDir, `${shot.id}.browser-evidence.json`);
    const evidencePayload = {
      schema_version: 1, status: "pass", shot_id: shot.id, attempt,
      source_url: plan.source_url, viewport: plan.viewport, pre_roll_seconds: preRoll,
      requirements: evidence.map(item => ({
        ...item,
        evidence_timestamp_seconds: Number((item.evidence_timestamp_seconds + preRoll).toFixed(3)),
        evidence_file: relativePath(dirname(evidenceFile), join(evidenceDir, item.evidence_file)),
      })),
    };
    writeFileSync(evidenceFile, JSON.stringify(evidencePayload, null, 2), "utf8");
    const manifestFile = join(outDir, `${shot.id}.capture-manifest.json`);
    const manifest = {
      schema_version: 1, status: "recorded-validated",
      source: { kind: "browser", url: plan.source_url, viewport_width: plan.viewport.width, viewport_height: plan.viewport.height },
      capture: {
        started_at: new Date(shotStart).toISOString(), requested_duration_seconds: Number(targetDuration.toFixed(3)),
        draw_mouse: true, scope_confirmed: true, human_privacy_review_required: true,
        semantic_validation: {
          status: "pass", requirement_count: evidence.length,
          evidence_file: relativePath(dirname(manifestFile), evidenceFile), evidence_sha256: sha256File(evidenceFile),
        },
      },
      renderer: { name: "playwright-chromium", ffmpeg_version: ffmpegVersionLine, external_binary: true },
      output: { file: basename(output), sha256: sha256File(output), ...metadata },
      publication_authorized: false,
    };
    writeFileSync(manifestFile, JSON.stringify(manifest, null, 2), "utf8");
    return { shot_id: shot.id, attempt, video: output, manifest: manifestFile, evidence: evidenceFile };
  } finally {
    if (!rawVideo) await context.close().catch(() => {});
  }
}

export async function runPlan(plan, options) {
  validatePlan(plan);
  const playwright = await loadPlaywright(options.playwrightModule);
  const launchOptions = { headless: plan.browser?.headless ?? true };
  if (options.browserExecutable || plan.browser?.executable_path) {
    launchOptions.executablePath = options.browserExecutable || plan.browser.executable_path;
  }
  const browser = await playwright.chromium.launch(launchOptions);
  const ffmpegVersionLine = ffmpegVersion(options.ffmpeg);
  const results = [];
  try {
    for (const shot of plan.shots) {
      let lastError;
      const maxAttempts = Number(shot.max_attempts || 2);
      for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
        try {
          results.push(await recordAttempt(browser, plan, shot, options.outDir, attempt, options.ffmpeg, ffmpegVersionLine));
          lastError = undefined;
          break;
        } catch (error) {
          lastError = error;
          writeFileSync(join(options.outDir, `${shot.id}.attempt-${attempt}.error.log`), `${error.stack || error}\n`, "utf8");
        }
      }
      if (lastError) throw new Error(`shot ${shot.id} failed after ${maxAttempts} attempts: ${lastError.message}`);
    }
  } finally {
    await browser.close();
  }
  return results;
}

async function main() {
  const args = parseArgs(process.argv);
  const planPath = resolve(args.plan);
  const outDir = resolve(args.out);
  mkdirSync(outDir, { recursive: true });
  const plan = validatePlan(JSON.parse(readFileSync(planPath, "utf8")));
  if (!/^[a-z][a-z0-9+.-]*:/i.test(plan.source_url)) {
    plan.source_url = pathToFileURL(resolve(dirname(planPath), plan.source_url)).href;
  }
  const ffmpeg = args.ffmpeg || process.env.FFMPEG_BINARY || "ffmpeg";
  const results = await runPlan(plan, {
    outDir, playwrightModule: args.playwrightModule,
    browserExecutable: args.browserExecutable, ffmpeg,
  });
  process.stdout.write(`${JSON.stringify({ status: "recorded-validated", shot_count: results.length, results }, null, 2)}\n`);
}

if (process.argv[1] && pathToFileURL(resolve(process.argv[1])).href === import.meta.url) {
  main().catch(error => {
    process.stderr.write(`Error: ${error.stack || error}\n`);
    process.exitCode = 1;
  });
}
