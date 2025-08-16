import React, { useState } from "react";

export function Tabs({ tabs }) {
  const [active, setActive] = useState(tabs[0]?.id);
  return (
    <div>
      <div className="tabs">
        {tabs.map((t) => (
          <button
            key={t.id}
            className={`tab ${active === t.id ? "active" : ""}`}
            onClick={() => setActive(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>
      <div className="tab-content">
        {tabs.find((t) => t.id === active)?.content}
      </div>
    </div>
  );
}
