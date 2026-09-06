# rag_ui Checklist

Master tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate

Before marking any task complete, add or update its focused automated test, run it successfully, and run an `AppTest` or Compose-backed check for user-visible behavior. Do not begin the next task until those checks pass.

## P0 Setup

- [x] Create the `rag_ui/` project directory and this checklist.
- [x] Add the shared `ui` service placeholder to `docker-compose.yml`.
- [x] Review the shared UI and API configuration in `.env.example`.
- [x] Add project packaging, dependency declaration, and test layout.

## Planned Work

- [x] Create the Streamlit app and settings loader.
- [x] Add chat controls, search integration, streaming, and citations.
- [x] Add `AppTest` coverage for UI behavior and failures.