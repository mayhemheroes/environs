#!/usr/bin/env python3

import atheris
import sys
import io
from contextlib import contextmanager
import fuzz_helpers

with atheris.instrument_imports(include=['environs', 'json', ]):
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
    try:
        with fdp.ConsumeTemporaryFile('.env', all_data=False, as_bytes=False) as fname, nostdout():
            env = environs.Env()
            env.read_env(fname)
            test = fdp.ConsumeIntInRange(0, 6)
            if test == 0:
                env.dump()
            elif test == 1:
                env.seal()
            elif test == 2:
                env.int(fdp.ConsumeRandomString())
            elif test == 3:
                env.date(fdp.ConsumeRandomString())
            elif test == 4:
                env.timedelta(fdp.ConsumeRandomString())
            elif test == 5:
                env.log_level(fdp.ConsumeRandomString())
            else:
                env.list(fdp.ConsumeRandomString())
    except environs.EnvError:
        return -1
    except ValueError as e:
        if 'null' in str(e):
            return -1
        raise


def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
