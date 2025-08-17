import React, { useEffect, useMemo, useState } from "react";
import Section from "./components/Section.jsx";
import { Tabs } from "./components/Tabs.jsx";

const API = "/api"; // proxied to FastAPI by vite.config.js

async function fetchJSON(path) {
  const res = await fetch(`${API}${path}`, {
    cache: "no-store",
    headers: { "Cache-Control": "no-store" },
  });
  if (!res.ok) throw new Error(`Fetch failed: ${res.status}`);
  return res.json();
}

export default function App() {
  const [patchVersion, setPatchVersion] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [champions, setChampions] = useState({});
  const [items, setItems] = useState({});
  const [other, setOther] = useState({});
  const [arena, setArena] = useState({ arena: {}, mentions: [] });
  const [tagline, setTagline] = useState("");
  const [aiSummary, setAiSummary] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [highlights, setHighlights] = useState({
    image: null,
    alt: "",
    caption: "",
  });
  const displayVersion = useMemo(() => {
    if (!patchVersion) return "";
    return String(patchVersion).replace(/-/g, ".");
  }, [patchVersion]);
  const [availableVersions, setAvailableVersions] = useState([]);

  useEffect(() => {
    let mounted = true;
    async function load() {
      try {
        setLoading(true);
        setError("");
        // Fetch aggregated bundle for latest + auxiliary versions list
        const [bundle, vs] = await Promise.all([
          fetchJSON("/bundle/"),
          fetchJSON("/versions/"),
        ]);
        if (!mounted) return;
        setChampions(bundle?.champions || {});
        setItems(bundle?.items || {});
        setOther(bundle?.other || {});
        const arenaData = bundle?.arena || { arena: {}, mentions: [] };
        setArena({
          arena: arenaData.arena || {},
          mentions: arenaData.mentions || [],
        });
        setTagline(bundle?.tagline || "");
        setHighlights(
          bundle?.highlights || { image: null, alt: "", caption: "" }
        );
        setPatchVersion(bundle?.version || "");
        setAvailableVersions(
          (vs?.versions || []).map((v) => v.replace(/-/g, "."))
        );
      } catch (e) {
        if (!mounted) return;
        setError(e.message);
      } finally {
        if (mounted) setLoading(false);
        // Lazy-load AI summary in the background
        if (mounted) {
          try {
            setAiLoading(true);
            const sm = await fetchJSON("/summary/");
            if (mounted) setAiSummary(sm?.summary || "");
          } catch (e) {
            if (mounted) setAiSummary("");
          } finally {
            if (mounted) setAiLoading(false);
          }
        }
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  // Load a specific version when user selects it
  const onSelectVersion = async (dotted) => {
    try {
      setLoading(true);
      setError("");
      // clear AI summary but keep page responsive; tagline will reload with core data
      setAiSummary("");
      setAiLoading(true);
      const dashed = String(dotted).replace(/\./g, "-");
      const bundle = await fetchJSON(`/bundle/${dashed}`);
      setPatchVersion(dashed);
      setChampions(bundle?.champions || {});
      setItems(bundle?.items || {});
      setOther(bundle?.other || {});
      const arenaData = bundle?.arena || { arena: {}, mentions: [] };
      setArena({
        arena: arenaData.arena || {},
        mentions: arenaData.mentions || [],
      });
      setTagline(bundle?.tagline || "");
      setHighlights(
        bundle?.highlights || { image: null, alt: "", caption: "" }
      );
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
      // Fetch summary in the background
      try {
        const dashed = String(dotted).replace(/\./g, "-");
        const sm = await fetchJSON(`/summary/${dashed}`);
        setAiSummary(sm?.summary || "");
      } catch (e) {
        setAiSummary("");
      } finally {
        setAiLoading(false);
      }
    }
  };

  useEffect(() => {
    if (displayVersion) {
      document.title = `Patchnote Summarizer - ${displayVersion}`;
    } else {
      document.title = `League of Legends Patchnote Summarizer`;
    }
  }, [displayVersion]);

  const tabs = useMemo(
    () => [
      {
        id: "highlights",
        label: "Highlights",
        content: (
          <div>
            {highlights?.image ? (
              <div>
                <img
                  src={highlights.image}
                  alt={highlights.alt || "Patch Highlights"}
                  style={{
                    width: "100%",
                    height: "auto",
                    borderRadius: 8,
                    border: "1px solid #1f2937",
                  }}
                />
                {highlights.caption && (
                  <p className="" style={{ marginTop: 8 }}>
                    {highlights.caption}
                  </p>
                )}
              </div>
            ) : (
              <div className="status">No highlights image found.</div>
            )}
          </div>
        ),
      },
      {
        id: "champions",
        label: "Champions",
        content: <Section data={champions} />,
      },
      { id: "items", label: "Items", content: <Section data={items} /> },
      {
        id: "arena",
        label: "Arena",
        content: (
          <>
            <h3 style={{ marginBottom: 8 }}>Arena</h3>
            <Section data={arena.arena} />
            {!!arena.mentions?.length && (
              <div style={{ marginTop: 16 }}>
                <h4 style={{ marginBottom: 8 }}>
                  Arena, all changes (See "other" tab)
                </h4>
                <Section
                  data={{
                    Mentions: arena.mentions.map(
                      (m) => `${m.context}: ${m.text}`
                    ),
                  }}
                />
              </div>
            )}
          </>
        ),
      },
      { id: "other", label: "Other", content: <Section data={other} /> },
    ],
    [highlights, champions, items, other, arena]
  );

  return (
    <div className="container">
      <header className="header">
        <h1>League of Legends Patchnote Summarizer</h1>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          {!!availableVersions.length && (
            <select
              aria-label="Select patch version"
              value={displayVersion || ""}
              onChange={(e) => onSelectVersion(e.target.value)}
              className="version-select"
              disabled={loading}
            >
              {availableVersions.map((v) => (
                <option key={v} value={v}>
                  {v}
                </option>
              ))}
            </select>
          )}
        </div>
      </header>
      {(!!tagline || !!aiSummary || aiLoading) && (
        <div className="tagline" title="Summaries">
          {tagline}
          {aiLoading && (
            <span className="muted" style={{ marginLeft: 8 }}>
              — Generating AI summary…
            </span>
          )}
          {!aiLoading && aiSummary && (
            <span className="muted" style={{ marginLeft: 8 }}>
              — {aiSummary}
            </span>
          )}
        </div>
      )}

      {loading && <div className="status">Loading…</div>}
      {error && <div className="status error">{error}</div>}

      {!loading && !error && <Tabs tabs={tabs} />}

      <footer className="footer">
        <a
          className="source-link"
          href="https://www.leagueoflegends.com/en-us/news/game-updates/"
          target="_blank"
          rel="noopener noreferrer"
        >
          Official patch notes — Riot Games
        </a>
        <span className="muted"> · </span>
        <a
          className="source-link"
          href="https://jaalip.com/"
          target="_blank"
          rel="noopener noreferrer"
        >
          JaaLip.com
        </a>
      </footer>
    </div>
  );
}
