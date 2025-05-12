from bs4 import BeautifulSoup
import re
import pathlib
from tqdm import tqdm

BR_KEY = "␤nl␤"
EXPR = re.compile(r"\s+")
EXPR_NL = re.compile("""
{2,}""")
def strip(text: str):
    return re.sub(EXPR, " ", text).replace(BR_KEY, "\n").strip()

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
        for nav in body.select(".navi-gb, .center, .centerbig, .footnote"):
            nav.decompose()

        found_heading = False
        body_paragraphs = []


        for tag in body.descendants:
            if not hasattr(tag, "name"):
                continue
            try:
                classes = tag.get("class", set())
                for br in tag.find_all("br"):
                    br.replace_with(BR_KEY)
            except (IndexError, AttributeError):
                classes = set()
            tag_name = str(tag.name)
            if len(tag_name) == 2 and tag_name[0] == "h" and tag_name[1].isdigit():
                heading_level = int(tag_name[1])
                found_heading = True
                heading_text = strip(tag.get_text())

                is_title = "title" in classes

                if is_title:
                    heading_level = 1
                    body_paragraphs = []

                if heading_text and heading_text != "Inhalt":
                    if body_paragraphs:
                        body_paragraphs.append("")
                    for line in heading_text.split("\n"):
                        body_paragraphs.append(
                    "#" * heading_level + " " + line
                        )
                    body_paragraphs.append("")
            if not found_heading:
                continue

            if tag_name == "p":
                text = strip(tag.get_text())
                if text:
                    for line in text.split("\n"):
                        body_paragraphs.append(line.strip())
                    if "vers" in tag.get("class", set()):
                        body_paragraphs.append("")

        content = "\n".join(body_paragraphs)
        content = EXPR_NL.sub(content, "\n\n")

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
