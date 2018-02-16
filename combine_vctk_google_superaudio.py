from data_collection_utils import download
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging
from logging.config import fileConfig
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


def read_segments_file(fname):
    dat = pd.read_csv(fname,
                      engine="python",
                      header=2,
                      skipinitialspace=True,
                      names=["ytid", "start", "end", "labels"])
    return dat


def get_read_class_labels(fname: Path):
    download("http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv",
             class_labels_path)
    label_map = pd.read_csv(class_labels_path)
    return label_map


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


def n_from_each_category(n, labels, segment_fnames):
    category_files = []
    for fname in segment_fnames:
        logging.info(f"using segment file {fname}")
        segs = read_segments_file(fname)
        for idx, row in labels.iterrows():
            logging.info(f"gathering ytids for category {row['display_name']}")
            ytids = []
            for idx2, aud_clip in segs.iterrows():
                if row["mid"] in aud_clip["labels"]:
                    ytids.append(aud_clip["ytid"])
                    segs.drop(idx2, inplace=True)
                if len(ytids) == n:
                    break
            if not len(ytids) == n:
                logging.info(f"could not find {n} entries for category {row['display_name']}")
            category_files.append(ytids)


if __name__ == "__main__":
    args = parser.parse_args()
    try:
        fileConfig("logging.conf")
    except:
        pass
    info = logging.info
    debug = logging.debug

    data_dir = Path(args.data_dir_path)
    audioset_root = data_dir / Path("AUDIOSET")
    vctk_root = data_dir / Path("VCTK-Corpus")
    output_root = data_dir / Path("output") / Path("audioset")

    if not output_root.exists():
        output_root.mkdir()

    audioset_files = [Path(x) for x in (audioset_root / Path("data")).glob("**/*.flac")]
    vctk_files = [Path(x) for x in (data_dir / Path("VCTK-Corpus/wav48")).glob("**/*.wav")]

    class_labels_path = audioset_root / Path("class_labels_indices.csv")
    class_labels = get_read_class_labels(class_labels_path)

    segments = read_segments_file(audioset_root / Path("eval_segments.csv"))

    eval_segments_path = audioset_root / Path("eval_segments.csv")

    cat_files = n_from_each_category(5, class_labels, [eval_segments_path])
    info(cat_files)

    """
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
