import json
from gpt import GPT
import torch
from torch.nn import functional as F
from vocabulary import Vocabulary

LÄNDER = [
    "Bayern",
    "Niedersachsen",
    "Baden-Württemberg",
    "Nordrhein-Westfalen",
    "Brandenburg",
    "Mecklenburg-Vorpommern",
    "Hessen",
    "Sachsen-Anhalt",
    "Rheinland-Pfalz",
    "Sachsen",
    "Thüringen",
    "Schleswig-Holstein",
    "Saarland"
]

def correct(token, vocab):
    land_capitals = {
        "München ",
        "Hannover ",
        "Stuttgart ",
        "Düsseldorf ",
        "Potsdam ",
        "Wiesbaden ",
        "Magdeburg ",
        "Dresden ",
        "Erfurt ",
        "Kiel ",
        "Mainz ",
        "Saarbrücken ",
    }
    land_capital_tokens = { vocab.encode(capital)[0] for capital in land_capitals }
    return token in land_capital_tokens

WITH_ARTICLE = { "Saarland" }

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def accent_gradient(t, accent_color):
    """
    General gradient from white to the given accent color.

    Parameters:
        t (float): A value in [0, 0.4].
        accent_color (str or tuple): Hex string (e.g. '#00AA00') or RGB tuple.

    Returns:
        str: Interpolated hex color string.
    """
    assert 0.0 <= t <= 0.4, "t must be in [0, 0.4]"

    if isinstance(accent_color, str):
        end_rgb = hex_to_rgb(accent_color)
    else:
        end_rgb = accent_color

    start_rgb = (255, 255, 255)
    t_norm = t / 0.4

    interp_rgb = tuple(
        int(start + (end - start) * t_norm)
        for start, end in zip(start_rgb, end_rgb)
    )

    return '#{:02X}{:02X}{:02X}'.format(*interp_rgb)


def green_gradient(t):
    return accent_gradient(t, '#00AA00')  # readable green


def yellow_gradient(t):
    return accent_gradient(t, '#CCCC00')  # readable yellow (adjustable)

def main():
    model = GPT.load("output/anticausal-fw2.pt")
    vocab = Vocabulary.load("fineweb2.vocab")

    logits = torch.zeros(len(LÄNDER), 50304)
    for land_id, land in enumerate(LÄNDER):
        letter = "m" if land in WITH_ARTICLE else "n"
        string = f"ist die Hauptstadt vo{letter} {land}. "
        tokens = vocab.encode(string, reverse=True)
        model_x = torch.tensor([tokens]).to("cuda")
        model_y, _ = model(model_x)
        logits[land_id] = model_y[0]

    probs = F.softmax(logits, dim = -1)

    top_probs, top_tokens = torch.topk(probs, 3)

    token_set = set()

    groups = {}
    for land_id, land in enumerate(LÄNDER):
        print(land, end=": ")
        for i, token_id in enumerate(top_tokens[land_id].tolist()):
            token_set.add(token_id)
            print(
                vocab.decode([token_id]),
                f"{float(top_probs[land_id, i]) * 100:.2f}%",
                end=" • "
            )
        color = "#DD6666"
        if any(correct(int(top_tokens[land_id, i]), vocab) for i in {1, 2}):
            color = "#EEEE00"
        if correct(int(top_tokens[land_id, 0]), vocab):
            color = green_gradient(top_probs[land_id, 0])
        if color not in groups:
            groups[color] = { "paths": [] }
        groups[color]["paths"].append(land)

    result = {
        "groups": groups,
          "title": "",
          "hidden": [],
          "background": "#ffffff",
          "borders": "#000",
          "legendFont": "Century Gothic",
          "legendFontColor": "#000",
          "legendBorderColor": "#00000000",
          "legendBgColor": "#00000000",
          "legendWidth": 150,
          "legendBoxShape": "square",
          "areBordersShown": True,
          "defaultColor": "#d1dbdd",
          "labelsColor": "#6a0707",
          "labelsFont": "Arial",
          "strokeWidth": "medium",
          "areLabelsShown": False,
          "uncoloredScriptColor": "#ffff33",
          "zoomLevel": "1.00",
          "zoomX": "0.00",
          "zoomY": "0.00",
          "v6": True,
          "page": "germany",
          "levelsVisibility": ["show", "show", "transparent"],
          "legendPosition": "bottom_right",
          "legendSize": "medium",
          "legendTranslateX": "0.00",
          "legendStatus": "show",
          "scalingPatterns": True,
          "legendRowsSameColor": True,
          "legendColumnCount": 1
    }


    with open("output/anticausal-fw2-bundesländer-hauptstädte.txt", "w") as f:
        json.dump(result, f)



if __name__ == "__main__":
    main()
