from logging.config import fileConfig
from pathlib import Path
import logging
import sox
import argparse


if __name__ == "__main__":
    try:
        fileConfig("logging.conf")
    except:
        pass

    parser = argparse.ArgumentParser()
    parser.add_argument("--audioset_root")
    parser.add_argument("--output_dir")
    args = parser.parse_args()

    audioset_root = Path(args.audioset_root)
    output_dir = Path(args.output_dir)

    if not output_dir.exists():
        output_dir.mkdir()

    files = map(Path, audioset_root.glob("**/*.flac"))

    for file in files:
        trf = sox.Transformer()
        output_fname = str(output_dir / Path(file.stem)) + ".wav"
        trf.build(str(file), output_fname)
