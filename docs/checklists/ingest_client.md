# ingest_client Checklist

Main progress tracker: [SPEC.md](../SPEC.md).

## End-of-Task Test Gate (Repeat for Every Task)

Before checking off **each** task below, complete this sequence:

- [ ] Add or update a focused automated test proving the task works.
- [ ] Run the focused test successfully.
- [ ] Run the mocked-API or running-API check whenever request behavior changes.
- [ ] Review the result and fix failures before marking the task complete.
- [ ] Only then begin the next task or section.

## Foundation

- [ ] Create the CLI entry point and API settings loader.
- [ ] Define outbox, state-file, batch-size, and dry-run options.
- [ ] Load API timeout, retry limit, and retry-delay settings from environment variables.
- [ ] Include client version and request correlation IDs in API calls.

## Outbox Validation

- [ ] Require a matching manifest for every JSONL document payload.
- [ ] Confirm the manifest SHA-256, output format version, and chunk counts.
- [ ] Validate source lineage, chunk type, and required model metadata.
- [ ] Quarantine invalid or incomplete outbox files with a reason.

## Ingestion Flow

- [ ] Read JSONL and manifest files from the outbox.
- [ ] Validate every envelope before making API requests.
- [ ] Upsert documents through `PUT /documents` using SHA-256.
- [ ] Submit chunks through `POST /chunks/bulk` in configurable batches.
- [ ] Record completed document hashes in resumable state.
- [ ] Implement retry and exponential-backoff handling.
- [ ] Support dry-run output without API mutations.
- [ ] Retry only transient failures; fail fast for validation and authorization errors.
- [ ] Avoid marking a document complete until every chunk batch succeeds.
- [ ] Support an explicit retry of failed documents without resending completed ones.

## Observability and Release

- [ ] Log document hash, batch number, response status, retry count, and failure reason.
- [ ] Produce a run summary with created, updated, skipped, failed, and retried counts.
- [ ] Document recovery steps for failed batches and corrupted state files.
- [ ] Confirm secrets are read from environment variables and never written to logs or state.

## Verification

- [ ] Add unit tests for validation, batching, retries, dry-run, and state recovery.
- [ ] Mock API transport to verify request payloads and error handling.
- [ ] Reject malformed JSONL without making a network request.
- [ ] Verify a repeated outbox ingestion creates no duplicate documents or chunks.
- [ ] Add a running-API integration test for document and chunk counts.
- [ ] Test transient API failures, non-retryable failures, partial batches, and state recovery.
- [ ] Test manifest/JSONL mismatch and quarantine behavior.
- [ ] Run `pytest ingest_client/tests` successfully.