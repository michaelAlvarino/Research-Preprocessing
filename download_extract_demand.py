from data_collection_utils import download, extract_zip
from pathlib import Path
import argparse
import logging


parser = argparse.ArgumentParser(description="Downloads the VCTK corpus if it does not exist. Assumes it is" +
        "being run from the parent directory to `preprocessing` where it will create a data directory and do" +
        "all of the download and extracting work")

parser.add_argument("--demand_dir",
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
    for url, fname in zip(urls, destinations):
        download(url, demand_dir / Path(fname))


def extract_demand_zips(subjects, demand_dir):
    zips = list(map(lambda fname: demand_dir / Path("{}_48k.zip".format(fname)), subjects))
    for zipf in zips:
        extract_zip(zipf, demand_dir)


if __name__ == "__main__":
    args = parser.parse_args()
    logging.basicConfig(format=logging.BASIC_FORMAT, level=args.log_level)
    demand_dir = Path(args.demand_dir)
    if not demand_dir.exists():
        demand_dir.mkdir()
    subjects = ["DWASHING", "DKITCHEN", "DLIVING", "NFIELD",
                "NPARK", "NRIVER", "OOFFICE", "OHALLWAY",
                "OMEETING", "PSTATION", "PCAFETER", "PRESTO",
                "SCAFE", "STRAFFIC", "SPSQUARE", "TMETRO",
                "TBUS", "TCAR"]
    download_demand_zips(subjects, demand_dir)
    extract_demand_zips(subjects, demand_dir)
