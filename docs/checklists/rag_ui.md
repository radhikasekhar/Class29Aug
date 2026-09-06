# rag_ui Checklist

Main progress tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate (Repeat for Every Task)

Before checking off **each** task below, complete this sequence:

- [ ] Add or update a focused automated test proving the task works.
- [ ] Run the focused test successfully.
- [ ] Run an `AppTest` or Compose-backed check whenever user-visible behavior changes.
- [ ] Review the result and fix failures before marking the task complete.
- [ ] Only then begin the next task or section.

## Foundation

- [ ] Create the Streamlit application and settings loader.
- [ ] Add API and LLM provider configuration.
- [ ] Store chat history with `st.session_state`.
- [ ] Validate required settings and disable unavailable provider options.
- [ ] Keep API keys server-side and never expose them in the browser or chat history.

## Retrieval and Prompting

- [ ] Validate question input and prevent empty submissions.
- [ ] Map all sidebar controls to the documented search request schema.
- [ ] Apply retrieval filters before building the grounded prompt.
- [ ] Limit retrieved context to the configured context budget.
- [ ] Preserve source identifiers and locators while assembling prompt context.

## Chat Experience

- [ ] Add provider, model, top-k, chunk-type, collection, and temperature controls.
- [ ] Submit vector or hybrid search requests to `rag_api`.
- [ ] Display retrieval and provider failures clearly.
- [ ] Build grounded prompts from retrieved chunks.
- [ ] Stream answers from Ollama or OpenAI.
- [ ] Render expandable citations with document name, page, and chunk text.
- [ ] Support a no-results state with a clear next action.
- [ ] Prevent answer submission while a response is actively streaming.
- [ ] Handle network failures, provider failures, and partial streams without losing chat history.

## Accessibility and Release

- [ ] Provide clear labels for all controls and keyboard-accessible chat actions.
- [ ] Ensure citations remain readable at narrow desktop and mobile viewport widths.
- [ ] Avoid rendering untrusted source Markdown or HTML as executable content.
- [ ] Document local startup, supported providers, and troubleshooting steps.

## Verification

- [ ] Add `streamlit.testing.v1.AppTest` tests for controls and session state.
- [ ] Mock API and LLM responses to test request payloads and token streaming.
- [ ] Test citation rendering and error states.
- [ ] Add a Compose-backed UI test using fixture search results.
- [ ] Verify a question produces a grounded answer with page-level citations.
- [ ] Test no-results, slow-stream, cancelled-stream, and provider-failure states.
- [ ] Test that control changes produce the expected API payload.
- [ ] Run `pytest rag_ui/tests` successfully.