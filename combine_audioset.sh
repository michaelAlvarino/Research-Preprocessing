#!/bin/bash

source venv/bin/activate

python combine_vctk_google_superaudio.py \
    data/AUDIOSET \
    data/VCTK-Corpus/wav48 \
    data/output \
    10
