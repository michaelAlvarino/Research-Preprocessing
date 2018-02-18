from logging.config import fileConfig
from pathlib import Path
import logging
import argparse
import subprocess as sp


if __name__ == "__main__":
    try:
        fileConfig("logging.conf")
    except:
        logging.basicConfig(format=logging.BASIC_FORMAT, level="INFO")

    parser = argparse.ArgumentParser()
    parser.add_argument("--audioset_root")
    parser.add_argument("--output_dir")
    args = parser.parse_args()

    audioset_root = Path(args.audioset_root)
    output_dir = Path(args.output_dir)

    if not output_dir.exists():
        output_dir.mkdir()

    files = map(Path, audioset_root.glob("**/*.flac"))

    ffmpegpath = Path("/rigel/home/maa2282/Research-Preprocessing/ffmpeg")

    i = 0
    logging.info("starting...")
    for file in files:
        i += 1
        output_fname = str(output_dir / Path(file.stem)) + ".wav"
        if not Path(output_fname).exists() and not Path(output_fname).stem == "2H4PqZ5BQKg_30000_40000":
            sp.run([str(ffmpegpath), "-i", str(file), output_fname, "-y", "-loglevel", "quiet"])
        if i % 10000 == 0:
            logging.info("processed {} files".format(i))
