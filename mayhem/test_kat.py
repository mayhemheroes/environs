#!/usr/bin/env python3
"""
Known-answer behavioral oracle for environs.

Loads a fixed .env via `Env.read_env` (the same code path the fuzz harness drives) and asserts
the parsed values byte-for-byte, plus the error semantics (missing-required and invalid-cast both
raise EnvError). These are real output assertions — a no-op / exit(0) / value-altering patch CANNOT
pass — so the suite is not reward-hackable.

Emits one `PASS <name>` / `FAIL <name>` line per check; exits 0 iff every check passed.
mayhem/test.sh tallies the lines into a CTRF summary.
"""
import os
import sys
import tempfile

import environs

ENV_CONTENT = (
    "STR_VAL=hello world\n"
    "INT_VAL=42\n"
    "BOOL_VAL=true\n"
    "FLOAT_VAL=3.5\n"
    "LIST_VAL=a,b,c\n"
    "BAD_INT=notanumber\n"
)

results = []


def check(name, cond):
    results.append((name, bool(cond)))


def raises_env_error(fn):
    try:
        fn()
    except environs.EnvError:
        return True
    except Exception:
        return False
    return False


def main():
    fd, path = tempfile.mkstemp(suffix=".env")
    with os.fdopen(fd, "w") as f:
        f.write(ENV_CONTENT)
    try:
        env = environs.Env()
        env.read_env(path, recurse=False)

        check("str parses verbatim", env.str("STR_VAL") == "hello world")
        check("int parses to int", env.int("INT_VAL") == 42)
        check("bool parses true", env.bool("BOOL_VAL") is True)
        check("float parses", env.float("FLOAT_VAL") == 3.5)
        check("list splits on comma", env.list("LIST_VAL") == ["a", "b", "c"])
        check("default used for missing key", env.str("ABSENT_VAL", "fallback") == "fallback")
        check("missing required raises EnvError",
              raises_env_error(lambda: env.int("DOES_NOT_EXIST")))
        check("invalid int cast raises EnvError",
              raises_env_error(lambda: env.int("BAD_INT")))
    finally:
        os.unlink(path)

    ok = True
    for name, passed in results:
        sys.stdout.write(("PASS " if passed else "FAIL ") + name + "\n")
        ok = ok and passed
    sys.stdout.flush()
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
