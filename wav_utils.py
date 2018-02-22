import logging
import numpy as np
from pathlib import Path
from scipy.io.wavfile import read


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
