# sedb

明るい低炭素社会 社会実験事例データベース（https://low-carbon-k.github.io/sedb/）

## 作り方

データの正本は `assets/rdf/data.rdf`。ページと配布用のデータは、ここから作る。

```
pip install rdflib jinja2
python3 tools/build_json.py
```

- ページのひな形は `tools/templates/`。生成した HTML（`index.html` ほか、`case/`、`experiment/`）は
  そのままコミットする。GitHub Pages は master の直下を配る（Actions は使わない）。
- 事例・社会実験の画面は 1 件 1 ページの静的ページで、その資源の記述を JSON-LD で埋め込んでいる。
- 旧 URL の `detail.html?uri=…` と `group.html?uri=…` は、静的ページへ移る。
- 経緯は `docs/notes/static-site.md`。

## データ

- `assets/rdf/data.rdf`（RDF/XML）、`assets/rdf/data.ttl`（Turtle）、`assets/rdf/vocab.ttl`（語彙）
- `assets/data/cases.json`、`assets/data/experiments.json`
