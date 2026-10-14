// データの読み込み。以前は dydra の SPARQL に問い合わせていたが、
// 今は tools/build_json.py が data.rdf から作った JSON を読む。

var SEDB = {};

SEDB.load = function() {
	return $.when(
		$.getJSON("assets/data/cases.json"),
		$.getJSON("assets/data/experiments.json")
	).then(function(c, e) {
		var data = {
			cases : c[0],
			experiments : e[0],
			caseByUri : {},
			expByUri : {}
		};
		$.each(data.cases, function(i, obj) {
			data.caseByUri[obj.uri] = obj;
		});
		$.each(data.experiments, function(i, obj) {
			data.expByUri[obj.uri] = obj;
		});
		return data;
	});
};

// 事例 × 所属する社会実験 の行に展開する（1 事例が複数の実験に属することがある）
SEDB.rows = function(data) {
	var rows = [];
	$.each(data.cases, function(i, c) {
		$.each(c.experiments, function(j, e) {
			rows.push({ c : c, exp : e });
		});
	});
	return rows;
};

SEDB.param = function(name) {
	var url = location.search.substring(1).split('&');
	for (var i = 0; url[i]; i++) {
		var k = url[i].split('=');
		if (k[0] == name) {
			return decodeURIComponent(k[1]);
		}
	}
	return null;
};

SEDB.escape = function(s) {
	return $("<div>").text(s).html();
};

// 文字列をエスケープし、改行を <br> にする
SEDB.html = function(s) {
	return SEDB.escape(s).replace(/\n/g, "<br>");
};
