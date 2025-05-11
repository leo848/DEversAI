from bs4 import BeautifulSoup
import os
import pathlib
from tqdm import tqdm

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
            tag_name = str(tag.name)
            if not found_heading:
                if len(tag_name) == 2 and tag_name[0] == "h":
                    heading_level = int(tag_name[1])
                    found_heading = True
                    heading_text = tag.get_text(strip=True).strip()
                    if heading_text:
                        body_paragraphs.append(
                    "#" * heading_level + " " + heading_text + "\n"
                        )
                continue

            if tag_name == "p":
                if "vers" in tag.get("class", set()):
                    BR_KEY = "␤nl␤"
                    for br in tag.find_all("br"):
                        br.replace_with(BR_KEY)
                    text = tag.get_text(strip=True).strip().replace(BR_KEY, "\n") + "\n"
                else:
                    text = tag.get_text(strip=True).strip()
                if text:
                    body_paragraphs.append(text)

        content = "\n".join(body_paragraphs)

        if len(content) < 100:
            continue

        parts = list(file.parts[-3:])
        if file.suffix:
            parts[-1] = file.stem
        filename = "--".join(parts) + ".txt"
        new_path = pathlib.Path("/data/gutenberg-extracted") / filename
        with open(new_path, "w") as f:
            f.write(content)
        tqdm.write(" ".join(map(str, (file, ":", len(content), repr(content[:100])))))

if __name__ == "__main__":
    main()
