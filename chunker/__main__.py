import argparse
from pathlib import Path

from chunker.pipeline import Provider, SUPPORTED_TYPES, process_document
from chunker.settings import Settings
from shared.models import ChunkType


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--chunk-types", default="semantic")
    args = parser.parse_args()
    settings = Settings()
    input_dir, output_dir = args.input or settings.data_input, args.out or settings.data_output
    chunk_types = {ChunkType(value.strip().rstrip("s")) if value.strip().rstrip("s") != "qa_pair" else ChunkType.QA_PAIR for value in args.chunk_types.split(",")}
    provider = Provider(settings)
    for source in input_dir.iterdir():
        if source.is_file() and source.suffix.lower() in SUPPORTED_TYPES:
            print(process_document(source, output_dir, settings, provider, chunk_types))


if __name__ == "__main__":
    main()