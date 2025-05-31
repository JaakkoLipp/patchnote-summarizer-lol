# Architecture Vision (v2)

## High‑Level Diagram

see init_architecture.png

## Decision Table (update)

| Layer                   | Choice                              | Status | Rationale                                             |
| ----------------------- | ----------------------------------- | ------ | ----------------------------------------------------- |
| UI                      | **Next.js App Router**              | ✅     | SSR + SPA, easy Tailwind integration                  |
| API                     | **FastAPI**                         | ✅     | Python ecosystem & async support                      |
| Worker                  | **Standalone Python module**        | ✅     | Keeps scraper & summariser separate from request path |
| Storage – relational    | **PostgreSQL (local Docker)**       | ✅     | ACID joins, easy backups                              |
| Storage – blobs         | **MinIO (self‑hosted S3)**          | ✅     | S3‑compatible, runs in same Docker Compose            |
| LLM provider            | **OpenAI GPT‑4o**                   | ✅     | Best summary quality for now; env var key             |
| Container orchestration | **Docker Compose on localhost/VPS** | ✅     | Single‑node, minimal ops                              |
| Observability           | **Loki + Grafana**                  | ❓     | TBD depending on resource budget                      |

---

## Non‑Functional Requirements

| Area              | Target                                                |
| ----------------- | ----------------------------------------------------- |
| Latency p99       | < 3 s for `/since/{date}` when 24 months of patches   |
| Cold storage cost | < €1/month on local disk                              |
| Availability      | Single‑node ≈ 95 %                                    |
| Test coverage     | ≥ 80 % lines for backend modules                      |
| Security          | Secrets via `.env`; no external ingress except 80/443 |

---

## Open Questions

- Do we want a public API key for demo mode, or keep it local‑only?
- Which alerting mechanism (email vs. Discord webhook)
- Embed Grafana in the same Docker stack or run separately?
