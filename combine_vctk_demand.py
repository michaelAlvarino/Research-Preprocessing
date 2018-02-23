from pathlib import Path
from scipy.io.wavfile import read, write
from concurrent.futures import ThreadPoolExecutor
from wav_utils import n_random_continous_samples
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
parser.add_argument("--vctk_dir",
                    help="path to vctk directory, will be created if non-existent, ex: data",
                    default="data/VCTK")
parser.add_argument("--demand_dir",
        help="path to the demand directory",
        default="data/DEMAND")
parser.add_argument("--log_level",
                    help="logging level",
                    default="INFO")
parser.add_argument(
    "--output_dir",
    help="where to output the newly mixed files",
    default="OUTPUT")


def combine(category: str,
            noise_channel: str,
            noise_dir: Path,
            noise_fname: Path,
            clip_dir: Path,
            clip_fname: Path,
            output_dir: Path):
    clip_rate, clip_data = read(str(clip_dir / clip_fname))
    noise_rate, noise_data = read(str(noise_dir / noise_fname))
    trimmed_noise, start, end = n_random_continous_samples(clip_data.shape[0], noise_data)
    multi_channel = np.stack([trimmed_noise, clip_data]).T
    output = output_dir / Path("{}_{}_{}_{}_{}".format(category, noise_channel, start, end, clip_fname))
    logging.info("writing to {}".format(output))
    write(str(output), clip_rate, multi_channel)


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

    demand_dir = Path(args.demand_dir)
    vctk_corpus = Path(args.vctk_dir)
    output_dir = Path(args.output_dir)
    demand_categories = list(map(Path, ["PRESTO", "NPARK", "PSTATION", "NRIVER", "STRAFFIC"]))

    if not output_dir.exists():
        output_dir.mkdir()

    search_str = str(vctk_corpus / Path("wav48") / Path("**/*.wav"))
    clips = glob.glob(search_str)

    # logging.info("creating threadpool")
    # ThreadPoolExecutor defaults to number of processors * 5
    # with ThreadPoolExecutor(max_workers=5) as executor:
    logging.info("found {} clips in {}".format(len(clips), search_str))
    for clip in clips:
        logging.info("adding noise to clip {}".format(clip))
        for category in demand_categories:
            clip_path = Path(clip)
            # all channels sound the same to me, select them randomly
            channel = "ch{:02d}.wav".format(np.random.randint(1, 17))
            combine(category=str(category),
                    noise_channel=channel[:4],
                    noise_dir=demand_dir / category,
                    noise_fname=Path(channel),
                    clip_dir=Path(clip).parent,
                    clip_fname=Path(clip).name,
                    output_dir=output_dir)
    logging.info("preprocessing complete.")
