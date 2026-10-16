# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2026-10-16

### Added
- T-35 "Mina spel" backend: bets API (`POST /api/bets`, `GET /api/bets`, settle), with rows and price computed server-side, per-horse `422` validation errors, SQLite store, protected by API key.
- K-35 manual odds/streck snapshots: `POST /api/snapshots` (`source=manual` only, full field required, phase `pre`/`final`, `minutesToStart`); snapshot history is kept and settlement uses the `final` rows.

### Fixed
- Guard fix: stronger test ensuring no automatic collection; `horseName` is now filled server-side.
