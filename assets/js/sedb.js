// 検索・地図・分析の画面が共通で使う読み込み。
// データは tools/build_json.py が data.rdf から作った JSON（以前は dydra の SPARQL に問い合わせていた）。

var SEDB = {};

SEDB.load = function () {
  return Promise.all([
    fetch("assets/data/cases.json").then(function (r) { return r.json(); }),
    fetch("assets/data/experiments.json").then(function (r) { return r.json(); })
  ]).then(function (res) {
    return { cases: res[0], experiments: res[1] };
  });
};

// 事例 × 所属する社会実験 の行に展開する（1 事例が複数の実験に属することがある）
SEDB.rows = function (data) {
  var rows = [];
  data.cases.forEach(function (c) {
    c.experiments.forEach(function (e) {
      rows.push({ c: c, exp: e });
    });
  });
  return rows;
};

SEDB.caseHref = function (c) {
  return "case/" + c.id + ".html";
};

SEDB.expHref = function (e) {
  return "experiment/" + e.id + ".html";
};

// 要素を作る。text は文字として入れる（HTML として解釈しない）
SEDB.el = function (tag, attrs, text) {
  var el = document.createElement(tag);
  Object.keys(attrs || {}).forEach(function (k) {
    el.setAttribute(k, attrs[k]);
  });
  if (text !== undefined) {
    el.textContent = text;
  }
  return el;
};
