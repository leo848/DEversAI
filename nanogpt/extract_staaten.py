
import json
from math import inf
import re
from gpt import GPT
import torch
from torch.nn import functional as F
from vocabulary import Vocabulary

EXCLUDE_EXPR = re.compile(r"^und |, |\(|\)|^Das ")



STAATEN_RAW = [
    "von/Albanien/Albania/Tirana",
    "von/Andorra/Andorra/Andorra la Vella",
    "von/Belarus/Belarus/Minsk",
    "von/Belgien/Belgium/Brüssel",
    "von/Bosnien und Herzegowina/Bosnia_and_Herzegovina/Sarajevo",
    "von/Bulgarien/Bulgaria/Sofia",
    "von/Dänemark/Denmark/Kopenhagen",
    "von/Deutschland/Germany/Berlin",
    "von/Estland/Estonia/Tallinn",
    "von/Finnland/Finland/Helsinki",
    "von/Frankreich/France/Paris",
    "von/Griechenland/Greece/Athen",
    "von/Irland/Ireland/Dublin",
    "von/Island/Iceland/Reykjavík",
    "von/Italien/Italy/Rom",
    "von/Kasachstan/Kazakhstan/Astana",
    "von/Kroatien/Croatia/Zagreb",
    "von/Kosovo/Kosovo/Pristina",
    "von/Lettland/Latvia/Riga",
    "von/Liechtenstein/Liechtenstein/Vaduz",
    "von/Litauen/Lithuania/Vilnius",
    "von/Malta/Malta/Valletta",
    "von/Moldau/Moldova/Chișinău",
    "von/Montenegro/Montenegro/Podgorica",
    "von/Niederlande/Netherlands/Amsterdam",
    "von/Nordmazedonien/North_Macedonia/Skopje",
    "von/Norwegen/Norway/Oslo",
    "von/Österreich/Austria/Wien",
    "von/Polen/Poland/Warschau",
    "von/Portugal/Portugal/Lissabon",
    "von/Rumänien/Romania/Bukarest",
    "von/Russland/Russia/Moskau",
    "von/Schweden/Sweden/Stockholm",
    "von der/Schweiz/Switzerland/Bern",
    "von/Serbien/Serbia/Belgrad",
    "von/Slowakei/Slovakia/Bratislava",
    "von/Slowenien/Slovenia/Ljubljana",
    "von/Spanien/Spain/Madrid",
    "von/Tschechien/Czechia/Prag",
    "von/Türkei/Turkey/Ankara",
    "von der/Ukraine/Ukraine/Kiew",
    "von/Ungarn/Hungary/Budapest",
    "von dem/Vereinigten Königreich/United_Kingdom/London",
]

staaten = [
    {
        "prep": prep,
        "country": country,
        "country_en": country_en,
        "capital": capital
    }
    for (prep, country, country_en, capital)
    in (s.split("/") for s in STAATEN_RAW)
]


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

MAX_T = 0.5

def accent_gradient(t, accent_color):
    """
    General gradient from white to the given accent color.

    Parameters:
        t (float): A value in [0, 0.4].
        accent_color (str or tuple): Hex string (e.g. '#00AA00') or RGB tuple.

    Returns:
        str: Interpolated hex color string.
    """
    assert 0.0 <= t <= MAX_T, "t must be in [0, 0.4]"

    if isinstance(accent_color, str):
        end_rgb = hex_to_rgb(accent_color)
    else:
        end_rgb = accent_color

    start_rgb = (255, 255, 255)
    t_norm = t / MAX_T

    interp_rgb = tuple(
        int(start + (end - start) * t_norm)
        for start, end in zip(start_rgb, end_rgb)
    )

    return '#{:02X}{:02X}{:02X}'.format(*interp_rgb)


def green_gradient(t):
    return accent_gradient(t, '#00AA00')  # readable green

def is_correct(country, last_token, vocab):
    last_token_country = vocab.encode(country["capital"] + " ")[-1]
    return last_token == last_token_country

def main():
    vocab = Vocabulary.load("fineweb2.vocab")

    token_mask = torch.zeros(50304)
    for token in range(50256):
        string = vocab.decode([token])
        if re.match(EXCLUDE_EXPR, string):
            token_mask[token] = -inf

    print(token_mask)

    model = GPT.load("output/anticausal-fw2.pt")

    logits = torch.zeros(len(staaten), 50304)
    for country_id, country in enumerate(staaten):
        string = f"ist die Hauptstadt {country["prep"]} {country["country"]}. "
        tokens = vocab.encode(string, reverse=True)
        model_x = torch.tensor([tokens]).to("cuda")
        model_y, _ = model(model_x)
        logits[country_id] = model_y[0]

    probs = F.softmax(logits + token_mask, dim = -1)

    top_probs, top_tokens = torch.topk(probs, 3)

    token_set = set()

    groups = {}
    for country_id, country in enumerate(staaten):
        print(country["country"], end=": ")
        for i, token_id in enumerate(top_tokens[country_id].tolist()):
            token_set.add(token_id)
            print(
                vocab.decode([token_id]),
                f"{float(top_probs[country_id, i]) * 100:.2f}%",
                end=" • "
            )
        print()
        color = "#DD6666"
        if any(is_correct(country, int(top_tokens[country_id, i]), vocab) for i in {1, 2}):
            color = "#EEEE00"
        if is_correct(country, int(top_tokens[country_id, 0]), vocab):
            color = green_gradient(top_probs[country_id, 0])
        if color not in groups:
            groups[color] = { "paths": [] }
        groups[color]["paths"].append(country["country_en"])

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


    with open("output/anticausal-fw2-staaten-hauptstädte.txt", "w") as f:
        json.dump(result, f)



if __name__ == "__main__":
    main()
