# Sprint 0 Plan

> _Sprint 0 goal: deliver an end‑to‑end walking skeleton that fetches one patch, stores it, summarises it, and serves it via `/patches`._

---

## Sprint Frame

| Field             | Value (edit)                                |
| ----------------- | ------------------------------------------- |
| **Sprint length** | 1 week                                      |
| **Capacity**      | 5 story points (\~1 SP ≈ 1 day)             |
| **Sprint Goal**   | Walking skeleton delivered + CI/CD in place |

---

## Stories Pulled Into Sprint 0

| ID     | Title                       | Points | Acceptance Criteria                                                                   |
| ------ | --------------------------- | ------ | ------------------------------------------------------------------------------------- |
| MVP‑01 | Detect new patch            | 1      | Given the Riot index fixture, the function returns the latest patch URL and number.   |
| MVP‑02 | Download & archive raw HTML | 1      | Raw HTML saved to `storage/raw/`, checksum verified, unit test asserts file exists.   |
| MVP‑03 | Clean & split sections      | 1      | `clean_html()` strips nav & ads; integration test snapshot matches approved Markdown. |
| MVP‑04 | Summarise one section       | 1      | OpenAI mocked test returns ≤6 bullet markdown.                                        |
| API‑01 | GET /patches (single)       | 1      | FastAPI route returns summary JSON when DB has one row; Postman test passes.          |

_Total = 5 SP_

---

## Definition of Done (DoD)

- [ ] Code merged to `main` behind PR
- [ ] Unit tests ≥ 80 % coverage
- [ ] GitHub Actions: lint + test pipeline green
- [ ] Docker Compose `up` starts API & Postgres locally
- [ ] README updated with local setup instructions

---

## Board Setup Checklist

1. Create **GitHub Project** → _Board: Sprint 0_.
2. Columns: **Backlog ▽ | In Progress | Review | Done**.
3. Enable automation: PR merged ⇒ moves card to **Done**.
4. Set **Milestone** `sprint0` and assign to every Issue.

---

## Ceremonies & Events

| When           | Duration           | Agenda                                     |
| -------------- | ------------------ | ------------------------------------------ |
| Kick‑off       | 30 min             | Confirm stories, estimates, risks          |
| Daily stand‑up | async Slack thread | Yesterday / Today / Blockers               |
| Demo + Retro   | 30 min             | Show walking skeleton, gather improvements |

---

## Burndown Chart Placeholder
