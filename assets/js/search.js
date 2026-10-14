// 検索画面。条件は URL（?q=…&target=keyword&exp=…）に載せるので、検索結果にそのままリンクできる。

(function () {
  var form = document.getElementById("search-form");
  var tbody = document.getElementById("list");
  var count = document.getElementById("count");
  var FILTERS = ["group", "exp", "process", "type", "condition"];
  // 全文検索の対象にする事例の項目
  var TEXT_FIELDS = ["title", "group", "process", "type", "problem", "problemSystem",
    "problemInterest", "problemDiffusion", "problemTech", "influence",
    "solution", "service", "improvement", "condition", "suggestion",
    "place", "keyword", "location"];

  var rows = [];
  // 旧サイトの初期表示（グループ名の降順）に合わせる
  var sort = { key: "group", dir: -1 };

  function value(row, key) {
    return key == "exp" ? row.exp.title : row.c[key];
  }

  function readForm() {
    var cond = {};
    new FormData(form).forEach(function (v, k) {
      v = v.trim();
      if (v) cond[k] = v;
    });
    if (cond.target == "all") delete cond.target;
    return cond;
  }

  function writeForm(cond) {
    form.q.value = cond.q || "";
    form.querySelector('input[name=target][value="' + (cond.target == "keyword" ? "keyword" : "all") + '"]').checked = true;
    FILTERS.forEach(function (k) {
      form[k].value = cond[k] || "";
    });
  }

  function match(row, cond) {
    var c = row.c;
    if (cond.q) {
      var fields = cond.target == "keyword" ? ["keyword"] : TEXT_FIELDS;
      var q = cond.q.toLowerCase();
      var hit = fields.some(function (f) {
        return c[f].toLowerCase().indexOf(q) != -1;
      });
      if (!hit) return false;
    }
    return FILTERS.every(function (k) {
      return !cond[k] || value(row, k) == cond[k];
    });
  }

  function render() {
    var cond = readForm();
    var hits = rows.filter(function (row) { return match(row, cond); });
    hits.sort(function (a, b) {
      return sort.dir * value(a, sort.key).localeCompare(value(b, sort.key), "ja");
    });
    tbody.replaceChildren();
    if (!hits.length) {
      var empty = SEDB.el("tr");
      empty.append(SEDB.el("td", { colspan: 7, "class": "text-center py-4" },
        "条件に合う事例はありません。キーワードや絞り込みを変えてみてください。"));
      tbody.append(empty);
    }
    hits.forEach(function (row) {
      var c = row.c;
      var tr = SEDB.el("tr", { "data-href": SEDB.caseHref(c) });
      var td = SEDB.el("td");
      td.append(SEDB.el("a", { href: SEDB.caseHref(c) }, c.title));
      tr.append(td);
      td = SEDB.el("td");
      td.append(SEDB.el("a", { href: "./?group=" + encodeURIComponent(c.group) }, c.group));
      tr.append(td);
      td = SEDB.el("td");
      td.append(SEDB.el("a", { href: SEDB.expHref(row.exp) }, row.exp.title));
      tr.append(td);
      tr.append(SEDB.el("td", {}, c.process));
      tr.append(SEDB.el("td", {}, c.type));
      tr.append(SEDB.el("td", {}, c.keyword));
      td = SEDB.el("td");
      var a = SEDB.el("a", { href: SEDB.caseHref(c), "class": "btn btn-home btn-sm text-nowrap" }, "詳細 »");
      td.append(a);
      tr.append(td);
      tbody.append(tr);
    });
    count.textContent = hits.length + " 件（全 " + rows.length + " 件）";
    document.querySelectorAll("button.sort").forEach(function (b) {
      var th = b.parentNode;
      if (b.dataset.key == sort.key) {
        th.setAttribute("aria-sort", sort.dir > 0 ? "ascending" : "descending");
      } else {
        th.removeAttribute("aria-sort");
      }
    });
  }

  function updateUrl() {
    var params = new URLSearchParams(readForm());
    var qs = params.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    updateUrl();
    render();
  });
  // 絞り込みとラジオは選んだ時点で、キーワードは打ち終わって少し経ったら反映する
  form.addEventListener("change", function (ev) {
    if (ev.target.name == "q") return;
    updateUrl();
    render();
  });
  var typing;
  form.q.addEventListener("input", function () {
    clearTimeout(typing);
    typing = setTimeout(function () {
      updateUrl();
      render();
    }, 300);
  });
  form.addEventListener("reset", function () {
    // reset の後に値が消えるので、次の周回で描き直す
    setTimeout(function () {
      updateUrl();
      render();
    });
  });
  document.querySelectorAll("button.sort").forEach(function (b) {
    b.addEventListener("click", function () {
      sort = { key: b.dataset.key, dir: sort.key == b.dataset.key ? -sort.dir : 1 };
      render();
    });
  });

  // 「TOP」は少しスクロールしてから出す（スマートフォンで表やボタンに重ならないように）
  var pagetop = document.querySelector(".pagetop");
  function togglePagetop() {
    pagetop.classList.toggle("is-hidden", window.scrollY < 400);
  }
  window.addEventListener("scroll", togglePagetop, { passive: true });
  togglePagetop();

  // 旧サイトの名前 query・textTarget でも受け付ける
  var p = new URLSearchParams(location.search);
  var cond = {};
  p.forEach(function (v, k) { cond[k] = v; });
  if (cond.query && !cond.q) cond.q = cond.query;
  if (cond.textTarget && !cond.target) cond.target = cond.textTarget;
  writeForm(cond);

  SEDB.load().then(function (data) {
    rows = SEDB.rows(data);
    render();
  });
})();
