// 地図検索。座標は tools/build_json.py が地名から引いて JSON に入れてある。

(function () {
  var map = L.map("map").setView([35.859251, 139.983061], 12);
  L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  var markers = L.markerClusterGroup();

  function popup(c, exp) {
    var div = SEDB.el("div", { "class": "map-popup" });
    var a = SEDB.el("a", { href: SEDB.caseHref(c) });
    a.append(SEDB.el("img", { src: "assets/images/apple-touch-icon.png", alt: "", width: 48, height: 48 }));
    div.append(a);
    var body = SEDB.el("div");
    body.append(SEDB.el("strong", {}, c.title));
    body.append(SEDB.el("div", { "class": "small" }, exp.title));
    body.append(SEDB.el("a", { href: SEDB.caseHref(c) }, "詳細"));
    div.append(body);
    return div;
  }

  SEDB.load().then(function (data) {
    SEDB.rows(data).forEach(function (row) {
      var c = row.c;
      if (c.lat === undefined) return;
      var marker = L.marker([c.lat, c.lon], { title: c.title + "（" + row.exp.title + "）", alt: c.title });
      marker.bindPopup(popup(c, row.exp));
      markers.addLayer(marker);
    });
    map.addLayer(markers);
  });
})();
