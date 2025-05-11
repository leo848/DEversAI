from typing import cast
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

    contents = []

    for file in tqdm(files):
        counter += 1
        with open(file) as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        body = soup.body
        for nav in body.select(".navi-gb"):
            nav.decompose()

        found_heading = False
        body_paragraphs = []


        for tag in body.descendants:
            if not hasattr(tag, "name"):
                continue
            if not found_heading:
                tag_name = cast(str, tag.name)
                if len(tag_name) == 2 and tag_name[0] == "h":
                    heading_level = int(tag_name[1])
                    found_heading = True
                    body_paragraphs.append(
                        "#" * heading_level +
                        tag.get_text(strip=True)
                    )
                continue

            if found_heading and tag.name == "p":
                body_paragraphs.append(tag.get_text(strip=True))

        if counter > 1000:
            break

        content = "\n".join(body_paragraphs)
        contents.append((file, content))

    for file, content in contents:
        print(file, ":", len(content), repr(content[:100]))

if __name__ == "__main__":
    main()
