"""data.rdf から、ブラウザが読む JSON と Turtle を作る。

使い方: python3 tools/build_json.py
出力:
  assets/data/cases.json        38 事例（所属する社会実験の URI と名前を展開済み）
  assets/data/experiments.json  10 社会実験（属する事例の URI を付ける）
  assets/rdf/data.ttl           data.rdf と同じ中身の Turtle

data.rdf は書き換えない。長文の「\\ + 改行」（元の表計算の改行が崩れたもの）は
JSON では改行 1 つに直す。
"""

import json
from pathlib import Path

import rdflib

ROOT = Path(__file__).resolve().parent.parent
SE = rdflib.Namespace("http://www.teitanso.org/2012/04/se#")

# 地名の座標。2026-10-13 に Nominatim で 1 度だけ調べた値（実行時には問い合わせない）
PLACES = {
    "柏市": (35.8676218, 139.9756876),
    "柏ビレジ近隣公園": (35.9029454, 139.9664862),
}

CASE_FIELDS = [
    "title", "group", "process", "type", "problem", "problemSystem",
    "problemInterest", "problemDiffusion", "problemTech", "influence",
    "solution", "service", "improvement", "condition", "suggestion",
    "place", "keyword", "location",
]
EXP_FIELDS = ["exTitle", "purpose", "sequence", "summary", "organization", "finance"]


def text(g, s, field):
    v = g.value(s, SE[field])
    if v is None:
        return ""
    return str(v).replace("\\\n", "\n").replace("\\n", "\n")


def main():
    g = rdflib.Graph()
    g.parse(ROOT / "assets/rdf/data.rdf")

    experiments = {}
    for s in sorted(g.subjects(SE.exTitle, None)):
        e = {"uri": str(s)}
        for f in EXP_FIELDS:
            e[f] = text(g, s, f)
        e["cases"] = []
        experiments[str(s)] = e

    cases = []
    for s in sorted(g.subjects(SE.title, None)):
        c = {"uri": str(s)}
        for f in CASE_FIELDS:
            c[f] = text(g, s, f)
        c["experiments"] = []
        for ex in sorted(g.objects(s, SE.exRdfName)):
            e = experiments[str(ex)]
            c["experiments"].append({"uri": e["uri"], "title": e["exTitle"]})
            e["cases"].append(c["uri"])
        if c["location"]:
            lat, lon = PLACES[c["location"]]
            c["lat"], c["lon"] = lat, lon
        cases.append(c)

    out = ROOT / "assets/data"
    out.mkdir(exist_ok=True)
    for name, data in [("cases", cases), ("experiments", list(experiments.values()))]:
        (out / f"{name}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    g.bind("se", SE)
    g.serialize(ROOT / "assets/rdf/data.ttl", format="turtle")

    print(f"cases {len(cases)}, experiments {len(experiments)}, triples {len(g)}")


if __name__ == "__main__":
    main()
