import argparse
from pathlib import Path

from ingest_client.client import IngestClient


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outbox", type=Path, required=True)
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--state", type=Path, default=Path("data/ingest-state.json"))
    parser.add_argument("--batch-size", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    client = IngestClient(args.api, batch_size=args.batch_size)
    for path in sorted(args.outbox.glob("*.jsonl")):
        print(f"{path}: {client.ingest_file(path, args.state, args.dry_run)} chunks")


if __name__ == "__main__":
    main()