# dydra をやめて静的サイトにする

## 2026-10-13 現状の確認と計画

### 今のしくみ

- 6 ページ（index / search / group / detail / map / analyze）が、表示のたびに
  jQuery で `https://dydra.com/ut-digital-archives/sedb/sparql` に SPARQL を投げている。
- 地図は Nominatim（OpenStreetMap の住所検索）に地名を毎回問い合わせて座標を得ている。
- 分析グラフは `google.com/jsapi`（廃止済みの Google Charts の読み込み方）。
- リポジトリは 2018-09-17 が最後の push で、アーカイブ済み。

### dydra の全件と data.rdf の突き合わせ

測り方: `CONSTRUCT {?s ?p ?o} WHERE {?s ?p ?o}` を N-Triples で取得
（`data/dydra-2026-10-13.nt`）。名前付きグラフは 0 個、`COUNT(*)` は 751。
LIMIT 500 で 2 ページに分けても 751 で、途中で切れてはいない。
比較は `tools/compare.py`（rdflib の graph_diff）と `tools/diffvals.py`。

| | dydra | data.rdf |
|---|---|---|
| トリプル | 751 | 750 |
| 事例（se:title を持つもの） | 38 | 38 |
| 社会実験（se:exTitle を持つもの） | 10 | 10 |
| se:exRdfName の数 | 41 | 41 |

- 差は 2 種類だけ。
  1. dydra にだけ `<http://dydra.com/> <http://dydra.com/> "more"` という 1 件がある。
     中身のデータではない（dydra 側の混入）。
  2. 41 件の長文で、元データの改行の書き方が違う。dydra は「`\` と `n` の 2 文字」、
     data.rdf は「`\` と本物の改行」。どちらも元の表計算の改行が崩れたもので、
     文字の中身は同じ。
- **結論: data.rdf が dydra の全件と同じ。dydra にしか無いデータは無い。**
- 訂正: 動画の台本係の報告にあった「本番は 41 事例・10 実験」の 41 は、
  事例の数ではなく se:exRdfName の数（1 事例が複数の実験に属するため）。
  事例は 38 で、リポジトリと同じ。
- 10 実験のうち「ちょい山」には事例が 0 件。

### 既知の不具合（台本係の報告）をコードで確かめた結果

- 社会実験名の絞り込みが 0 件: 検索画面が `?s se:exp '…'` を作るが、
  データに se:exp は無い（実験名は se:exRdfName → se:exTitle の 2 段）。
- 「キーワードのみ」が効かない: `if (param[i].value = "all")` が代入になっていて、
  常に全文検索になる。
- フッターのリンク 403: `http://low-carbon.k.u-tokyo.ac.jp/` がもう応答しない。
  事例の URI もこのドメインだが、識別子としてはそのまま残す。
- 地図の背景が灰色: Mapbox v4 の旧 API（Leaflet の例のトークン）が使えない。
- 分析グラフが出ない: `google.com/jsapi` が廃止。

### 計画

方針: **SPARQL をやめ、ビルド時に data.rdf から JSON を作り、ブラウザはそれを読むだけにする。**
ページ構成と URL（`detail.html?…`、`group.html?…`）は今のまま保つ。動画や外部からのリンクを壊さないため。

