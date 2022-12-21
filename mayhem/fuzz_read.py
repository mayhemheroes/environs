#!/usr/bin/env python3

import atheris
import sys
import fuzz_helpers

with atheris.instrument_imports(include=['environs']):
    import environs


def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    with fdp.ConsumeTemporaryFile('.env', all_data=True, as_bytes=False) as fname:
        env = environs.Env()
        env.read_env(fname)
        env.dump()


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
