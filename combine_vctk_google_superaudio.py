from data_collection_utils import download
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging
import argparse
import sox
import pandas as pd


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
parser.add_argument("--n_samples_per_index",
                    help="number of samples to use from each sample category",
                    default=100)


def combine_vctk_with_audioset(
        vctk_fname: Path,
        audioset_fname: Path,
        output_fname: Path,
        input_volumes=[1.5, 0.3]):
    vctk_duration = sox.file_info.duration(str(vctk_fname))
    audioset_duration = sox.file_info.duration(str(audioset_fname))
    logging.debug(f"vctk duration: {vctk_duration}, audioset duration: {audioset_duration}")
    cbn = sox.Combiner()
    debug(f"Building file {output_fname} with volumes {input_volumes}")
    cbn.build([str(vctk_fname), str(audioset_fname)],
              str(output_fname),
              "mix",
              input_volumes)


def read_segments_file(fname: Path):
    dat = pd.read_csv(fname,
                      engine="python",
                      header=2,
                      skipinitialspace=True,
                      names=["ytid", "start", "end", "labels"])
    return dat.set_index("ytid")


def get_read_class_labels(fname: Path):
    download("http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv",
             class_labels_path)
    label_map = pd.read_csv(class_labels_path)
    return label_map.set_index("mid")


def get_labels(audioset: Path, segments: pd.DataFrame, label_map: pd.DataFrame):
    stem = audioset.stem.split("_")[0]
    labels = list(segments.loc[stem]["labels"].split(","))
    labels = list(map(lambda x: label_map.loc[x]["display_name"], labels))
    clean_labels = list(map(lambda x: x.replace(" ", "_"), labels))
    return clean_labels


def get_filename(labels: list, vctk_fname: Path, audioset_fname: Path):
    parts = [vctk_fname.stem, audioset_fname.stem] + labels
    joined = "_".join(parts) + ".wav"
    return Path(joined)


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(format=logging.BASIC_FORMAT, level=args.log_level)
    info = logging.info
    debug = logging.debug

    data_dir = Path(args.data_dir_path)
    audioset_root = data_dir / Path("AUDIOSET")
    vctk_root = data_dir / Path("VCTK-Corpus")
    output_root = data_dir / Path("output")

    if not output_root.exists():
        output_root.mkdir()

    audioset_files = [Path(x) for x in (audioset_root / Path("data")).glob("**/*.flac")]
    vctk_files = [Path(x) for x in (data_dir / Path("VCTK-Corpus/wav48")).glob("**/*.wav")]

    class_labels_path = audioset_root / Path("class_labels_indices.csv")
    label_map = get_read_class_labels(class_labels_path)

    segments = read_segments_file(audioset_root / Path("eval_segments.csv"))

    with ThreadPoolExecutor() as pool:
        info("Beginning processing")
        for vctk_fname in vctk_files:
            for audioset_fname in audioset_files:
                labels = get_labels(audioset_fname, segments, label_map)
                fname = get_filename(labels, vctk_fname, audioset_fname)
                pool.submit(combine_vctk_with_audioset,
                            vctk_fname,
                            audioset_fname,
                            output_root / fname)
        info("Processing complete")

    """
    In [25]: category_files = []
    ...: for idx, row in class_labels.iterrows():
    ...:     ytids = []
    ...:     for idx2, segment in segments.iterrows():
    ...:         if row["mid"] in segment["labels"]:
    ...:             ytids.append(segment["ytid"])
    ...:         if len(ytids) == 10:
    ...:             break
    ...:     category_files.append(ytids)
    ...:
    """
