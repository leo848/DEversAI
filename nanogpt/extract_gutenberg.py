from bs4 import BeautifulSoup
import os
import pathlib
from tqdm import tqdm


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
            if child.is_dir():
                directory_stack.append(child)
            elif child.is_file():
                if is_relevant_file(child):
                    yield child
    return files


def main():
    files = all_files()
    counter = 0
    for file in tqdm(files):
        counter += 1
        with open(file) as f:
            soup = BeautifulSoup(f.read())
        print(soup.prettify()[:10000])
        if counter > 10:
            break

if __name__ == "__main__":
    main()
