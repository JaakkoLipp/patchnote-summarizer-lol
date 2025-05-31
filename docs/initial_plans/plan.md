# League of Legends patch-note summarizer

## Elevator Pitch

> “Tell me what changed in League of Legends since **<date I last played>**.”

## Motivation

League of Legends is a live service e-sports game with biweekly updates, which can have a major impact on how you approach the gameplay.
It's crucial to stay up to date on the latest changes, this is why i wanted to create a simple tool to quickly get a returning player up and running without having to read pages of previous patch notes.

## Approach

- Scrape html patch-note page and store in local db.
- Use AI LLM to make a user friendly short summary of the changes.
- Let user in web UI pick a date when they last played, and then recieving a short summary on the most important information.

---

## Target User

| Segment                           | Problem they have                           | Why this app helps           |
| --------------------------------- | ------------------------------------------- | ---------------------------- |
| Returning LoL player              | Doesn’t want to read 8 000‑word patch notes | Gets a 30‑second digest      |
| Esports analyst / content creator | Needs quick reference for video/stream      | Instant summary & share link |

## Feasibility Notes

- **Riot ToS check**: scraping allowed for non‑commercial informational use (see “Legal Jibber Jabber”, last reviewed 2024‑09‑12).
- **Rate limits**: plan to poll index page once per day; cache raw HTML in object storage.
- **Tech spike**: one‑off script successfully fetched Patch 14.10 on 2025‑05‑30.

## Success Metric(s)

| Category      | Metric                                                     | Target       |
| ------------- | ---------------------------------------------------------- | ------------ |
| **Technical** | 95‑th percentile API latency                               | < 2 s        |
| **Product**   | Users who click “Copy link”                                | ≥ 3 per week |
| **Quality**   | Accuracy of champion change bullets vs manual ground truth | ≥ 90 %       |
