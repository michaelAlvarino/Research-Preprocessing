from pathlib import Path
from scipy.io.wavfile import read, write
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import sox
import logging
import argparse
import glob
np.random.seed(42)


parser = argparse.ArgumentParser()

parser.add_argument("--url",
                    help="url to tar gzip'd data path, ex: " +
                    "http://homepages.inf.ed.ac.uk/jyamagis/release/VCTK-Corpus.tar.gz",
                    default="http://homepages.inf.ed.ac.uk/jyamagis/release/VCTK-Corpus.tar.gz")
parser.add_argument("--data_dir_path",
                    help="path to data directory, will be created if non-existent, ex: data",
                    default="data")
parser.add_argument("--log_level",
                    help="logging level",
                    default="INFO")


def main():
    logging.info("hello world")
    kitchen_01 = Path("data/DEMAND/DKITCHEN/ch11.wav")
    vctk_01 = Path("data/VCTK-Corpus/wav48/p225/p225_001.wav")
    cbn = sox.Combiner()
    cbn.build([str(kitchen_01), str(vctk_01)], "data/output/out1.wav", "mix")


def n_random_seconds_of(n: int, source: Path):
    logging.debug(f"sampling {n} seconds from {source}")
    rate, data = read(source)
    logging.debug(f"info: rate = {rate}, data shape = {data.shape}")
    max_random_range = data.shape[0] - rate * n
    random_start = np.random.randint(0, high=max_random_range)
    end = random_start + n * rate
    return data[random_start: end]


def n_random_continous_samples(n: int, data: np.ndarray):
    high = data.shape[0] - n - 1
    start = np.random.randint(0, high)
    end = start + n
    logging.debug(f"start: {start}, end: {high}")
    return data[start: end], start, end


def combine(category: str,
            noise_channel: str,
            noise_dir: Path,
            noise_fname: Path,
            clip_dir: Path,
            clip_fname: Path,
            output_dir: Path):
    clip_rate, clip_data = read(clip_dir / clip_fname)
    noise_rate, noise_data = read(noise_dir / noise_fname)
    trimmed_noise, start, end = n_random_continous_samples(clip_data.shape[0], noise_data)
    multi_channel = np.stack([trimmed_noise, clip_data]).T
    output = output_dir / Path(f"{category}_{noise_channel}_{start}_{end}_{clip_fname}")
    logging.debug(f"writing to {output}")
    write(output, clip_rate, multi_channel)


if __name__ == "__main__":
    """
    DEMAND and vctk files were sampled at 48000 / second

    Types of noise:
    1. Human - Restoraunt
    2. Animals - Park
    3. Unidentifiable Things - Station
    4. Natural - River
    5. Loud Background - Traffic
    """
    args = parser.parse_args()
    logging.basicConfig(format=logging.BASIC_FORMAT, level=args.log_level)

    data_dir = Path(args.data_dir_path)
    demand_dir = data_dir / Path("DEMAND")
    vctk_corpus = data_dir / Path("VCTK-Corpus")
    output_dir = data_dir / Path("output")
    demand_categories = list(map(Path, ["PRESTO", "NPARK", "PSTATION", "NRIVER", "STRAFFIC"]))

    if not output_dir.exists():
        output_dir.mkdir()

    search_str = str(vctk_corpus / Path("wav48") / Path("**/*.wav"))
    clips = glob.glob(search_str)

    logging.info("creating threadpool")
    # ThreadPoolExecutor defaults to number of processors * 5
    with ThreadPoolExecutor() as executor:
        for clip in clips:
            logging.info(f"adding noise to clip {clip}")
            for category in demand_categories:
                clip_path = Path(clip)
                # all channels sound the same to me, select them randomly
                channel = f"ch{np.random.randint(1, 17):02d}.wav"
                executor.submit(combine,
                                category=str(category),
                                noise_channel=channel[:4],
                                noise_dir=demand_dir / category,
                                noise_fname=Path(channel),
                                clip_dir=Path(clip).parent,
                                clip_fname=Path(clip).name,
                                output_dir=output_dir)
        logging.info("preprocessing complete.")
