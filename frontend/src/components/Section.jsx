import React from "react";
import { Card } from "./card/Card.jsx";

function normalizeToEntries(data) {
  // Accept object of key->value or array of strings; return array of {title, content}
  if (!data) return [];
  if (Array.isArray(data)) {
    return data.map((v, i) => ({ title: `Item ${i + 1}`, content: v }));
  }
  if (typeof data === "object") {
    return Object.entries(data).map(([k, v]) => ({ title: k, content: v }));
  }
  return [{ title: "Content", content: String(data) }];
}

export default function Section({ data }) {
  const entries = normalizeToEntries(data);
  if (!entries.length) return <div className="muted">No data</div>;
  return (
    <div className="grid">
      {entries.map((e, idx) => (
        <Card key={idx} title={e.title} content={e.content} />
      ))}
    </div>
  );
}
