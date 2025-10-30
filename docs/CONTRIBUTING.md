# Contributing & Maintenance Notes

ChoopScoop is developed primarily as a **personal portfolio project** by Jerusha Gray.  
While it’s not an open-collaboration project, this document outlines structure and standards for future maintenance or internal extension.

---

## 🧱 Project Principles

- **Keep it simple.** No unnecessary abstractions or external dependencies.
- **Optimize for clarity.** Readable, documented code > “clever” code.
- **Version intentionally.** Every release (v2.1, v2.2, etc.) must have documented patch notes.
- **Maintain async purity.** All async operations use Python’s native asyncio (no Twisted/Scrapy).

---

## 🧩 Development Guidelines

1. **Run linting and type checks**
   ```bash
   pylint choopscoop_site_auditor_v2.1.py
   mypy choopscoop_site_auditor_v2.1.py
   ```

2. **Keep dependencies lean**
   - Prefer stdlib and Playwright.
   - Avoid introducing frameworks that conflict with asyncio.

3. **Documentation updates**
   - Update relevant `.md` files under `/docs/` with each release.
   - Maintain versioned quick-start and delivery summaries.

4. **Testing**
   - Basic smoke tests for crawl and export functions.
   - Validate JSON and CSV output for structure integrity.

---

## 🧠 Ownership

Developed and maintained by **Jerusha Gray**  
IdeoPraxis Collective LLC — DBA GetFunnelCaked
