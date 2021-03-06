from pathlib import Path
import logging
from data_collection_utils import download, extract_tarball
import argparse
# import sox

parser = argparse.ArgumentParser(description="Downloads the VCTK corpus if it does not exist. Assumes it is" +
        "being run from the parent directory to `preprocessing` where it will create a data directory and do" +
        "all of the download and extracting work")

parser.add_argument("--url",
                    help="url to tar gzip'd data path, ex: " +
                    "http://homepages.inf.ed.ac.uk/jyamagis/release/VCTK-Corpus.tar.gz",
                    default="http://homepages.inf.ed.ac.uk/jyamagis/release/VCTK-Corpus.tar.gz")
parser.add_argument("--download_dir_path",
                    help="path to data directory, will be created if non-existent, ex: data",
                    default="data")
parser.add_argument("--log_level",
                    help="logging level",
                    default="INFO")


def download_and_extract(data_dir_path, url):
    data_dir = Path(data_dir_path)

    if_nonexistent_create_directory(data_dir)

    filepath = data_dir / Path("VCTK-Corpus.tar.gz")

    download(url, filepath)

    extract_tarball(filepath, data_dir)


def if_nonexistent_create_directory(path):
    if not path.is_dir():
        logging.info("creating directory {}".format(path))
        path.mkdir()


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(format=logging.BASIC_FORMAT, level=args.log_level)
    download_and_extract(args.download_dir_path, args.url)
