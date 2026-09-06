# chunker Checklist

Main progress tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate (Repeat for Every Task)

Before checking off **each** task below, complete this sequence:

- [ ] Add or update a focused automated test proving the task works.
- [ ] Run the focused test successfully.
- [ ] Run shared-contract validation whenever output structure changes.
- [ ] Review the result and fix failures before marking the task complete.
- [ ] Only then begin the next task or section.

## Foundation

- [ ] Create the CLI entry point and settings loader.
- [ ] Define the supported input and outbox directory conventions.
- [ ] Validate CLI arguments and report actionable failures.
- [ ] Load model, chunk-size, overlap, and output-format settings from environment variables.
- [ ] Record chunker version, model names, and prompt version in each manifest.

## Input Safety and Lifecycle

- [ ] Calculate the source SHA-256 before processing.
- [ ] Detect duplicate source files and support explicit reprocessing.
- [ ] Isolate each document failure so one bad file does not stop a batch.
- [ ] Write structured error details to a per-document failure record.
- [ ] Write outputs atomically so incomplete JSONL files are never ingested.

## Document Processing

- [ ] Convert PDF, DOCX, and HTML with Docling.
- [ ] Pass TXT documents through as normalized Markdown.
- [ ] Extract title, page count, and source metadata.
- [ ] Preserve page, character-offset, and heading-path provenance.
- [ ] Normalize whitespace and remove conversion-only boilerplate without losing provenance.
- [ ] Define behavior for scanned PDFs, empty documents, encrypted files, and unsupported formats.

## Artifacts

- [ ] Create semantic chunks with Chonkie.
- [ ] Generate contextual prefixes with Ollama.
- [ ] Generate map-reduce summaries with Ollama.
- [ ] Generate QA pairs and factoids with Ollama.
- [ ] Add the RAPTOR interface stub, then implement RAPTOR in P4.
- [ ] Write versioned JSONL chunks and per-document manifests.
- [ ] Include the parent semantic-chunk reference on derivative artifacts.
- [ ] Include embedding-provider and generator metadata in every output record.
- [ ] Enforce configured token-size limits and define overlap behavior.

## Observability and Release

- [ ] Log document identifiers, stage timings, artifact counts, and failures without logging source content.
- [ ] Report a run summary with processed, skipped, failed, and emitted counts.
- [ ] Document the CLI invocation, configuration, and supported file types.
- [ ] Verify output is reproducible with fixed models, settings, and fixtures.

## Verification

- [ ] Add unit tests for routing, conversion, provenance, and chunk boundaries.
- [ ] Add fixture tests for PDF, HTML, and TXT processing.
- [ ] Validate JSONL envelopes and manifests against shared contracts.
- [ ] Verify every output chunk has type, locator, and source lineage metadata.
- [ ] Test malformed, empty, scanned, and unsupported document handling.
- [ ] Test atomic output behavior when conversion or generation fails.
- [ ] Run `pytest chunker/tests` successfully.