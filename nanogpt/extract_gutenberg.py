import beautifulsoup4 as bs4
import os
import pathlib

def is_relevant_file(path) -> bool:
    if path.suffix != ".html":
        return False
    if path.stem == "index":
        return False
    return True

def all_files(root_folder="/home/shared/datasets/GUTENBERG"):
    directory_stack = [pathlib.Path(root_folder)]
    files = []

    while directory_stack:
        current = directory_stack.pop()
        children = current.iterdir()
        for child in children:
            if child.is_dir:
                directory_stack.append(child)
            elif child.is_file:
                if is_relevant_file(child):
                    files.append(child)
    return files


def main():
    files = all_files()
    print(len(files), "files")

if __name__ == "__main__":
    main()
