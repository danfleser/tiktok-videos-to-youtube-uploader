import os


def is_file_broken_size(path):
    is_file_broken = False

    generated_file_size = os.path.getsize(path)
    if generated_file_size < 100:
        is_file_broken = True

    return is_file_broken