1. データ
   - 正本は data.rdf のまま（dydra と同じことは確かめた）。改行の崩れ（`\` + 改行）は
     JSON 化のときに改行へ直す。data.rdf そのものは書き換えない。
   - `tools/build_json.py` で `assets/data/cases.json`（38 事例、所属実験の名前を展開済み）と
     `experiments.json`（10 実験）を作る。
   - 地図の座標は、地名 3 種（柏市・柏ビレジ近隣公園 ほか）を一度だけ調べて JSON に書き込む。
     実行時の Nominatim 問い合わせはやめる。
2. ページの差し替え（jQuery と Bootstrap 3 は今のまま。直すのは問い合わせの部分だけ）
   - index / group / detail: SPARQL の代わりに JSON から引く。
   - search: 絞り込みを JS で行う。社会実験名の絞り込みと「キーワードのみ」を直す。
   - map: 背景を OpenStreetMap の標準タイルにし、座標は JSON から。
   - analyze: 集計を JS で行い、グラフは Chart.js（版を固定、cdnjs）にする。
   - フッターの 403 リンクは外すか、説明文に置き換える（要相談）。
3. Linked Data として残すもの
   - data.rdf はそのまま配布し、Turtle（.ttl）も並べる。ページから「データをダウンロード」で
     リンクする。SPARQL の窓口は無くなるが、全件が 1 ファイルで手に入る。
4. 確認
   - 6 ページを手元で開き、38 事例・10 実験が出ること、上の不具合 5 件が直ったことを確かめる。
   - 公開後、動画を撮り直す（今の動画はアップロードしない）。
5. 公開（本人の確認を取ってから）
   - アーカイブ解除 → ブランチで commit → push → GitHub Pages の反映を確認 →
     必要なら再アーカイブ。Pages は master の直下から配っているので、ビルド生成物
     （JSON）もコミットする。

確かめていないこと: dydra の窓口がいつまで動くか。Pages の配信元は master の直下（2026-10-13 に確認）。

## 2026-10-13 計画 1〜4 を実装した（未コミット・未 push）

- `tools/build_json.py` が data.rdf から `assets/data/cases.json`（38 事例）・
  `experiments.json`（10 実験）・`assets/rdf/data.ttl`（750 トリプル）を作る。
  「`\` + 改行」は改行 1 つに直した（出力に `\` は 0 個）。
- 座標は Nominatim で 1 回だけ引いて build_json.py に書いた。地名の入った事例は実は 2 件だけ
  （柏市 35.8676218, 139.9756876 / 柏ビレジ近隣公園 35.9029454, 139.9664862）。
  3 件目の se:location は空文字。
- 共通の読み込みは `assets/js/sedb.js`。6 ページとも dydra・Nominatim・google.com/jsapi・
  Mapbox への問い合わせは 0 件（Playwright で外向きの要求を監視して確かめた）。
  使わなくなった `assets/js/uri.js` の読み込みは外した（ファイルは残した）。
- 各ページで変えたこと:
  - map: 背景を OSM 標準タイル、markercluster は unpkg の 1.4.1 に（以前は leaflet.github.io の
    開発版と例のデータ realworld.388.js を読んでいた）。クリックで座標を出す試験用の吹き出しは外した。
  - analyze: Chart.js 4.4.1（cdnjs、SRI 付き）。**数え方を変えた**: 以前は「事例 × 所属実験」の
    行（41）を数えていたので、2 つの実験に属する事例が 2 回数えられていた。今は事例 1 件を 1 回（38）。
  - search: 社会実験名は所属実験の名前で絞る（コムス 11 件）。「キーワードのみ」は se:keyword だけを
    見る（「大学」で 全文 11 件 / キーワードのみ 1 件）。全文検索は正規表現ではなく、大文字小文字を
    区別しない部分一致にした。選択肢の空の値（対応状況の ""）は出さない。
  - detail: 2 つの実験に属する事例は、社会実験の欄に両方をリンクで並べる（以前は最後の 1 件だけ）。
  - 値は HTML として差し込まず、文字として入れて改行だけ `<br>` にした。
- フッター: 403 のリンクは外し、名前は文字のまま残した。代わりに data.rdf / data.ttl / JSON 2 つへの
  リンクを並べた（計画 3 の「データをダウンロード」）。© 2014 はそのまま。
- 確認（計画 4、手元の http.server + Playwright）: 一覧 41 行、グループ「コミュニティ拠点(柏ビレジ)」9 件、
  地図のピン 2 本と背景タイル表示、分析のグラフ表示、コンソールのエラー 0。
- 残り: 計画 5（アーカイブ解除・push）は本人の確認待ち。公開後に動画を撮り直す。

## 2026-10-13 語彙ファイルとフッターの LD Browser へのリンク（ブランチ vocab-footer、未コミット）

- 名前空間 `http://www.teitanso.org/2012/04/se#` は https へ転送されたあと 404。元の語彙の定義は残っていない。
- `assets/rdf/vocab.ttl` を手で書いた（116 トリプル）。data.rdf が使う属性 25 個すべてに
  rdfs:label（ja・en）を付けた。過不足 0 は rdflib で data.rdf の述語と突き合わせて確かめた。
  日本語名は detail.html・group.html の表の見出しから取った（見出しと値の中身が合うことも数件見た。
  例: se:condition は「対応の結果」で値は「解決」）。英語名はこのとき付けた訳。
  事例・社会実験に型（rdf:type）は無いので、クラスは定義していない。
- フッター（6 ページ）: データの並びに「語彙（Turtle）」を足し、2 行目に「Linked Data として見る: LD Browser」を足した。
  既定はデータ全体（data.ttl）を開く。事例・社会実験の画面では、`assets/js/sedb.js` がその URI を開くリンクに書き換える。
  HTML は CRLF のまま（一度 LF に崩したので戻した）。
- 確認（手元の http.server + Playwright）: 6 ページともリンク先が想定どおり、vocab.ttl は text/turtle で 200、エラー 0。
  公開中の LD Browser で、data.ttl を開くと「この URI を主語とする記述はありません」と出たうえで、下に全資源が並ぶ。
  社会実験の URI は名前付きで開く。
- 確かめていないこと: LD Browser の側はまだ語彙を読まない（属性名は `se:condition` のまま出る）。
- 同日、PR #2 でマージ・公開（7fa2db8）。公開先で vocab.ttl が 200・text/turtle・CORS あり、フッターと sedb.js の反映を確かめた。

## 2026-10-14 Turtle にも「\ + 改行」が残っていた

- 動画の撮り直しで、公開中の data.ttl に「\\」が 62 か所残っているのが見つかった。
  上の「出力に `\` は 0 個」は JSON だけを見た結果で、Turtle は data.rdf の文字列をそのまま書き出していた。
- build_json.py で、Turtle を書く前に文字列を JSON と同じ規則で整えるようにした。
  トリプル数は 750 のまま、「\」は 0 個、JSON は変化なし。data.rdf は今も書き換えていない。
