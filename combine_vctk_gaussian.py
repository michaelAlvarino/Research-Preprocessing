from pathlib import Path
from scipy.io.wavfile import read, write
from concurrent.futures import ThreadPoolExecutor

import argparse
import numpy as np
import logging
from logging.config import fileConfig


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("VCTK_DIR")
    parser.add_argument("OUTPUT_DIR")
    return parser.parse_args()


def make_noisy(path, intensity, output_dir):
            rate, data = read(path)
            std = np.std(data) * intensity
            mean = np.mean(data) * intensity - std
            noise = np.random.normal(
                    loc=mean,
                    scale=std,
                    size=data.shape)
            noisy = np.vstack((data, noise)).T
            output_f = "{}_intensity_{}_gaussian_{}_{}.wav".format(path.stem, intensity, mean, std)
            write(output_dir / Path(output_f), rate, noisy)


if __name__ == "__main__":
    try:
        fileConfig("logging.conf")
    except Exception:
        logging.basicConfig(format=logging.BASIC_FORMAT, level="INFO")
    args = parse_args()
    vctk_root = Path(args.VCTK_DIR)
    output_root = Path(args.OUTPUT_DIR)

    if not output_root.exists():
        output_root.mkdir()

    vctk_files = list(map(Path, vctk_root.glob("**/*.wav")))

    with ThreadPoolExecutor() as pool:
        for i, path in enumerate(vctk_files):
            for intensity in range(10):
                pool.submit(
                        make_noisy,
                        path,
                        10 ** -intensity,
                        output_root
                        )
            if i % 1000 == 0:
                logging.info("processed {} files, next is {}".format(i, vctk_files[i + 1]))
