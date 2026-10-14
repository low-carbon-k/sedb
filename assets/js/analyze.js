// 分析。グループごとに、選んだ項目（フェーズ・対応状況・課題の種別）の値ごとの事例数を数えて棒グラフにする。
// 事例 1 件を 1 と数える（複数の社会実験に属する事例も 1 回だけ）。

(function () {
  var select = document.getElementById("field");
  var table = document.getElementById("counts");
  // 元の index.html のグループの色
  var COLORS = ["#C2CA2D", "#E39E52", "#E2536B", "#C04F88", "#1F7FB1", "#939494",
    "#99A021", "#B88043", "#B84357", "#9C406E", "#19668F"];
  var chart = null;
  var cases = [];

  function count(field) {
    var groups = [];
    var values = [];
    var n = {};
    cases.forEach(function (c) {
      var v = c[field];
      if (groups.indexOf(c.group) == -1) groups.push(c.group);
      if (!v) return;
      if (values.indexOf(v) == -1) values.push(v);
      var k = c.group + "\t" + v;
      n[k] = (n[k] || 0) + 1;
    });
    groups.sort();
    values.sort();
    return { groups: groups, values: values, n: function (g, v) { return n[g + "\t" + v] || 0; } };
  }

  function drawTable(r) {
    table.replaceChildren();
    var thead = SEDB.el("thead");
    var tr = SEDB.el("tr");
    tr.append(SEDB.el("th", {}, "グループ"));
    r.values.forEach(function (v) { tr.append(SEDB.el("th", {}, v)); });
    thead.append(tr);
    table.append(thead);
    var tbody = SEDB.el("tbody");
    r.groups.forEach(function (g) {
      var tr = SEDB.el("tr");
      tr.append(SEDB.el("th", { scope: "row" }, g));
      r.values.forEach(function (v) { tr.append(SEDB.el("td", { "class": "text-end" }, String(r.n(g, v)))); });
      tbody.append(tr);
    });
    table.append(tbody);
  }

  function show() {
    var field = select.value;
    var label = select.options[select.selectedIndex].text;
    var r = count(field);
    var datasets = r.values.map(function (v, i) {
      return {
        label: v,
        data: r.groups.map(function (g) { return r.n(g, v); }),
        backgroundColor: COLORS[i % COLORS.length]
      };
    });
    if (chart) chart.destroy();
    chart = new Chart(document.getElementById("chart"), {
      type: "bar",
      data: { labels: r.groups, datasets: datasets },
      options: {
        maintainAspectRatio: false,
        plugins: { title: { display: true, text: "『" + label + "』に関する分析" } },
        scales: {
          x: { title: { display: true, text: "グループ" } },
          y: { beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: "事例数" } }
        }
      }
    });
    drawTable(r);
  }

  select.addEventListener("change", show);
  SEDB.load().then(function (data) {
    cases = data.cases;
    show();
  });
})();
