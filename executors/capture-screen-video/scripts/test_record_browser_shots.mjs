import test from "node:test";
import assert from "node:assert/strict";

import { validatePlan } from "./record_browser_shots.mjs";

function fixturePlan() {
  return {
    schema_version: 1,
    source_url: "https://example.test/product",
    viewport: { width: 1280, height: 720 },
    shots: [{
      id: "open-filter",
      duration_seconds: 3,
      actions: [{ id: "open", type: "click", selector: "#open" }],
      requirements: [{
        id: "panel-visible", after_action: "open", selector: "#panel",
        state: "visible", minimum_hold_ms: 300,
      }],
    }],
  };
}

test("accepts a bounded declarative browser shot", () => {
  assert.equal(validatePlan(fixturePlan()).shots.length, 1);
});

test("accepts an adaptive long workflow and semantic result wait", () => {
  const plan = fixturePlan();
  plan.shots[0].duration_seconds = 120;
  plan.shots[0].duration_mode = "adaptive";
  plan.shots[0].tail_hold_ms = 900;
  plan.shots[0].actions.push({
    id: "wait-results", type: "wait-for-visible", selector: "#results", timeout_ms: 90000,
  });
  assert.equal(validatePlan(plan).shots[0].actions.at(-1).type, "wait-for-visible");
});

test("accepts a bounded progressive scroll", () => {
  const plan = fixturePlan();
  plan.shots[0].actions.push({
    id: "browse-page", type: "scroll-to-end", value: 480, delay_ms: 300, timeout_ms: 30000,
  });
  assert.equal(validatePlan(plan).shots[0].actions.at(-1).type, "scroll-to-end");
});

test("accepts a URL wait that does not depend on navigation completion", () => {
  const plan = fixturePlan();
  plan.shots[0].actions.push({
    id: "wait-target", type: "wait-for-url", value: "github.com/example/repo", timeout_ms: 30000,
  });
  assert.equal(validatePlan(plan).shots[0].actions.at(-1).type, "wait-for-url");
});

test("accepts a rendered body-text wait after cross-origin navigation", () => {
  const plan = fixturePlan();
  plan.shots[0].actions.push({
    id: "wait-content", type: "wait-for-text", value: "Repository content", timeout_ms: 30000,
  });
  assert.equal(validatePlan(plan).shots[0].actions.at(-1).type, "wait-for-text");
});

test("rejects a workflow above the safety ceiling", () => {
  const plan = fixturePlan();
  plan.shots[0].duration_seconds = 181;
  assert.throws(() => validatePlan(plan), /duration is invalid/);
});

test("rejects requirements bound to unknown actions", () => {
  const plan = fixturePlan();
  plan.shots[0].requirements[0].after_action = "missing";
  assert.throws(() => validatePlan(plan), /unknown recorded action/);
});

test("rejects more than twelve shots", () => {
  const plan = fixturePlan();
  plan.shots = Array.from({ length: 13 }, (_, index) => ({
    ...plan.shots[0], id: `shot-${index + 1}`,
  }));
  assert.throws(() => validatePlan(plan), /1 to 12/);
});
