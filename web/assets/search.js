(function () {
  var docs = window.__SEARCH__ || [];
  var q = document.getElementById('q');
  var box = document.getElementById('results');
  if (!q || !box) return;
  function run() {
    var kw = q.value.trim().toLowerCase();
    box.innerHTML = '';
    if (!kw) return;
    var hits = docs.filter(function (d) {
      return (d.t + ' ' + d.k).toLowerCase().indexOf(kw) >= 0;
    }).slice(0, 20);
    if (!hits.length) { box.innerHTML = '<p class="no-hit">没有匹配的内容</p>'; return; }
    box.innerHTML = hits.map(function (d) {
      return '<a class="hit" href="' + d.u + '"><strong>' + d.t + '</strong><span>' + d.k.slice(0, 80) + '…</span></a>';
    }).join('');
  }
  q.addEventListener('input', run);
})();
