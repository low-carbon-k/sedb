"""data.rdf から、ブラウザが読む JSON・Turtle と、サイトの HTML を作る。

使い方: python3 tools/build_json.py   （rdflib と jinja2 が要る）
出力:
  assets/data/cases.json        38 事例（所属する社会実験の URI と名前を展開済み）
  assets/data/experiments.json  10 社会実験（属する事例の URI を付ける）
  assets/rdf/data.ttl           data.rdf と同じトリプルの Turtle（文字列は下のとおり整える）
  case/<id>.html                事例ごとの静的ページ（JSON-LD を埋め込む）
  experiment/<id>.html          社会実験ごとの静的ページ（同上）
  index / search / map / analyze.html   ひな形は tools/templates/
  detail.html / group.html      旧 URL（?uri=…）を静的ページへ移すだけのページ

data.rdf は書き換えない。長文の「\\ + 改行」（元の表計算の改行が崩れたもの）は
JSON・Turtle・HTML では改行 1 つに直す。
生成物もコミットする（Pages は master の直下をそのまま配る。Actions は使わない）。
"""

import json
from pathlib import Path
from urllib.parse import quote

import jinja2
import rdflib
from markupsafe import Markup, escape

ROOT = Path(__file__).resolve().parent.parent
SE = rdflib.Namespace("http://www.teitanso.org/2012/04/se#")
BASE_URI = "http://low-carbon.k.u-tokyo.ac.jp/"
SITE_URL = "https://low-carbon-k.github.io/sedb/"

# 地名の座標。2026-10-13 に Nominatim で 1 度だけ調べた値（実行時には問い合わせない）
PLACES = {
    "柏市": (35.8676218, 139.9756876),
    "柏ビレジ近隣公園": (35.9029454, 139.9664862),
}

# トップのタイルの並びと色（2014 年版の index.html から）
GROUPS = [
    {"key": "農業・緑地計画G", "label": "農業・緑地計画", "color": "#C2CA2D", "field_color": "#AFB72B", "case_color": "#99A021"},
    {"key": "モビリティG", "label": "モビリティ", "color": "#E39E52", "field_color": "#CF904A", "case_color": "#B88043"},
    {"key": "植物医科学G", "label": "植物医科学", "color": "#E2536B", "field_color": "#CC4B61", "case_color": "#B84357"},
    {"key": "エネルギーG", "label": "エネルギー", "color": "#C04F88", "field_color": "#AD477B", "case_color": "#9C406E"},
    {"key": "都市計画G", "label": "都市計画", "color": "#1F7FB1", "field_color": "#1C75A1", "case_color": "#19668F"},
]

CASE_FIELDS = [
    "title", "group", "process", "type", "problem", "problemSystem",
    "problemInterest", "problemDiffusion", "problemTech", "influence",
    "solution", "service", "improvement", "condition", "suggestion",
    "place", "keyword", "location",
]
EXP_FIELDS = ["exTitle", "purpose", "sequence", "summary", "organization", "finance"]

# 事例の画面の表（項目、見出し、見出しの色）。見出しは 2014 年版の detail.html のまま
CASE_ROWS = [
    ("title", "タイトル", "dense"),
    ("group", "グループ名", "dense"),
    ("experiments", "関連する社会実験", "dense"),
    ("process", "フェーズ", "dense"),
    ("type", "種別", "dense"),
    ("problem", "事象", "dense2"),
    ("problemSystem", "国・自治体等の制度上の課題", "dense2"),
    ("problemInterest", "ステークホルダー間の利害調整上の課題", "dense2"),
    ("problemDiffusion", "普及等にあたっての効果/課題", "dense2"),
    ("problemTech", "社会実験の技術的な課題", "dense2"),
    ("influence", "課題の効果影響", "dense2"),
    ("solution", "課題発生時の対処状況", "dense2"),
    ("service", "その後の対応", "dense2"),
    ("improvement", "取りうる対策", "dense2"),
    ("condition", "対応の結果", "dense2"),
    ("suggestion", "社会実験成果の適用に必要な条件", "dense2"),
    ("place", "適用対象", "dense2"),
    ("keyword", "キーワード", "dense2"),
    ("location", "場所", "dense2"),
]
EXP_ROWS = [
    ("exTitle", "社会実験名"),
    ("purpose", "目的"),
    ("sequence", "経緯"),
    ("summary", "内容"),
    ("organization", "体制"),
    ("finance", "財源"),
]
FILTERS = [
    ("group", "グループ名"),
    ("exp", "社会実験名"),
    ("process", "フェーズ"),
    ("type", "課題の種別"),
    ("condition", "対応状況"),
]
ANALYZE_FIELDS = [("process", "フェーズ"), ("condition", "対応状況"), ("type", "課題の種別")]

