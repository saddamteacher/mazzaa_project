/* Калькулятор заказа: состав хранится в браузере, все цифры считает сервер (/api/calc/). */
(function () {
  'use strict';
  var el = document.getElementById('calc'); if (!el) return;
  var KEY = 'mazzaa_cart', L = JSON.parse(document.getElementById('calc-labels').textContent);
  var access = el.dataset.access === '1', cur = el.dataset.currency, used = false, timer, seq = 0;
  var csrf = (document.querySelector('[name=csrfmiddlewaretoken]') || {}).value || '';
  var rows = {}, cart = {};
  function $(id) { return document.getElementById(id); }
  function fmt(n, d) { return n == null ? '—' : Number(n).toLocaleString(document.documentElement.lang, { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); }
  try { cart = JSON.parse(localStorage.getItem(KEY)) || {}; } catch (e) { cart = {}; }

  el.querySelectorAll('.row').forEach(function (row) {
    var id = row.dataset.id, input = row.querySelector('input');
    rows[id] = { row: row, input: input, name: row.querySelector('b').textContent };
    input.addEventListener('input', function () { set(id, input.value); });
    row.querySelectorAll('[data-step]').forEach(function (b) {
      b.addEventListener('click', function () { set(id, (cart[id] || 0) + (+b.dataset.step)); });
    });
  });
  Object.keys(cart).forEach(function (id) { if (!rows[id]) delete cart[id]; });
  var add = new URLSearchParams(location.search).get('add');
  if (add && rows[add] && !cart[add]) cart[add] = 1;

  function set(id, value) {
    var n = Math.max(0, Math.min(100000, parseInt(value, 10) || 0));
    if (n) cart[id] = n; else delete cart[id];
    if (!used) { used = true; if (window.mzTrack) window.mzTrack('calculator_use'); }
    render(); schedule();
  }
  function items() { return Object.keys(cart).map(function (id) { return { id: +id, boxes: cart[id] }; }); }
  function render() {
    Object.keys(rows).forEach(function (id) {
      var r = rows[id], n = cart[id] || 0;
      if (document.activeElement !== r.input || !n) r.input.value = n;
      r.row.classList.toggle('is-on', n > 0);
    });
    try { localStorage.setItem(KEY, JSON.stringify(cart)); } catch (e) {}
    var payload = JSON.stringify(items());
    document.querySelectorAll('input[name=items]').forEach(function (i) { i.value = payload; });
  }
  function schedule() { clearTimeout(timer); timer = setTimeout(calc, 180); }
  function calc() {
    var mine = ++seq, list = items();
    if (!list.length) return show(null);
    fetch(el.dataset.api, { method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrf }, body: JSON.stringify({ items: list }) })
      .then(function (r) { return r.json(); })
      .then(function (data) { if (mine === seq) show(data); })
      .catch(function () {});
  }
  function show(d) {
    var has = !!(d && d.lines.length);
    $('sum-empty').hidden = has; $('sum-totals').hidden = !has; $('sum-actions').hidden = !has;
    $('sum-cont').hidden = !(has && d.containers['20']);
    var ul = $('sum-lines'); ul.textContent = '';
    if (!has) return;
    d.lines.forEach(function (l) {
      var li = document.createElement('li'), name = document.createElement('b'), qty = document.createElement('span'), del = document.createElement('button');
      name.textContent = l.name + ' · ' + l.weight_g;
      qty.textContent = l.boxes + ' ' + L.boxes + (l.amount != null ? ' · ' + fmt(l.amount) : '');
      del.type = 'button'; del.textContent = '×'; del.title = L.remove; del.setAttribute('aria-label', L.remove + ': ' + l.name);
      del.addEventListener('click', function () { set(String(l.id), 0); });
      li.appendChild(name); li.appendChild(qty); li.appendChild(del); ul.appendChild(li);
    });
    var part = ' (' + L.partial + ')';
    $('t-boxes').textContent = fmt(d.total_boxes);
    $('t-amount').textContent = d.has_prices ? fmt(d.total_amount, 2) + ' ' + cur : '🔒';
    $('t-weight').textContent = fmt(d.total_weight_kg, 1) + ' ' + L.kg + (d.weight_complete ? '' : part);
    $('t-volume').textContent = fmt(d.total_volume_m3, 2) + ' ' + L.m3 + (d.volume_complete ? '' : part);
    $('t-pallets').textContent = d.pallets == null ? '—' : fmt(d.pallets);
    ['20', '40'].forEach(function (k) {
      var c = d.containers[k]; if (!c) return;
      $('c' + k).textContent = c.count + ' × · ' + L.fill + ' ' + fmt(c.fill_percent, 1) + '%';
      $('c' + k + 'bar').style.width = Math.min(100, c.fill_percent / c.count) + '%';
    });
  }
  $('clear').addEventListener('click', function () { cart = {}; render(); show(null); });
  if (document.getElementById('order-form')) document.getElementById('order-form').addEventListener('submit', function () {
    try { localStorage.removeItem(KEY); } catch (e) {}
  });
  render(); calc();
})();
