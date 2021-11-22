import sys


class vNError(Exception):
    pass


def run_safe(fn):
    def wrapped(*args, **kwargs):
        try:
            fn(*args, **kwargs)
        except vNError as err:
            sys.stderr.write(str(err) + '\n')
            sys.exit(1)

    return wrapped
