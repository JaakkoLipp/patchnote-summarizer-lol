import React, { useState } from "react";

function Content({ content }) {
  if (Array.isArray(content)) {
    return (
      <ul className="list">
        {content.map((line, i) => (
          <li key={i}>{line}</li>
        ))}
      </ul>
    );
  }
  if (typeof content === "object" && content !== null) {
    const { content: inner, note, ...rest } = content;
    return (
      <div className="stack">
        {inner && <Content content={inner} />}
        {note && <div className="note">{note}</div>}
        {Object.keys(rest).length > 0 && (
          <pre className="json">{JSON.stringify(rest, null, 2)}</pre>
        )}
      </div>
    );
  }
  return <div>{String(content)}</div>;
}

export function Card({ title, content }) {
  const [open, setOpen] = useState(false);
  return (
    <div className={`card ${open ? "open" : ""}`}>
      <button className="card-header" onClick={() => setOpen((o) => !o)}>
        <span className="card-title">{title}</span>
        <span className="chev" aria-hidden>
          ▸
        </span>
      </button>
      {open && (
        <div className="card-body">
          <Content content={content} />
        </div>
      )}
    </div>
  );
}