# Bootstrap Icons 1.11.3（MIT）から、使う分だけ
ICONS = {
    "search": '<path d="M11.742 10.344a6.5 6.5 0 1 0-1.397 1.398h-.001q.044.06.098.115l3.85 3.85a1 1 0 0 0 1.415-1.414l-3.85-3.85a1 1 0 0 0-.115-.1zM12 6.5a5.5 5.5 0 1 1-11 0 5.5 5.5 0 0 1 11 0"/>',
    "bar-chart": '<path d="M1 11a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1zm5-4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1zm5-5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v12a1 1 0 0 1-1 1h-2a1 1 0 0 1-1-1z"/>',
    "geo": '<path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10m0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6"/>',
    "globe": '<path d="M0 8a8 8 0 1 1 16 0A8 8 0 0 1 0 8m7.5-6.923c-.67.204-1.335.82-1.887 1.855A8 8 0 0 0 5.145 4H7.5zM4.09 4a9.3 9.3 0 0 1 .64-1.539 7 7 0 0 1 .597-.933A7.03 7.03 0 0 0 2.255 4zm-.582 3.5c.03-.877.138-1.718.312-2.5H1.674a7 7 0 0 0-.656 2.5zM4.847 5a12.5 12.5 0 0 0-.338 2.5H7.5V5zM8.5 5v2.5h2.99a12.5 12.5 0 0 0-.337-2.5zM4.51 8.5a12.5 12.5 0 0 0 .337 2.5H7.5V8.5zm3.99 0V11h2.653c.187-.765.306-1.608.338-2.5zM5.145 12q.208.58.468 1.068c.552 1.035 1.218 1.65 1.887 1.855V12zm.182 2.472a7 7 0 0 1-.597-.933A9.3 9.3 0 0 1 4.09 12H2.255a7 7 0 0 0 3.072 2.472M3.82 11a13.7 13.7 0 0 1-.312-2.5h-2.49c.062.89.291 1.733.656 2.5zm6.853 3.472A7 7 0 0 0 13.745 12H11.91a9.3 9.3 0 0 1-.64 1.539 7 7 0 0 1-.597.933M8.5 12v2.923c.67-.204 1.335-.82 1.887-1.855q.26-.487.468-1.068zm3.68-1h2.146c.365-.767.594-1.61.656-2.5h-2.49a13.7 13.7 0 0 1-.312 2.5m2.802-3.5a7 7 0 0 0-.656-2.5H12.18c.174.782.282 1.623.312 2.5zM11.27 2.461c.247.464.462.98.64 1.539h1.835a7 7 0 0 0-3.072-2.472c.218.284.418.598.597.933M10.855 4a8 8 0 0 0-.468-1.068C9.835 1.897 9.17 1.282 8.5 1.077V4z"/>',
    "arrow-up": '<path d="M16 8A8 8 0 1 0 0 8a8 8 0 0 0 16 0m-7.5 3.5a.5.5 0 0 1-1 0V5.707L5.354 7.854a.5.5 0 1 1-.708-.708l3-3a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 5.707z"/>',
}

SITE = "明るい低炭素社会 社会実験事例データベース"
DESCRIPTION = "明るい低炭素社会の実現に向けた都市変革プログラムの社会実験（10 件）と、その事例（38 件）のデータベース。"


def clean(v):
    return str(v).replace("\\\n", "\n").replace("\\n", "\n")


def text(g, s, field):
    v = g.value(s, SE[field])
    if v is None:
        return ""
    return clean(v)


def local_id(uri):
    assert uri.startswith(BASE_URI), uri
    return uri[len(BASE_URI):]


def br(s):
    """文字列をエスケープし、改行を <br> にする"""
    return Markup("<br>\n").join(escape(line) for line in str(s).split("\n"))


def jsonld(g, s):
    """資源 s を主語とするトリプルを JSON-LD にする（語は se: のまま）"""
    sub = rdflib.Graph()
    sub.bind("se", SE)
    for t in g.triples((s, None, None)):
        sub.add(t)
    doc = json.loads(sub.serialize(format="json-ld", context={"se": str(SE)}, auto_compact=True))
    # </script> で閉じないように
    return json.dumps(doc, ensure_ascii=False, indent=1).replace("</", "<\\/")


def write(path, s):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)


