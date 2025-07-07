"use client";
import React, { useState } from "react";

type CardProps = {
  title: string;
  description?: string;
  children?: React.ReactNode;
  className?: string;
};

const Card: React.FC<CardProps> = ({
  title,
  description,
  children,
  className,
}) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={`card${className ? ` ${className}` : ""}`}>
      <div
        className="card-header"
        style={{ cursor: "pointer", display: "flex", alignItems: "center" }}
        onClick={() => setCollapsed((c) => !c)}
      >
        <span style={{ marginRight: 8 }}>{collapsed ? "▶" : "▼"}</span>
        <h2 className="card-h2" style={{ margin: 0 }}>
          {title}
        </h2>
      </div>
      {!collapsed && (
        <>
          {description && <p className="card-p">{description}</p>}
          {children}
        </>
      )}
    </div>
  );
};

export default Card;
