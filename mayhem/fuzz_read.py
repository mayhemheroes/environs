#!/usr/bin/env python3

import atheris
import sys
import io
from contextlib import contextmanager
import fuzz_helpers

with atheris.instrument_imports():
    import environs

@contextmanager
def nostdout():
    save_stdout = sys.stdout
    save_stderr = sys.stderr
    sys.stdout = io.StringIO()
    sys.stderr = io.StringIO()
    yield
    sys.stdout = save_stdout
    sys.stderr = save_stderr

def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    with fdp.ConsumeTemporaryFile('.env', all_data=True, as_bytes=False) as fname, nostdout():
        env = environs.Env()
        env.read_env(fname)
        env.dump()
        env.seal()


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