def main():
    g = rdflib.Graph()
    g.parse(ROOT / "assets/rdf/data.rdf")

    # 文字列を整えたグラフ（Turtle と JSON-LD の元）
    clean_g = rdflib.Graph()
    clean_g.bind("se", SE)
    for s_, p, o in g:
        if isinstance(o, rdflib.Literal):
            o = rdflib.Literal(clean(o), lang=o.language, datatype=o.datatype)
        clean_g.add((s_, p, o))

    experiments = {}
    for s in sorted(g.subjects(SE.exTitle, None)):
        e = {"uri": str(s), "id": local_id(str(s))}
        for f in EXP_FIELDS:
            e[f] = text(g, s, f)
        e["cases"] = []
        experiments[str(s)] = e

    cases = []
    for s in sorted(g.subjects(SE.title, None)):
        c = {"uri": str(s), "id": local_id(str(s))}
        for f in CASE_FIELDS:
            c[f] = text(g, s, f)
        c["experiments"] = []
        for ex in sorted(g.objects(s, SE.exRdfName)):
            e = experiments[str(ex)]
            c["experiments"].append({"uri": e["uri"], "id": e["id"], "title": e["exTitle"]})
            e["cases"].append(c["uri"])
        if c["location"]:
            lat, lon = PLACES[c["location"]]
            c["lat"], c["lon"] = lat, lon
        cases.append(c)

    out = ROOT / "assets/data"
    for name, data in [("cases", cases), ("experiments", list(experiments.values()))]:
        write(out / f"{name}.json", json.dumps(data, ensure_ascii=False, indent=1) + "\n")

    clean_g.serialize(ROOT / "assets/rdf/data.ttl", format="turtle")

    # --- HTML ---
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(ROOT / "tools/templates"),
        autoescape=True, keep_trailing_newline=True)
    env.filters["br"] = br
    env.filters["urlencode_all"] = lambda s: quote(str(s), safe="")
    env.globals.update(
        SITE=SITE, DESCRIPTION=DESCRIPTION,
        LD_BROWSER="https://browser.ldas.jp/?u=", DATA_TTL=SITE_URL + "assets/rdf/data.ttl",
        CASE_ROWS=CASE_ROWS, EXP_ROWS=EXP_ROWS, FILTERS=FILTERS, ANALYZE_FIELDS=ANALYZE_FIELDS,
        icon=lambda name: Markup(
            '<svg class="bi" width="1em" height="1em" fill="currentColor" viewBox="0 0 16 16" '
            f'aria-hidden="true">{ICONS[name]}</svg>'),
    )

    def render(template, dest, **kw):
        write(ROOT / dest, env.get_template(template).render(**kw))

    case_by_uri = {c["uri"]: c for c in cases}
    group_by_key = {gr["key"]: gr for gr in GROUPS}

    # グループごとの社会実験（事例の並びで最初に出た順。2014 年版と同じ）
    groups = []
    for gr in GROUPS:
        seen, exps = set(), []
        for c in cases:
            if c["group"] != gr["key"]:
                continue
            for ce in c["experiments"]:
                if ce["uri"] not in seen:
                    seen.add(ce["uri"])
                    exps.append(experiments[ce["uri"]])
        groups.append({**gr, "experiments": exps})

    render("index.html", "index.html", root="", groups=groups)

    filter_values = {k: sorted({c[k] for c in cases if c[k]}) for k in ["group", "process", "type", "condition"]}
    filter_values["exp"] = sorted(e["exTitle"] for e in experiments.values())
    render("search.html", "search.html", root="", active="search", page_title="検索", filter_values=filter_values)
    render("map.html", "map.html", root="", active="map", page_title="地図検索",
           located=sum(1 for c in cases if "lat" in c))
    render("analyze.html", "analyze.html", root="", active="analyze", page_title="分析")
    render("redirect.html", "detail.html", root="", old="detail", dir="case", what="事例",
           list_href="search.html", list_label="検索")
    render("redirect.html", "group.html", root="", old="group", dir="experiment", what="社会実験",
           list_href="./", list_label="トップページ")

    for c in cases:
        render("case.html", f"case/{c['id']}.html", root="../", c=c,
               group=group_by_key.get(c["group"]), ld_target=c["uri"],
               page_title=c["title"], description=f"{c['title']}（{c['group']}の社会実験事例）",
               jsonld=jsonld(clean_g, rdflib.URIRef(c["uri"])))

    for e in experiments.values():
        ecases = [case_by_uri[u] for u in e["cases"]]
        group = group_by_key.get(ecases[0]["group"]) if ecases else None
        # 2014 年版の一覧と同じく、フェーズの降順
        ecases = sorted(ecases, key=lambda c: c["process"], reverse=True)
        render("experiment.html", f"experiment/{e['id']}.html", root="../", e=e, cases=ecases,
               group=group, ld_target=e["uri"], page_title=e["exTitle"],
               description=f"社会実験「{e['exTitle']}」の概要と関連事例",
               jsonld=jsonld(clean_g, rdflib.URIRef(e["uri"])))

    print(f"cases {len(cases)}, experiments {len(experiments)}, triples {len(g)}")


if __name__ == "__main__":
    main()
