from bs4 import BeautifulSoup
import os
import pathlib


def is_relevant_file(path) -> bool:
    if path.suffix != ".html":
        return False
    if path.stem == "index":
        return False
    return True

def all_files(root_folder="/data/gutenberg-raw"):
    directory_stack = [pathlib.Path(root_folder)]
    files = []

    while directory_stack:
        current = directory_stack.pop()
        children = current.iterdir()
        for child in children:
            if child.is_dir(follow_symlinks=False):
                directory_stack.append(child)
            elif child.is_file():
                if is_relevant_file(child):
                    files.append(child)
    return files


def main():
    files = all_files()
    print(len(files), "files")

if __name__ == "__main__":
    main()
