// 一覧の表で、行のどこを押しても詳細の画面へ移る（tr に data-href がある行）。
// 行の中のリンクやボタンを押したとき、文字を選んでいるときは、そちらを優先する。

document.addEventListener("click", function (ev) {
  var tr = ev.target.closest("tr[data-href]");
  if (!tr || ev.target.closest("a, button, input, select, label")) return;
  if (String(window.getSelection())) return;
  if (ev.ctrlKey || ev.metaKey || ev.shiftKey) {
    window.open(tr.dataset.href, "_blank");
  } else {
    location.href = tr.dataset.href;
  }
});
