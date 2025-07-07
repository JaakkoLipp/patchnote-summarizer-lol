"use client";
import Card from "./card";

export default function Home() {
  return (
    <div
      id="main"
      style={{
        padding: "20px",
        textAlign: "center",
        marginTop: "20%",
      }}
    >
      <h1 id="title" style={{ margin: "10px 0" }}>
        W.H.I.Le.
      </h1>
      <p style={{ fontStyle: "italic" }}>What Happened In League?</p>
      <br />
      <hr
        style={{
          border: "none",
          borderTop: "2px solid #444",
          margin: "10px 0",
          maxWidth: "50%",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      />
      <p>last played in:</p>
      <br />
      <input
        type="date"
        style={{
          border: "none",
          borderRadius: "6px",
          padding: "10px 14px",
          fontSize: "16px",
          outline: "none",
          background: "#27272a",
          color: "#f4f4f5",
          boxShadow: "none",
          transition: "background 0.2s, color 0.2s",
        }}
        onChange={async (e) => {
          const date = e.target.value;
          console.log(date);
        }}
      />
      <br />
      <Card
        title="Patch 15.12"
        description="Key changes and updates in this patch."
        className="my-4"
      >
        <ul>
          <li>Champion balance updates</li>
          <li>Item adjustments</li>
          <li>Bug fixes and improvements</li>
        </ul>
      </Card>
      <Card
        title="Patch 15.11"
        description="Key changes and updates in this patch."
        className="my-4"
      >
        <ul>
          <li>Champion balance updates</li>
          <li>Item adjustments</li>
          <li>Bug fixes and improvements</li>
        </ul>
      </Card>
      <Card
        title="Patch 15.10"
        description="Key changes and updates in this patch."
        className="my-4"
      >
        <ul>
          <li>Champion balance updates</li>
          <li>Item adjustments</li>
          <li>Bug fixes and improvements</li>
        </ul>
      </Card>
    </div>
  );
}
