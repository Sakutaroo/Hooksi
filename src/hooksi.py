from __future__ import annotations

from typing import Sequence
from argparse import ArgumentParser
from sys import stdout
from subprocess import run as subprocess_run, PIPE, CalledProcessError
from hashlib import sha1


def check_clang_format() -> bool:
    """Check if user has clang-format installed."""
    result = subprocess_run(['clang-format', '--version'], stdout=PIPE)
    if result.returncode != 0:
        return False
    return True


def check_file_hash(filename: str, initial_hash):
    """Check if file has changed."""
    initial_hash = initial_hash

    updated_hash = sha1()
    with open(filename, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            updated_hash.update(chunk)

    return initial_hash.hexdigest() == updated_hash.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    """Check if files are formatted according to clang-format."""
    if check_clang_format() is False:
        stdout.write("clang-format not found. Please install clang-format.")
        return 1
    parser = ArgumentParser()
    parser.add_argument(
        'filenames', nargs='*',
        help='Filenames pre-commit believes are changed.',
    )
    args = parser.parse_args(argv)
    for filename in args.filenames:
        initial_hash = sha1()
        with open(filename, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                initial_hash.update(chunk)
        try:
            subprocess_run(['clang-format', '-style=file', '-i', filename], stdout=PIPE, stderr=PIPE, check=True)
        except CalledProcessError as e:
            stdout.write(f"Error with {filename} during clang-format.\n")
            continue
        updated_hash = check_file_hash(filename, initial_hash)
        if updated_hash is False:
            stdout.write(f"File {filename} was modified during the clang-format hook.\n")
            subprocess_run(['git', 'add', filename], stdout=PIPE, stderr=PIPE)
            continue
    stdout.write(f"Clang format end\n")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
