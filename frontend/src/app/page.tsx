"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import Link from "next/link";
import "./landing.css";

const TOTAL_FRAMES = 192;

function framePath(i: number) {
  return `/frames/ezgif-frame-${String(i).padStart(3, "0")}.png`;
}

export default function LandingPage() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const heroContentRef = useRef<HTMLDivElement>(null);
  const navRef = useRef<HTMLElement>(null);
  const framesRef = useRef<HTMLImageElement[]>([]);
  const readyRef = useRef(false);
  const currentFrameRef = useRef(0);
  const [loadProgress, setLoadProgress] = useState(0);
  const [loaded, setLoaded] = useState(false);

  // Canvas + scroll-driven frame animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    function resize() {
      if (!canvas) return;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      if (readyRef.current) drawFrame(currentFrameRef.current);
    }

    function drawFrame(idx: number) {
      if (!canvas || !ctx) return;
      idx = Math.max(0, Math.min(TOTAL_FRAMES - 1, idx));
      currentFrameRef.current = idx;
      const img = framesRef.current[idx];
      if (!img || !img.complete) return;
      ctx.fillStyle = "#060a08";
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      const cw = canvas.width, ch = canvas.height;
      const iw = img.naturalWidth, ih = img.naturalHeight;
      const scale = Math.max(cw / iw, ch / ih);
      const dw = iw * scale, dh = ih * scale;
      ctx.drawImage(img, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
    }

    function onScroll() {
      const scrollY = window.scrollY || window.pageYOffset;
      const docH = document.documentElement.scrollHeight - window.innerHeight;
      if (readyRef.current && docH > 0) {
        const rel = Math.max(0, Math.min(1, scrollY / docH));
        const idx = Math.round((rel * (TOTAL_FRAMES - 1) * 4) % TOTAL_FRAMES);
        drawFrame(idx);
      }
      if (heroContentRef.current) {
        const fade = 1 - Math.min(1, scrollY / (window.innerHeight * 0.4));
        heroContentRef.current.style.opacity = String(Math.max(0, fade));
        heroContentRef.current.style.transform = `translateY(${-scrollY * 0.3}px)`;
      }
      if (navRef.current) {
        navRef.current.classList.toggle("stuck", scrollY > 80);
      }
    }

    let loadedCount = 0;
    const imgs: HTMLImageElement[] = [];
    for (let i = 1; i <= TOTAL_FRAMES; i++) {
      const img = new Image();
      img.src = framePath(i);
      img.onload = img.onerror = () => {
        loadedCount++;
        setLoadProgress((loadedCount / TOTAL_FRAMES) * 100);
        if (loadedCount >= TOTAL_FRAMES) {
          readyRef.current = true;
          setLoaded(true);
          resize();
          onScroll();
        }
      };
      imgs.push(img);
    }
    framesRef.current = imgs;

    window.addEventListener("resize", resize);
    window.addEventListener("scroll", onScroll, { passive: true });
    resize();

    return () => {
      window.removeEventListener("resize", resize);
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  // Intersection observer for reveal animations
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.classList.add("visible");
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -30px 0px" }
    );
    document.querySelectorAll(".l-reveal, .l-agent-row, .l-pipe-step").forEach((el) =>
      observer.observe(el)
    );
    return () => observer.disconnect();
  }, []);

  const scrollTo = useCallback((id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, []);

  return (
    <div className="landing-root">
      {/* Grain overlay */}
      <svg className="l-grain" xmlns="http://www.w3.org/2000/svg">
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.65" numOctaves="3" stitchTiles="stitch" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>

      {/* Scroll progress bar */}
      <div
        className="l-progress"
        style={{ width: `${(typeof window !== "undefined" && document.documentElement.scrollHeight > window.innerHeight) ? 0 : 0}%` }}
      />

      {/* Loader bar */}
      {!loaded && (
        <div
          className="l-loader"
          style={{ width: `${loadProgress}%`, opacity: loaded ? 0 : 1 }}
        />
      )}

      {/* Canvas */}
      <canvas ref={canvasRef} className="l-canvas" />
      <div className="l-vignette" />

      {/* NAV */}
      <nav ref={navRef} className="l-nav">
        <div className="l-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.png" alt="ScoutR" className="l-brand-logo" />
        </div>
        <ul className="l-nav-links">
          <li><a href="#problem" onClick={(e) => { e.preventDefault(); scrollTo("problem"); }}>Problem</a></li>
          <li><a href="#agents" onClick={(e) => { e.preventDefault(); scrollTo("agents"); }}>Agents</a></li>
          <li><a href="#pipeline" onClick={(e) => { e.preventDefault(); scrollTo("pipeline"); }}>How It Works</a></li>
        </ul>
        <Link href="/app" className="l-nav-cta">ENTER APP</Link>
      </nav>

      {/* PAGE CONTENT */}
      <div className="l-content">

        {/* ── HERO ── */}
        <div className="l-hero">
          <div className="l-hero-content" ref={heroContentRef}>
            <div className="l-hero-badge">
              <span className="l-pulse" />
              Agentic Transfer Intelligence
            </div>
            <h1>
              Transfer Intelligence<span className="l-accent">.</span>
              <br />Always On<span className="l-accent">.</span>
            </h1>
            <p className="l-hero-sub">
              ScoutR watches 50+ leagues so your sporting director doesn&apos;t have to.
            </p>
          </div>
          <div className="l-scroll-hint">
            <span>Scroll</span>
            <div className="l-scroll-bar" />
          </div>
        </div>

        {/* ── PROBLEM ── */}
        <section className="l-section l-section-glass" id="problem">
          <div className="l-container l-reveal">
            <div className="l-problem-grid">
              <div className="l-stat-stack">
                <div className="l-stat-item">
                  <div className="l-stat-number">300+</div>
                  <div className="l-stat-text">Clubs flying blind every window</div>
                </div>
                <div className="l-stat-item">
                  <div className="l-stat-number">€50M</div>
                  <div className="l-stat-text">Average misspent per transfer window</div>
                </div>
                <div className="l-stat-item">
                  <div className="l-stat-number">3 Weeks</div>
                  <div className="l-stat-text">Average manual scouting time per target</div>
                </div>
              </div>
              <div className="l-problem-text">
                <div className="l-section-label"><span>The Problem</span></div>
                <h2>Elite clubs have 20-person analytics departments.</h2>
                <p>
                  The other 300+ clubs in the Championship, Bundesliga 2, Serie B, and MLS are making
                  multi-million euro transfer decisions with Transfermarkt and a spreadsheet.
                  ScoutR changes that.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* ── AGENTS ── */}
        <section className="l-section l-section-glass" id="agents">
          <div className="l-container">
            <div className="l-agents-header l-reveal">
              <div className="l-section-label" style={{ justifyContent: "center" }}>Four AI Agents</div>
              <h2 className="l-agents-heading">HOW SCOUTR THINKS</h2>
              <p className="l-agents-sub">
                Each agent runs autonomously, reasons in real time, and streams its output to your screen.
              </p>
            </div>

            {/* Agent 01 */}
            <div className="l-agent-row">
              <div className="l-agent-info">
                <div className="l-agent-num">01 · Scout Agent</div>
                <h3 className="l-agent-title">NATURAL LANGUAGE SEARCH</h3>
                <p className="l-agent-desc">
                  Describe the player you need in plain English. The Scout Agent translates your brief into
                  structured criteria, scans real player data across 54 leagues, and returns ranked candidates
                  with full reasoning — streamed live.
                </p>
              </div>
              <div className="l-agent-terminal">
                <div className="l-at-header">
                  <div className="l-at-header-left">
                    <div className="l-at-dot live" />
                    <span className="l-at-agent-label">Scout Agent</span>
                  </div>
                  <div className="l-at-status">● Live</div>
                </div>
                <div className="l-at-row"><span className="l-at-key">Query</span><span className="l-at-val">&ldquo;LB, U24, high press&rdquo;</span></div>
                <div className="l-at-row"><span className="l-at-key">Leagues</span><span className="l-at-val green">54 scanned</span></div>
                <div className="l-at-row"><span className="l-at-key">Filtered</span><span className="l-at-val green">2,847 → 12 → 3</span></div>
                <div className="l-at-row"><span className="l-at-key">Top Match</span><span className="l-at-val green">L. Hoffmann — 94.2%</span></div>
                <div className="l-at-row"><span className="l-at-key">Latency</span><span className="l-at-val">2.4s</span></div>
                <div className="l-at-glow" />
              </div>
            </div>

            {/* Agent 02 */}
            <div className="l-agent-row l-reverse">
              <div className="l-agent-info">
                <div className="l-agent-num" style={{ color: "#f5c518" }}>02 · Valuation Agent</div>
                <h3 className="l-agent-title">MARKET FEE INTELLIGENCE</h3>
                <p className="l-agent-desc">
                  Cross-references comparable transfers, contract expiry windows, and selling-club finances
                  to produce a negotiation-ready fee range — not a Transfermarkt guess.
                </p>
              </div>
              <div className="l-agent-terminal">
                <div className="l-at-header">
                  <div className="l-at-header-left">
                    <div className="l-at-dot gold" />
                    <span className="l-at-agent-label">Valuation Agent</span>
                  </div>
                  <div className="l-at-status gold">● Processing</div>
                </div>
                <div className="l-at-row"><span className="l-at-key">Market Value</span><span className="l-at-val gold">€8.2M</span></div>
                <div className="l-at-row"><span className="l-at-key">Range</span><span className="l-at-val gold">€6.5M – €9.1M</span></div>
                <div className="l-at-row"><span className="l-at-key">Contract</span><span className="l-at-val">Jun 2026</span></div>
                <div className="l-at-row"><span className="l-at-key">Comparables</span><span className="l-at-val">14 transfers</span></div>
                <div className="l-at-row"><span className="l-at-key">Seller Pressure</span><span className="l-at-val red">HIGH</span></div>
                <div className="l-at-glow gold" />
              </div>
            </div>

            {/* Agent 03 */}
            <div className="l-agent-row">
              <div className="l-agent-info">
                <div className="l-agent-num">03 · Tactical Fit Agent</div>
                <h3 className="l-agent-title">FORMATION COMPATIBILITY</h3>
                <p className="l-agent-desc">
                  Analyses positional heatmaps, pressing metrics, and formation compatibility. Scores how
                  well a target integrates into your system — then explains why in plain English.
                </p>
              </div>
              <div className="l-agent-terminal">
                <div className="l-at-header">
                  <div className="l-at-header-left">
                    <div className="l-at-dot live" />
                    <span className="l-at-agent-label">Tactical Fit</span>
                  </div>
                  <div className="l-at-status">● Matched</div>
                </div>
                <div className="l-at-row"><span className="l-at-key">Formation</span><span className="l-at-val green">4-3-3 ✓</span></div>
                <div className="l-at-row"><span className="l-at-key">Press Resistance</span><span className="l-at-val green">92nd %ile</span></div>
                <div className="l-at-row"><span className="l-at-key">Prog. Carries</span><span className="l-at-val green">88th %ile</span></div>
                <div className="l-at-row"><span className="l-at-key">Tactical Score</span><span className="l-at-val green">9.4 / 10</span></div>
                <div className="l-at-row"><span className="l-at-key">System Overlap</span><span className="l-at-val">87%</span></div>
                <div className="l-at-glow" />
              </div>
            </div>

            {/* Agent 04 */}
            <div className="l-agent-row l-reverse">
              <div className="l-agent-info">
                <div className="l-agent-num" style={{ color: "#ff5555" }}>04 · Monitoring Agent</div>
                <h3 className="l-agent-title">24/7 TARGET WATCH</h3>
                <p className="l-agent-desc">
                  Watches your shortlist around the clock. Sends instant delta alerts when something shifts
                  — contract updates, rival scouts spotted, clubs entering financial trouble.
                </p>
              </div>
              <div className="l-agent-terminal">
                <div className="l-at-header">
                  <div className="l-at-header-left">
                    <div className="l-at-dot red" />
                    <span className="l-at-agent-label">Monitor</span>
                  </div>
                  <div className="l-at-status red">● 3 Alerts</div>
                </div>
                <div className="l-at-row"><span className="l-at-key">Contract</span><span className="l-at-val gold">Expiry in 6mo</span></div>
                <div className="l-at-row"><span className="l-at-key">Rival Activity</span><span className="l-at-val red">Wolves scouted</span></div>
                <div className="l-at-row"><span className="l-at-key">Club Finances</span><span className="l-at-val red">FFP breach risk</span></div>
                <div className="l-at-row"><span className="l-at-key">Window</span><span className="l-at-val gold">32 days left</span></div>
                <div className="l-at-row"><span className="l-at-key">Priority</span><span className="l-at-val red">ACT NOW</span></div>
                <div className="l-at-glow red" />
              </div>
            </div>
          </div>
        </section>

        {/* ── PIPELINE ── */}
        <section className="l-pipeline-section l-section-heavy" id="pipeline">
          <div className="l-container">
            <div className="l-section-label l-reveal" style={{ justifyContent: "center" }}>Architecture</div>
            <h2 className="l-pipeline-heading l-reveal">QUERY → DOSSIER IN SECONDS</h2>
            <div className="l-pipeline-track">
              {[
                {
                  num: "01", title: "NATURAL LANGUAGE QUERY",
                  desc: "The sporting director describes what they need. No filters, no dropdowns, no SQL.",
                  tags: [{ label: "Gemini 2.5 Flash", hl: true }, { label: "Google AI" }],
                },
                {
                  num: "02", title: "AGENT ORCHESTRATION",
                  desc: "LangGraph coordinates four agents in parallel — each reasons, searches, and scores independently.",
                  tags: [{ label: "LangGraph", hl: true }, { label: "Python" }, { label: "FastAPI" }],
                },
                {
                  num: "03", title: "VECTOR DATA RETRIEVAL",
                  desc: "RAG pipelines pull from StatsBomb events, FBref biographies, and Transfermarkt fee comparisons.",
                  tags: [{ label: "Chroma" }, { label: "StatsBomb", hl: true }],
                },
                {
                  num: "04", title: "LIVE REASONING STREAM",
                  desc: "Every agent step streams to the UI via SSE. Watch the system think in real time.",
                  tags: [{ label: "SSE" }, { label: "Next.js 14", hl: true }, { label: "Tailwind" }],
                },
                {
                  num: "05", title: "DOSSIER EXPORT",
                  desc: "Player dossier cards with fit scores, valuations, and risk flags. One-click PDF.",
                  tags: [{ label: "pdfkit" }, { label: "One-Click" }],
                },
              ].map((step) => (
                <div key={step.num} className="l-pipe-step">
                  <div className="l-pipe-num">{step.num}</div>
                  <div className="l-pipe-body">
                    <h3>{step.title}</h3>
                    <p>{step.desc}</p>
                    <div className="l-pipe-tags">
                      {step.tags.map((t) => (
                        <span key={t.label} className={`l-pipe-tag${t.hl ? " hl" : ""}`}>{t.label}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── TECH STRIP ── */}
        <div className="l-tech-strip l-section-glass">
          <div className="l-container l-reveal">
            <div className="l-tech-label">BUILT ON</div>
            <div className="l-tech-pills">
              {["LangGraph", "Gemini 2.5 Flash", "Chroma", "StatsBomb", "FastAPI", "Next.js 14", "Tailwind CSS", "Google AI"].map((t) => (
                <span
                  key={t}
                  className={`l-tech-pill${t === "Gemini 2.5 Flash" || t === "Google AI" ? " accent" : ""}`}
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* ── CTA ── */}
        <section className="l-cta-section">
          <div className="l-cta-inner l-reveal">
            <h2>
              <span className="l-dim">Stop Scouting.</span>
              <br />
              <span className="l-glow">Start Knowing.</span>
            </h2>
            <p>Built for sporting directors who can&apos;t afford to be second.</p>
            <div className="l-cta-buttons">
              <Link href="/app" className="l-btn l-btn-primary">
                ENTER THE APP
              </Link>
              <a
                href="https://github.com/girish-j04/scoutr"
                target="_blank"
                rel="noopener noreferrer"
                className="l-btn l-btn-outline"
              >
                VIEW ON GITHUB
              </a>
            </div>
          </div>
        </section>

        {/* ── FOOTER ── */}
        <footer className="l-footer l-section-glass">
          <span>ScoutR © 2025 — Agentic Transfer Intelligence</span>
          <div className="l-foot-links">
            <a href="https://github.com/girish-j04/scoutr" target="_blank" rel="noopener noreferrer">GitHub</a>
            <Link href="/app">App</Link>
          </div>
        </footer>

      </div>
    </div>
  );
}
