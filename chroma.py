#!/usr/bin/env python
import math
import random
import shutil
import subprocess
import tempfile
import time
from os import getcwd
from pathlib import Path
from sys import exit

from pydub import AudioSegment

MUSIC_DIR = Path("/home/kajm/media/music")    # change to directory with mp3 files
MP3_FILES = list(MUSIC_DIR.glob("**/*.mp3"))  # glob for finding mp3files
TEST_DATA = random.sample(MP3_FILES, 10)      # 10 is the number of songs to test out


def calculate_fingerprint(path):
    try:
        prog = ["fpcalc", "-raw", "-plain", path]
        fp = None
        with subprocess.Popen(prog, stdout=subprocess.PIPE, text=True) as proc:
            fp_raw = proc.stdout.read()
            fp = list(map(int, fp_raw.split(",")))
        return fp
    except ValueError:
        shutil.copy(path, getcwd())
        return None


def create_duration_samples(path, dest_dir):
    """
    Create 5 random samples from a given song. Both the
    position they starts in the song and how long the
    samples are is randomized. Occasionally creates.
    """
    song = AudioSegment.from_mp3(path)
    samples = [random.randint(5, 20) for _ in range(5)]
    song_name = path.stem
    snippets = []
    for i in samples:
        start = random.randint(0, 60)
        snippet = song[start * 1000: (i + start) * 1000]
        snippet_path = dest_dir / (song_name + f"_{i}_{start}s" + path.suffix)
        snippet.export(snippet_path)
        snippets.append(((i, start), snippet_path))
    return snippets


def make_slices(same_positions, limit):
    """
    Create collection of slices by merging consecutive
    positions and beginning/ending slices at the transitions
    between positions e.e [1, 2, 3, 5, 6, 8] becomes
    [(1, 3), (5, 6), (8, 8)]. Slices are inclusive of
    the end
    """
    sp = same_positions[:]
    slices = []
    while len(sp) > 1:
        try:
            start = sp[0]
            while sp[0] + 1 == sp[1]:
                sp.pop(0)
            slices.append((start, sp[0]))
            sp.pop(0)
        except IndexError:
            continue
    for s in sp:
        slices.append((s, s))
    return slices


def find_matching_positions(l1, l2):
    """
    l2 assumed to be longer than l1. Always use
    the index of first value in l1 present in l2
    """
    r1 = []
    r2 = []
    for (j, v) in enumerate(l2):
        try:
            i = l1.index(v)
            r1.append(i)
            r2.append(j)
        except ValueError:
            continue
    return (r1, r2)


def avg_distance(sample, candidate):
    """
    A value of 0 is ideal and means that the sample fingerprint
    is a proper subset of candidate fingerprint. math.inf in our
    case means that there's no way the fingerprints come from the
    same song
    """
    # find positions where the two fingerprints are equal
    sample_positions, candidate_positions = find_matching_positions(
        sample, candidate
    )
    if len(sample_positions) == 0:  # return early since no similar positions
        return math.inf
    all_diffs = []
    sample_slices = make_slices(sample_positions, len(sample_positions))
    candidate_slices = make_slices(
        candidate_positions, len(candidate_positions)
    )
    # find slices and compute their differences
    for ((ss, se), (cs, ce)) in zip(sample_slices, candidate_slices):
        if ss == se and cs == ce:
            all_diffs.append(abs(sample[ss] - candidate[cs]))
        else:
            sample_slice = sample[ss : se + 1]
            candidate_slice = candidate[cs : ce + 1]
            diffs = [
                abs(x - y) for (x, y) in zip(sample_slice, candidate_slice)
            ]
            all_diffs.append(
                sum(diffs) / len(diffs)
            )  # average distance between fingerprints in slices
    return sum(all_diffs) / len(all_diffs) # average of all differences


def compare_single_track(song, tdir, reference, reffp):
    title = song.stem
    print("-" * 70)
    print(f"Current:          {title:<50s}")
    print("*" * 70)
    print(f"Random Reference: {reference.stem:<50}")
    print("-" * 70)
    orig_fingerprint = calculate_fingerprint(song)
    samples = create_duration_samples(song, Path(tdir))
    if orig_fingerprint is None:
        print(f"Could not calculate fingerprint for track")
        return
    for ((duration, start), sample) in samples:
        s = calculate_fingerprint(sample)
        if s is None:
            print(f"Could not calculate fingerprint for {samples[0][1]}")
            continue
        start_time = time.process_time()
        dist = avg_distance(s, orig_fingerprint)
        dur = time.process_time() - start_time
        print(f"Fingerprint comparison completed in {dur:.8f}s")
        ref_dist = avg_distance(s, reffp)
        print(
            f"Sample starting {start}s to {start + duration}s\n"
            f"Distance to candidate {dist:.2f}\n"
            f"Distance to reference {ref_dist:.2f}\n"
        )


def main():
    track = random.choice(TEST_DATA)
    random_reference = random.choice(TEST_DATA)
    ref = calculate_fingerprint(random_reference)
    if not ref:
        print(f"Could not calculate fingerprint for reference")
        exit(1)
    with tempfile.TemporaryDirectory() as tdir:
        for track in TEST_DATA:
            compare_single_track(track, tdir, random_reference, ref)


if __name__ == "__main__":
    main()
