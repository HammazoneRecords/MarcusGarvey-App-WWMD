import React, { useEffect, useMemo, useState } from "react";

/**
 * Solob Wrapper ? Front Door -> Exit Flow (SVG diagram)
 *
 * Goals
 * - Zero Mermaid.
 * - Self-contained React component.
 * - Pan/zoom, node inspector, and a ?critical path only? toggle.
 *
 * Notes
 * - Designed to be ?audit-grade?: node-to-node edges represent real execution order.
 */

const TYPE = {
  PHASE: "phase",
  STEP: "step",
  STATE: "state",
  ARTIFACT: "artifact",
};

const KIND = {
  CRITICAL: "critical",
  AUDIT: "audit",
  NORMAL: "normal",
};

function clamp(n, a, b) {
  return Math.max(a, Math.min(b, n));
}

function niceWrap(text, max = 28) {
  // simple line wrapper for labels
  const words = String(text).split(/\s+/);
  const lines = [];
  let line = "";
  for (const w of words) {
    const next = line ? `${line} ${w}` : w;
    if (next.length > max) {
      if (line) lines.push(line);
      line = w;
    } else {
      line = next;
    }
  }
  if (line) lines.push(line);
  return lines.slice(0, 4); // cap to avoid huge boxes
}

function Icon({ name }) {
  // tiny inline SVG icons to make it feel like a system, not a school diagram
  const base = "h-4 w-4";
  if (name === "state")
    return (
      <svg className={base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2v20" />
        <path d="M4 7h16" />
        <path d="M6 17h12" />
      </svg>
    );
  if (name === "db")
    return (
      <svg className={base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <ellipse cx="12" cy="5" rx="8" ry="3" />
        <path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5" />
        <path d="M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6" />
      </svg>
    );
  if (name === "file")
    return (
      <svg className={base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <path d="M14 2v6h6" />
      </svg>
    );
  if (name === "shield")
    return (
      <svg className={base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 2 20 6v6c0 5-3.5 9.5-8 10-4.5-.5-8-5-8-10V6l8-4z" />
      </svg>
    );
  if (name === "bolt")
    return (
      <svg className={base} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M13 2 3 14h8l-1 8 11-14h-8l0-6z" />
      </svg>
    );
  return null;
}

function Badge({ children, tone = "neutral" }) {
  const tones = {
    neutral: "bg-zinc-800/80 text-zinc-100 border-zinc-700",
    critical: "bg-red-950/60 text-red-100 border-red-700/60",
    audit: "bg-violet-950/50 text-violet-100 border-violet-700/50",
    state: "bg-sky-950/50 text-sky-100 border-sky-700/50",
    artifact: "bg-emerald-950/40 text-emerald-100 border-emerald-700/40",
  };
  return (
    <span
      className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs ${tones[tone] || tones.neutral}`}
    >
      {children}
    </span>
  );
}

function runSelfTests(model) {
  // Lightweight ?tests? via console.assert so it never blocks running the UI.
  // (No test runner assumed in this canvas environment.)
  try {
    const nodeIds = new Set();
    for (const p of model.phases) {
      for (const s of p.steps) {
        console.assert(!nodeIds.has(s.id), `Duplicate node id detected: ${s.id}`);
        nodeIds.add(s.id);
      }
    }

    for (const e of model.edges) {
      console.assert(nodeIds.has(e.from), `Edge 'from' node missing: ${e.from}`);
      console.assert(nodeIds.has(e.to), `Edge 'to' node missing: ${e.to}`);
    }

    for (const id of model.criticalSpine) {
      console.assert(nodeIds.has(id), `Critical spine references missing node: ${id}`);
    }
  } catch (err) {
    // eslint-disable-next-line no-console
    console.warn("Self-tests encountered an error (non-fatal):", err);
  }
}

export default function SolobWrapperFlowVisualizer() {
  const [showCriticalOnly, setShowCriticalOnly] = useState(false);
  const [scale, setScale] = useState(1);
  const [tx, setTx] = useState(40);
  const [ty, setTy] = useState(40);
  const [selected, setSelected] = useState(null);

  const model = useMemo(() => {
    const phases = [
      {
        id: "P0",
        title: "Front Door",
        subtitle: "Start -> State Check -> OBSERVE",
        steps: [
          { id: "START", type: TYPE.STEP, kind: KIND.NORMAL, label: "START" },
          {
            id: "S1",
            type: TYPE.STEP,
            kind: KIND.CRITICAL,
            label: "? mw state\nCheck current system state",
          },
          { id: "OBS", type: TYPE.STATE, kind: KIND.NORMAL, label: "State: OBSERVE" },
        ],
      },
      {
        id: "P1",
        title: "PHASE 1: INITIALIZATION",
        subtitle: "Manifest + DB + Registry + Preflight",
        steps: [
          {
            id: "A1",
            type: TYPE.STEP,
            kind: KIND.CRITICAL,
            label: "? mw observe --note 'Starting session'\nGenerates SID",
          },
          { id: "A2", type: TYPE.STEP, kind: KIND.CRITICAL, label: "? snapshot_anchors.py" },
          { id: "M1", type: TYPE.ARTIFACT, kind: KIND.NORMAL, label: "anchors_manifest*.json" },
          { id: "A3", type: TYPE.STEP, kind: KIND.CRITICAL, label: "? init_db.py" },
          { id: "DB1", type: TYPE.ARTIFACT, kind: KIND.NORMAL, label: "data/memory.db" },
          {
            id: "A4",
            type: TYPE.STEP,
            kind: KIND.CRITICAL,
            label: "? register_anchors_from_registry.py",
          },
          {
            id: "A5",
            type: TYPE.STEP,
            kind: KIND.AUDIT,
            label: "? sanity_check.py\n(0 chunks expected)",
          },
          {
            id: "A6",
            type: TYPE.STEP,
            kind: KIND.AUDIT,
            label: "? pre_ingestion_audit_ext.py\n(manifest/DB/schema alignment)",
          },
        ],
      },
      {
        id: "P2",
        title: "PHASE 2: TRANSITION TO RECORD",
        subtitle: "Operator confirmation + implementation baseline",
        steps: [
          {
            id: "B1",
            type: TYPE.STEP,
            kind: KIND.CRITICAL,
            label: "? mw record --note 'Ready for ingestion'\nConfirm: YES_I_MEAN_IT",
          },
          { id: "REC", type: TYPE.STATE, kind: KIND.NORMAL, label: "State: RECORD" },
          { id: "B2", type: TYPE.STEP, kind: KIND.AUDIT, label: "? session_lock.py" },
          { id: "L1", type: TYPE.ARTIFACT, kind: KIND.NORMAL, label: "evidence/SESSION_LOCK.json" },
        ],
      },
      {
        id: "P3",
        title: "PHASE 3: INGESTION",
        subtitle: "Main work; repeat per anchor",
        steps: [
          {
            id: "C1",
            type: TYPE.STEP,
            kind: KIND.CRITICAL,
            label: "? mw run --intent ...\nimport_lexicon_chunks_v1_1.py\nOR chunk_bos_pages_pilot.py",
          },
          {
            id: "C2",
            type: TYPE.STEP,
            kind: KIND.AUDIT,
            label: "? post_ingestion_audit_ext.py\n(chunk integrity)",
          },
          {
            id: "C3",
            type: TYPE.STEP,
            kind: KIND.AUDIT,
            label: "? cartographer_emit_anchors_map.py",
          },
          { id: "MAP", type: TYPE.ARTIFACT, kind: KIND.NORMAL, label: "ANCHORS_MAP.md" },
        ],
      },
      {
        id: "P4",
        title: "PHASE 4: EVIDENCE BUNDLING",
        subtitle: "Gather -> verify -> index",
        steps: [
          { id: "D1", type: TYPE.STEP, kind: KIND.AUDIT, label: "? prosecutor_emit_evidence_bundle.py" },
          { id: "D2", type: TYPE.STEP, kind: KIND.AUDIT, label: "? prosecutor_verify_evidence_bundle.py" },
          { id: "D3", type: TYPE.STEP, kind: KIND.AUDIT, label: "? evidence_index.py" },
          { id: "IDX", type: TYPE.ARTIFACT, kind: KIND.NORMAL, label: "evidence/INDEX.json" },
        ],
      },
      {
        id: "P5",
        title: "PHASE 5: VALIDATION (Exit Gate)",
        subtitle: "Court sweep -> return to OBSERVE -> exit",
        steps: [
          {
            id: "E1",
            type: TYPE.STEP,
            kind: KIND.CRITICAL,
            label: "? court_sweep.py\nVerdict: PASS/FAIL",
          },
          {
            id: "E2",
            type: TYPE.STEP,
            kind: KIND.CRITICAL,
            label: "? mw observe --note 'Session complete'",
          },
          { id: "EXIT", type: TYPE.STATE, kind: KIND.NORMAL, label: "EXIT IF PASS" },
        ],
      },
    ];

    // Edges (audit-grade: node-to-node), plus artifact ?produces? edges.
    const edges = [
      ["START", "S1"],
      ["S1", "OBS"],

      ["OBS", "A1"],
      ["A1", "A2"],
      ["A2", "A3"],
      ["A3", "A4"],
      ["A4", "A5"],
      ["A5", "A6"],

      ["A6", "B1"],
      ["B1", "REC"],
      ["REC", "B2"],

      ["B2", "C1"],
      ["C1", "C2"],
      ["C2", "C3"],

      ["C3", "D1"],
      ["D1", "D2"],
      ["D2", "D3"],

      ["D3", "E1"],
      ["E1", "E2"],
      ["E2", "EXIT"],

      // Produces edges
      ["A2", "M1"],
      ["A3", "DB1"],
      ["B2", "L1"],
      ["C3", "MAP"],
      ["D3", "IDX"],
    ].map(([from, to]) => ({ id: `${from}->${to}`, from, to }));

    // Critical spine set
    const criticalSpine = new Set(["S1", "A1", "A2", "A3", "A4", "B1", "C1", "E1", "E2"]);

    return { phases, edges, criticalSpine };
  }, []);

  useEffect(() => {
    runSelfTests(model);
  }, [model]);

  const layout = useMemo(() => {
    // Layout rules:
    // - vertical timeline
    // - steps in two columns: main steps (left) + artifacts (right)
    // - phase background cards

    const mainX = 60;
    const artifactX = 520;
    const phasePadTop = 56;
    const phasePadBottom = 26;
    const rowH = 68;

    const nodes = new Map();
    const phaseBoxes = [];

    let y = 0;

    for (const phase of model.phases) {
      const phaseStartY = y;

      // Place phase title line (as a box top)
      y += 12;

      // Split: main steps are everything except artifacts; artifacts sit to the right aligned with producing step
      // For simplicity: we still advance y on each main-step row; artifacts use the same y as their own step slot.

      const phaseMainSteps = phase.steps.filter((s) => s.type !== TYPE.ARTIFACT);
      const phaseArtifacts = phase.steps.filter((s) => s.type === TYPE.ARTIFACT);

      y += phasePadTop;

      // Place main steps sequentially
      phaseMainSteps.forEach((s, i) => {
        const ny = y + i * rowH;
        nodes.set(s.id, {
          ...s,
          x: mainX,
          y: ny,
          w: s.type === TYPE.STATE ? 280 : 360,
          h: s.type === TYPE.STATE ? 42 : 54,
        });
      });

      // Place artifacts: find a best ?anchor? y based on edges (from -> artifact)
      const artifactIncoming = new Map();
      for (const e of model.edges) {
        if (phaseArtifacts.some((a) => a.id === e.to)) {
          artifactIncoming.set(e.to, e.from);
        }
      }

      phaseArtifacts.forEach((a) => {
        const fromId = artifactIncoming.get(a.id);
        const fromNode = fromId ? nodes.get(fromId) : null;
        const ny = fromNode ? fromNode.y : y;
        nodes.set(a.id, {
          ...a,
          x: artifactX,
          y: ny,
          w: 300,
          h: 46,
        });
      });

      const phaseHeight = phasePadTop + phaseMainSteps.length * rowH + phasePadBottom;
      const phaseEndY = phaseStartY + phaseHeight + 18;

      phaseBoxes.push({
        id: phase.id,
        title: phase.title,
        subtitle: phase.subtitle,
        x: 20,
        y: phaseStartY,
        w: 860,
        h: phaseEndY - phaseStartY,
      });

      y = phaseEndY;
    }

    // compute svg bounds
    const maxY = y + 40;
    const w = 920;
    const h = maxY;

    return { nodes, phaseBoxes, w, h };
  }, [model]);

  const visibleNodes = useMemo(() => {
    if (!showCriticalOnly) return layout.nodes;

    const keep = new Set();
    // critical nodes + states on the main line + entry/exit
    for (const [id, n] of layout.nodes.entries()) {
      if (model.criticalSpine.has(id)) keep.add(id);
      if (n.type === TYPE.STATE) keep.add(id);
      if (id === "START" || id === "EXIT" || id === "OBS" || id === "REC") keep.add(id);
    }

    const nodes = new Map();
    for (const id of keep) {
      const n = layout.nodes.get(id);
      if (n) nodes.set(id, n);
    }
    return nodes;
  }, [layout.nodes, model.criticalSpine, showCriticalOnly]);

  const visibleEdges = useMemo(() => {
    const nodes = visibleNodes;
    return model.edges.filter((e) => nodes.has(e.from) && nodes.has(e.to));
  }, [model.edges, visibleNodes]);

  function nodeTone(node) {
    if (node.type === TYPE.STATE) return "state";
    if (node.type === TYPE.ARTIFACT) return "artifact";
    if (node.kind === KIND.CRITICAL) return "critical";
    if (node.kind === KIND.AUDIT) return "audit";
    return "neutral";
  }

  function nodeIcon(node) {
    if (node.type === TYPE.STATE) return "state";
    if (node.type === TYPE.ARTIFACT) return node.label.includes(".db") ? "db" : "file";
    if (node.kind === KIND.AUDIT) return "shield";
    if (node.kind === KIND.CRITICAL) return "bolt";
    return "file";
  }

  function nodeStyles(node) {
    const base = {
      fill: "rgba(24,24,27,0.75)",
      stroke: "rgba(113,113,122,0.55)",
      strokeWidth: 1.2,
    };

    if (node.type === TYPE.STATE) {
      return {
        fill: "rgba(2, 6, 23, 0.65)",
        stroke: "rgba(56, 189, 248, 0.45)",
        strokeWidth: 2.2,
      };
    }

    if (node.type === TYPE.ARTIFACT) {
      return {
        fill: "rgba(6, 95, 70, 0.18)",
        stroke: "rgba(16, 185, 129, 0.35)",
        strokeWidth: 1.8,
      };
    }

    if (node.kind === KIND.CRITICAL) {
      return {
        fill: "rgba(88, 28, 28, 0.22)",
        stroke: "rgba(248, 113, 113, 0.55)",
        strokeWidth: 3,
      };
    }

    if (node.kind === KIND.AUDIT) {
      return {
        fill: "rgba(46, 16, 101, 0.18)",
        stroke: "rgba(192, 132, 252, 0.4)",
        strokeWidth: 2,
      };
    }

    return base;
  }

  function edgeStyles(fromNode, toNode) {
    // thicker on critical spine
    const critical = model.criticalSpine.has(fromNode.id) && model.criticalSpine.has(toNode.id);
    const produces = toNode.type === TYPE.ARTIFACT;

    return {
      stroke: produces
        ? "rgba(16, 185, 129, 0.35)"
        : critical
        ? "rgba(248, 113, 113, 0.6)"
        : "rgba(148, 163, 184, 0.35)",
      strokeWidth: produces ? 2 : critical ? 3.2 : 1.6,
      dasharray: produces ? "6 6" : "0",
    };
  }

  function centerOf(n) {
    return { cx: n.x + n.w / 2, cy: n.y + n.h / 2 };
  }

  function roundedRectPath(x, y, w, h, r) {
    const rr = Math.min(r, w / 2, h / 2);
    return `M ${x + rr} ${y} H ${x + w - rr} Q ${x + w} ${y} ${x + w} ${y + rr} V ${y + h - rr} Q ${x + w} ${y + h} ${x + w - rr} ${y + h} H ${x + rr} Q ${x} ${y + h} ${x} ${y + h - rr} V ${y + rr} Q ${x} ${y} ${x + rr} ${y} Z`;
  }

  // Pan/zoom handlers
  function onWheel(e) {
    e.preventDefault();
    const delta = -e.deltaY;
    const next = clamp(scale + (delta > 0 ? 0.08 : -0.08), 0.55, 1.85);
    setScale(next);
  }

  function onKeyDown(e) {
    if (e.key === "+" || e.key === "=") setScale((s) => clamp(s + 0.1, 0.55, 1.85));
    if (e.key === "-") setScale((s) => clamp(s - 0.1, 0.55, 1.85));
    if (e.key === "0") {
      setScale(1);
      setTx(40);
      setTy(40);
    }
  }

  const exportSvg = () => {
    const el = document.getElementById("solob-svg");
    if (!el) return;
    const svgText = new XMLSerializer().serializeToString(el);
    const blob = new Blob([svgText], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "solob-wrapper-flow.svg";
    a.click();
    URL.revokeObjectURL(url);
  };

  const selectedRoleText = useMemo(() => {
    if (!selected) return "";
    if (selected.kind === KIND.CRITICAL) return "Must work (NO-GO gate)";
    if (selected.kind === KIND.AUDIT) return "Verifies integrity";
    if (selected.type === TYPE.ARTIFACT) return "Stored proof/output";
    return "Operator step";
  }, [selected]);

  return (
    <div
      className="min-h-screen w-full bg-zinc-950 text-zinc-100"
      onKeyDown={onKeyDown}
      tabIndex={0}
      role="application"
      aria-label="Solob Wrapper Flow Visualizer"
    >
      <div className="mx-auto max-w-6xl px-4 py-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <div className="text-2xl font-semibold tracking-tight">SOLOB WRAPPER ? Front Door -> Exit Flow</div>
            <div className="mt-1 text-sm text-zinc-300/80">
              SVG diagram (pan/zoom) ? because every time you cross Flat Bridge you should see the flow in your head. ?
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <Badge tone="critical">
                <Icon name="bolt" /> Critical
              </Badge>
              <Badge tone="audit">
                <Icon name="shield" /> Audit
              </Badge>
              <Badge tone="state">
                <Icon name="state" /> State
              </Badge>
              <Badge tone="artifact">
                <Icon name="file" /> Artifact
              </Badge>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              className="rounded-xl border border-zinc-700/70 bg-zinc-900/60 px-3 py-2 text-sm hover:bg-zinc-900"
              onClick={() => setShowCriticalOnly((v) => !v)}
            >
              {showCriticalOnly ? "Show full flow" : "Show critical path only"}
            </button>
            <button
              className="rounded-xl border border-zinc-700/70 bg-zinc-900/60 px-3 py-2 text-sm hover:bg-zinc-900"
              onClick={() => setScale((s) => clamp(s + 0.1, 0.55, 1.85))}
            >
              Zoom +
            </button>
            <button
              className="rounded-xl border border-zinc-700/70 bg-zinc-900/60 px-3 py-2 text-sm hover:bg-zinc-900"
              onClick={() => setScale((s) => clamp(s - 0.1, 0.55, 1.85))}
            >
              Zoom ?
            </button>
            <button
              className="rounded-xl border border-zinc-700/70 bg-zinc-900/60 px-3 py-2 text-sm hover:bg-zinc-900"
              onClick={() => {
                setScale(1);
                setTx(40);
                setTy(40);
              }}
            >
              Reset view (0)
            </button>
            <button
              className="rounded-xl border border-zinc-700/70 bg-zinc-900/60 px-3 py-2 text-sm hover:bg-zinc-900"
              onClick={exportSvg}
            >
              Export SVG
            </button>
          </div>
        </div>

        <div className="mt-5 grid grid-cols-1 gap-4 lg:grid-cols-[1fr_360px]">
          <div className="rounded-2xl border border-zinc-800/70 bg-zinc-950 p-2 shadow-sm">
            <div className="rounded-xl border border-zinc-800/70 bg-zinc-950/60">
              <div className="flex items-center justify-between px-3 py-2 text-xs text-zinc-300/80">
                <div>Pan: drag background * Zoom: mouse wheel * Hotkeys: + / ? / 0</div>
                <div>Scale: {scale.toFixed(2)}</div>
              </div>
              <div
                className="relative h-[72vh] w-full overflow-hidden rounded-xl"
                onWheel={onWheel}
                onMouseDown={(e) => {
                  const startX = e.clientX;
                  const startY = e.clientY;
                  const ox = tx;
                  const oy = ty;
                  const onMove = (ev) => {
                    setTx(ox + (ev.clientX - startX));
                    setTy(oy + (ev.clientY - startY));
                  };
                  const onUp = () => {
                    window.removeEventListener("mousemove", onMove);
                    window.removeEventListener("mouseup", onUp);
                  };
                  window.addEventListener("mousemove", onMove);
                  window.addEventListener("mouseup", onUp);
                }}
              >
                <svg
                  id="solob-svg"
                  width="100%"
                  height="100%"
                  viewBox={`0 0 ${layout.w} ${layout.h}`}
                  className="block"
                >
                  <defs>
                    <marker
                      id="arrow"
                      viewBox="0 0 10 10"
                      refX="8"
                      refY="5"
                      markerWidth="7"
                      markerHeight="7"
                      orient="auto-start-reverse"
                    >
                      <path d="M 0 0 L 10 5 L 0 10 z" fill="rgba(148, 163, 184, 0.55)" />
                    </marker>
                    <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                      <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                      <feMerge>
                        <feMergeNode in="coloredBlur" />
                        <feMergeNode in="SourceGraphic" />
                      </feMerge>
                    </filter>
                  </defs>

                  <g transform={`translate(${tx},${ty}) scale(${scale})`}>
                    {/* Phase background boxes */}
                    {layout.phaseBoxes.map((pb) => (
                      <g key={pb.id}>
                        <path
                          d={roundedRectPath(pb.x, pb.y, pb.w, pb.h, 18)}
                          fill="rgba(9, 9, 11, 0.75)"
                          stroke="rgba(63, 63, 70, 0.65)"
                          strokeWidth="1.5"
                        />
                        <text
                          x={pb.x + 18}
                          y={pb.y + 28}
                          fill="rgba(244,244,245,0.9)"
                          fontSize="14"
                          fontWeight="700"
                        >
                          {pb.title}
                        </text>
                        <text x={pb.x + 18} y={pb.y + 48} fill="rgba(161,161,170,0.9)" fontSize="11">
                          {pb.subtitle}
                        </text>
                      </g>
                    ))}

                    {/* Edges */}
                    {visibleEdges.map((e) => {
                      const from = visibleNodes.get(e.from);
                      const to = visibleNodes.get(e.to);
                      if (!from || !to) return null;

                      const a = centerOf(from);
                      const b = centerOf(to);

                      // route: from right edge if target is artifact; else from bottom to top (vertical-ish)
                      const fromPx = to.type === TYPE.ARTIFACT ? from.x + from.w : a.cx;
                      const fromPy = to.type === TYPE.ARTIFACT ? a.cy : from.y + from.h;
                      const toPx = to.type === TYPE.ARTIFACT ? to.x : b.cx;
                      const toPy = to.type === TYPE.ARTIFACT ? b.cy : to.y;

                      // bezier
                      const dx = Math.max(40, Math.abs(toPx - fromPx) * 0.35);
                      const c1x = fromPx + (to.type === TYPE.ARTIFACT ? dx : 0);
                      const c1y = fromPy + (to.type === TYPE.ARTIFACT ? 0 : 24);
                      const c2x = toPx - (to.type === TYPE.ARTIFACT ? dx : 0);
                      const c2y = toPy - (to.type === TYPE.ARTIFACT ? 0 : 24);

                      const st = edgeStyles(from, to);

                      return (
                        <path
                          key={e.id}
                          d={`M ${fromPx} ${fromPy} C ${c1x} ${c1y}, ${c2x} ${c2y}, ${toPx} ${toPy}`}
                          fill="none"
                          stroke={st.stroke}
                          strokeWidth={st.strokeWidth}
                          strokeDasharray={st.dasharray}
                          markerEnd="url(#arrow)"
                          opacity={0.95}
                        />
                      );
                    })}

                    {/* Nodes */}
                    {[...visibleNodes.values()].map((n) => {
                      const st = nodeStyles(n);
                      const isSelected = selected?.id === n.id;
                      const labelLines = niceWrap(n.label, n.type === TYPE.STATE ? 22 : 30);

                      const rx = n.type === TYPE.STATE ? 999 : 14;
                      const ry = n.type === TYPE.STATE ? 999 : 14;

                      return (
                        <g
                          key={n.id}
                          style={{ cursor: "pointer" }}
                          onClick={() => setSelected(n)}
                          filter={isSelected ? "url(#glow)" : undefined}
                        >
                          <rect
                            x={n.x}
                            y={n.y}
                            width={n.w}
                            height={n.h}
                            rx={rx}
                            ry={ry}
                            fill={st.fill}
                            stroke={st.stroke}
                            strokeWidth={isSelected ? st.strokeWidth + 1 : st.strokeWidth}
                          />

                          {/* left accent bar for critical/audit */}
                          {n.type === TYPE.STEP && (
                            <rect
                              x={n.x}
                              y={n.y}
                              width={6}
                              height={n.h}
                              rx={10}
                              fill={
                                n.kind === KIND.CRITICAL
                                  ? "rgba(248,113,113,0.65)"
                                  : n.kind === KIND.AUDIT
                                  ? "rgba(192,132,252,0.55)"
                                  : "rgba(113,113,122,0.45)"
                              }
                            />
                          )}

                          {/* Icon */}
                          <foreignObject x={n.x + 12} y={n.y + (n.h - 18) / 2} width={20} height={20}>
                            <div className="text-zinc-100/90">
                              <Icon name={nodeIcon(n)} />
                            </div>
                          </foreignObject>

                          {/* Label */}
                          <text x={n.x + 40} y={n.y + 20} fill="rgba(244,244,245,0.92)" fontSize="12" fontWeight="600">
                            {labelLines[0] || ""}
                          </text>
                          {labelLines.slice(1).map((line, idx) => (
                            <text
                              key={idx}
                              x={n.x + 40}
                              y={n.y + 20 + (idx + 1) * 14}
                              fill="rgba(212,212,216,0.85)"
                              fontSize="11"
                            >
                              {line}
                            </text>
                          ))}

                          {/* tiny tag */}
                          <text
                            x={n.x + n.w - 12}
                            y={n.y + 18}
                            fill="rgba(161,161,170,0.75)"
                            fontSize="10"
                            textAnchor="end"
                          >
                            {n.type === TYPE.STATE ? "STATE" : n.type === TYPE.ARTIFACT ? "ARTIFACT" : n.kind.toUpperCase()}
                          </text>
                        </g>
                      );
                    })}

                    {/* Critical path spine hint */}
                    {!showCriticalOnly && (
                      <g opacity={0.35}>
                        <text x={520} y={32} fill="rgba(248,113,113,0.85)" fontSize="11" fontWeight="700">
                          Critical spine (NO-GO if broken)
                        </text>
                      </g>
                    )}
                  </g>
                </svg>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-zinc-800/70 bg-zinc-950/60 p-4">
            <div className="text-sm font-semibold">Inspector</div>
            <div className="mt-1 text-xs text-zinc-300/80">Click any node to see details. This is the ?receipts view.?</div>

            <div className="mt-4 space-y-3">
              {selected ? (
                <>
                  <div className="flex items-center justify-between">
                    <div className="text-base font-semibold">{selected.id}</div>
                    <Badge tone={nodeTone(selected)}>
                      <Icon name={nodeIcon(selected)} /> {selected.type.toUpperCase()}
                    </Badge>
                  </div>

                  <div className="rounded-xl border border-zinc-800/70 bg-zinc-950 p-3">
                    <div className="text-xs font-semibold text-zinc-200/90">Label</div>
                    <div className="mt-1 whitespace-pre-wrap text-sm text-zinc-100/90">{selected.label}</div>
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div className="rounded-xl border border-zinc-800/70 bg-zinc-950 p-3">
                      <div className="text-xs text-zinc-300/80">Kind</div>
                      <div className="mt-1 text-sm">{selected.kind}</div>
                    </div>
                    <div className="rounded-xl border border-zinc-800/70 bg-zinc-950 p-3">
                      <div className="text-xs text-zinc-300/80">Role</div>
                      <div className="mt-1 text-sm">{selectedRoleText}</div>
                    </div>
                  </div>

                  <div className="rounded-xl border border-zinc-800/70 bg-zinc-950 p-3">
                    <div className="text-xs font-semibold text-zinc-200/90">Why it matters</div>
                    <div className="mt-1 text-sm text-zinc-200/90">
                      {selected.id === "E1" ? (
                        <>This is the Exit Gate. It stops ?it ran? from pretending it?s ?it?s valid.?</>
                      ) : selected.id === "B1" ? (
                        <>This is the consent checkpoint ? the human signs reality before the system changes it.</>
                      ) : selected.type === TYPE.ARTIFACT ? (
                        <>Artifacts are the memory of the run. Without them, the run is just vibes.</>
                      ) : selected.kind === KIND.CRITICAL ? (
                        <>Critical means the whole chain collapses if this node fails. This is your ?NO GO? spine.</>
                      ) : selected.kind === KIND.AUDIT ? (
                        <>Audits are the immune system ? they detect corruption before it becomes history.</>
                      ) : (
                        <>A normal step ? still important, but not an immediate gatekeeper.</>
                      )}
                    </div>
                  </div>
                </>
              ) : (
                <div className="rounded-xl border border-zinc-800/70 bg-zinc-950 p-3 text-sm text-zinc-200/90">
                  No node selected yet. Click a box in the diagram.
                </div>
              )}

              <div className="rounded-xl border border-zinc-800/70 bg-zinc-950 p-3">
                <div className="text-xs font-semibold text-zinc-200/90">Quick controls</div>
                <ul className="mt-2 list-disc space-y-1 pl-5 text-xs text-zinc-300/80">
                  <li>Wheel = zoom</li>
                  <li>Drag = pan</li>
                  <li>+ / ? = zoom</li>
                  <li>0 = reset</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6 rounded-2xl border border-zinc-800/70 bg-zinc-950/50 p-4 text-sm text-zinc-200/90">
          <div className="font-semibold">Interpretation note</div>
          <div className="mt-1 text-zinc-300/80">
            This diagram is <span className="text-zinc-100">audit-grade</span>: node-to-node edges represent real execution order.
            Phase boxes are visual grouping only ? arrows don?t ?magically? imply sequence unless nodes are linked.
          </div>
        </div>
      </div>
    </div>
  );
}


## 

