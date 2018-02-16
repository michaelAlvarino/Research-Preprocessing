from pathlib import Path
from scipy.io.wavfile import read, write
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import logging
from logging.config import fileConfig


def make_noisy(path, intensity, output_dir):
            rate, data = read(path)
            std = np.std(data) * intensity
            mean = np.mean(data) * intensity - std
            noise = np.random.normal(
                    loc=mean,
                    scale=std,
                    size=data.shape)
            noisy = np.vstack((data, noise)).T
            output_f = f"{path.stem}_intensity_{intensity}_gaussian_{mean}_{std}.wav"
            write(output_dir / Path(output_f), rate, noisy)


if __name__ == "__main__":
    try:
        fileConfig("logging.conf")
    except:
        pass
    info = logging.info
    debug = logging.debug

    data_dir = Path("data")
    vctk_root = data_dir / Path("VCTK-Corpus")
    output_root = data_dir / Path("output") / Path("gaussian_noise")

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
                info(f"processed {i} files, next is {vctk_files[i + 1]}")
