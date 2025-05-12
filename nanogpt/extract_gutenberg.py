from bs4 import BeautifulSoup
import re
import pathlib
from tqdm import tqdm

EXPR = re.compile(r"\s+")
def strip(text: str):
    return re.sub(EXPR, " ", text).strip()

def is_relevant_file(path) -> bool:
    if path.suffix != ".html":
        return False
    if path.stem in {"index", "titlepage"}:
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
    SKIP_FIRST = None
    STOP_AFTER = None

    for file in tqdm(files, total=253773):
        counter += 1
        if SKIP_FIRST is not None and counter < SKIP_FIRST:
            continue
        if STOP_AFTER is not None and counter > STOP_AFTER:
            break

        with open(file) as f:
            try:
                soup = BeautifulSoup(f.read(), "html.parser")
            except UnicodeDecodeError:
                continue
        body = soup.body
        for nav in body.select(".navi-gb, .center, .footnote"):
            nav.decompose()

        found_heading = False
        body_paragraphs = []


        for tag in body.descendants:
            if not hasattr(tag, "name"):
                continue
            try:
                classes = tag.get("class", set())
            except (IndexError, AttributeError):
                classes = set()
            tag_name = str(tag.name)
            if len(tag_name) == 2 and tag_name[0] == "h" and tag_name[1].isdigit():
                heading_level = int(tag_name[1])
                found_heading = True
                heading_text = strip(tag.get_text())

                is_author = "author" in classes
                is_title = "title" in classes

                if is_title:
                    heading_level = 1
                    body_paragraphs = []

                if heading_text and not is_author:
                    body_paragraphs.append(
                "#" * heading_level + " " + heading_text + "\n"
                    )
            if not found_heading:
                continue

            if tag_name == "p":
                if "vers" in tag.get("class", set()):
                    BR_KEY = "␤nl␤"
                    for br in tag.find_all("br"):
                        br.replace_with(BR_KEY)
                    text = strip(tag.get_text()).replace(BR_KEY, "\n") + "\n"
                else:
                    text = strip(tag.get_text())
                if text:
                    body_paragraphs.append(text)

        content = "\n".join(body_paragraphs)

        if len(content) < 100:
            continue

        parts = list(file.parts[-3:])
        if file.suffix:
            parts[-1] = file.stem
        if parts[-1] == parts[-2]:
            continue
        filename = "--".join(parts) + ".txt"
        new_path = pathlib.Path("/data/gutenberg-extracted") / filename
        with open(new_path, "w") as f:
            f.write(content)

if __name__ == "__main__":
    main()
