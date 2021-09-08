import os


def path(path: str) -> str:
    return os.path.join(os.path.dirname(os.path.realpath(__file__)),
                        'testdata', path)
