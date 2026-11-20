# Contributing Guidelines & Engineering Standards

Welcome to **Slimefun-Texture-Drake**! This repository is part of DrakesCraft Labs: Resource pack de Slimefun para DrakesCraft (327 item definitions y 17 addons).

---

## 🏛️ Code of Conduct & Mutual Respect

All contributors, reviewers, and maintainers are required to follow our [Code of Conduct](CODE_OF_CONDUCT.md).
We expect all discussions in issues and pull requests to remain professional, constructive, and technically grounded.
**Insults, demanding entitlement, toxic behavior, or harassment will result in immediate thread locking and account blocking.**

---

## 📋 Issue-First Workflow (Mandatory)

Before opening a Pull Request:
1. **Search existing issues** to avoid duplicate proposals.
2. **Open an Issue first** describing the bug with logs and environment details, or detailing the proposed feature before writing code.
3. **Wait for maintainer approval** before undertaking large refactors or adding dependencies. Unsolicited massive PRs will be closed without review.

---

## 🛡️ SRE Golden Rule: Zero Production Disruption & Anti-Dupe

* **Zero Item Loss**: Any changes interacting with BlockStorage, PDC, item serialization, or databases must guarantee 100% data integrity and zero duplication vulnerabilities.
* **Asynchronous Execution**: Never block the Spigot main tick thread with heavy database or network calls.
* **Language Standards**: All in-game GUI titles, item lores, and player-visible messages must be written in **English**.

---

## 🛠️ Stack & Quality Standards (Resource Pack / JSON / Textures)

* **Quality Gates**:
  - Verification: `JSON schema validator on assets/models` must pass cleanly.
  - Linting: `jsonlint assets/**/*.json` must produce zero errors.
* **Clean Git History**: Commits must follow Conventional Commits (`feat: ...`, `fix: ...`, `docs: ...`).

---

## 🤖 AI-Assisted and Agent Contributions

We enforce a strict **Zero-Slop Policy**:
* If an AI was used, disclose it in the PR description.
* The human contributor assumes **100% engineering responsibility** for every line of code submitted.
* Fabricated Bukkit/Spigot methods, hallucinated Slimefun APIs, non-compiling boilerplate, or unchecked AI diffs will be closed immediately as spam.
* Detailed requirements for automated tools and AI agents are documented in [AGENTS.md](AGENTS.md).
