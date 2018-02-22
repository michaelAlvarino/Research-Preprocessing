import logging
import argparse
import pandas as pd
import numpy as np
from logging.config import fileConfig
from pathlib import Path
from wav_utils import n_random_continous_samples
from scipy.io.wavfile import read, write
from sklearn import preprocessing


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("AUDIOSET_DIR")
    parser.add_argument("VCTK_DIR")
    parser.add_argument("OUTPUT_DIR")
    parser.add_argument("N_VIDS", type=int)
    return parser.parse_args()


def get_categories(audioset_wav_root):
    return pd.read_csv(str(audioset_wav_root / Path("class_labels_indices.csv")))


def get_segments(audioset_wav_root):
    eval_segments = pd.read_csv(
            audioset_wav_root / Path("eval_segments.csv"),
            sep=",",
            skipinitialspace=True,
            header=2)
    balanced_train_segments = pd.read_csv(
            audioset_wav_root / Path("balanced_train_segments.csv"),
            sep=",",
            skipinitialspace=True,
            header=2)
    unbalanced_train_segments = pd.read_csv(
            audioset_wav_root / Path("unbalanced_train_segments.csv"),
            sep=",",
            skipinitialspace=True,
            header=2)
    return eval_segments, balanced_train_segments, unbalanced_train_segments


def get_all_segments(audioset_wav_root):
    all_segs_file = audioset_wav_root / Path("all_segments.csv")
    if all_segs_file.exists():
        return pd.read_csv(
                str(all_segs_file),
                header=0
                )
    else:
        segs = get_segments(audioset_wav_root)
        all_segs = pd.concat(segs)
        all_segs.to_csv(str(all_segs_file))
        return all_segs


def get_ytid_path_map(audioset_wav_root):
    paths = list(audioset_wav_root.glob("**/*.wav"))
    ytids = map(lambda x: x.stem.split("_")[0], paths)
    return {ytid: path for ytid, path in zip(ytids, paths)}


def combine_google_vctk(google_data, vctk_data, rate, fname):
    mms = preprocessing.MinMaxScaler()
    multi_channel = np.hstack([google_data, vctk_data.reshape(vctk_data.shape[0], 1)]).T
    stereo = multi_channel.mean(axis=0)
    scaled_stereo = mms.fit_transform(stereo.reshape(-1, 1))
    write(fname, rate, scaled_stereo)


def mix_for_each_vctk_entry(vctk_clips, audioset, noise_category, output_root):
    audioset_rate, audioset_data = read(audioset)
    for vctk in vctk_clips:
        vctk_rate, vctk_data = read(vctk)
        sample, start, end = n_random_continous_samples(vctk_data.shape[0], audioset_data)
        fname = output_root / Path(f"{vctk.stem}_{noise_category}_{audioset.stem}.wav")
        combine_google_vctk(sample, vctk_data, vctk_rate, fname)
        break


def ytid_to_exact_filepath(ytid, audioset_wav_root):
    return Path(list(audioset_wav_root.glob(f"**/*{ytid}*.wav"))[0])


if __name__ == "__main__":
    args = parse_args()

    try:
        fileConfig("logging.conf")
    except Exception:
        logging.basicConfig(
                format=logging.BASIC_FORMAT,
                level="INFO"
                )

    logging.info("starting...")

    audioset_wav_root = Path(args.AUDIOSET_DIR)
    output_root = Path(args.OUTPUT_DIR)
    vctk_root = Path(args.VCTK_DIR)
    n_vids = args.N_VIDS

    vctk_wavs = list(map(Path, vctk_root.glob("**/*.wav")))

    file_category_mapping = get_all_segments(audioset_wav_root)

    categories = get_categories(audioset_wav_root)

    ytid_path_map = get_ytid_path_map(audioset_wav_root)

    # go through each audio category
    for _, category in categories.iterrows():
        logging.info(f"matching category {category['display_name']}")
        cat_code = category["mid"]
        # until we find n_vids videos that were successfully downloaded, or have gone through all the videos
        n = 0
        for _, file_cat in file_category_mapping.iterrows():
            ytid = file_cat["# YTID"]
            labels = file_cat["positive_labels"]
            if cat_code in labels:
                try:
                    audioset_entry_path = ytid_to_exact_filepath(ytid, audioset_wav_root)
                except IndexError:
                    # ytid would have qualified but we failed to download or convert it to wav
                    logging.info(f"youtube audio clip for {ytid} is a match, but file is missing")
                    continue
                mix_for_each_vctk_entry(vctk_wavs, audioset_entry_path, category["display_name"], output_root)
                file_category_mapping.drop(_, inplace=True)
                n += 1
                if n == n_vids:
                    break
