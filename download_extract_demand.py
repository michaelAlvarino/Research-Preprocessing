from data_collection_utils import download, extract_zip
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, Future
import argparse
import logging


parser = argparse.ArgumentParser(description="Downloads the VCTK corpus if it does not exist. Assumes it is" +
        "being run from the parent directory to `preprocessing` where it will create a data directory and do" +
        "all of the download and extracting work")

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


def download_demand_zips(subjects, demand_dir):
    if not demand_dir.is_dir():
        demand_dir.mkdir()
    urls = map("http://parole.loria.fr/DEMAND/{}_48k.zip".format, subjects)
    destinations = map("{}_48k.zip".format, subjects)
    with ThreadPoolExecutor(max_workers=len(subjects)) as executor:
        futures = []
        for url, fname in zip(urls, destinations):
            future = executor.submit(download, url, demand_dir / Path(fname))
            futures.append(future)
        results = list(map(lambda fut: fut.exception(), futures))
        for result in results:
            if result is not None:
                logging.error(f"exception {result}")


def extract_demand_zips(subjects, demand_dir):
    zips = list(map(lambda fname: demand_dir / Path(f"{fname}_48k.zip"), subjects))
    with ThreadPoolExecutor(max_workers=len(zips)) as executor:
        futures = [executor.submit(extract_zip, zipf, demand_dir) for zipf in zips]
    results = list(map(lambda fut: fut.exception(), futures))
    for result in results:
        if result is not None:
            logging.error(f"exception {result}")


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(format=logging.BASIC_FORMAT, level=args.log_level)
    data_dir = Path(args.data_dir_path)
    demand_dir = data_dir / Path("DEMAND")
    subjects = ["DWASHING", "DKITCHEN", "DLIVING", "NFIELD",
                "NPARK", "NRIVER", "OOFFICE", "OHALLWAY",
                "OMEETING", "PSTATION", "PCAFETER", "PRESTO",
                "SCAFE", "STRAFFIC", "SPSQUARE", "TMETRO",
                "TBUS", "TCAR"]
    download_demand_zips(subjects, demand_dir)
    extract_demand_zips(subjects, demand_dir)
