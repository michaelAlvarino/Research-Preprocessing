from pathlib import Path
from data_collection_utils import download, extract_tarball
import argparse
import logging
import pandas as pd


parser = argparse.ArgumentParser(description="Downloads the VCTK corpus if it does not exist. Assumes it is" +
        "being run from the parent directory to `preprocessing` where it will create a data directory and do" +
        "all of the download and extracting work")

parser.add_argument("--data_dir_path",
                    help="path to data directory, will be created if non-existent, ex: data",
                    default="data")
parser.add_argument("--log_level",
                    help="logging level",
                    default="DEBUG")


def download_labels_indices(data_dir):
    labels_url = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/csv/class_labels_indices.csv"
    class_labels_indices_fname = Path("class_labels_indices.csv")
    download(labels_url, data_dir / class_labels_indices_fname)


def download_features(to):
    features_url = "http://storage.googleapis.com/us_audioset/youtube_corpus/v1/features/features.tar.gz"
    download(features_url, to)


def download_and_extract_features(data_dir):
    features_fname = Path("features.tar.gz")
    features_dirname = Path("features")
    tar_loc = data_dir / features_fname
    features_dir = data_dir / features_dirname
    download_features(tar_loc)
    extract_tarball(tar_loc, features_dir)


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(format=logging.BASIC_FORMAT, level=args.log_level)
    data_dir = Path(args.data_dir_path)
    download_labels_indices(data_dir)
    download_and_extract_features(data_dir)
