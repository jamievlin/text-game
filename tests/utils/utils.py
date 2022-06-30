import os

TEST_RESOURCES_DIR = 'test_resources'


def from_test_resources(filename: str) -> os.PathLike:
    # noinspection PyTypeChecker
    return os.path.join(TEST_RESOURCES_DIR, filename)
