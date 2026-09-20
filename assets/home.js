/* Главная страница: список предметов и заданий + поиск */
(function () {
  "use strict";

  var base = location.pathname.replace(/index\.html$/, "");
  var main = document.getElementById("subjects");
  var empty = document.getElementById("empty");
  var input = document.getElementById("search");
  var fullHtml = "";

  fetch(base + "manifest.json", { cache: "no-cache" })
    .then(function (r) { return r.json(); })
    .then(function (items) { render(items); })
    .catch(function () {
      main.innerHTML = '<p class="empty">Не удалось загрузить список заданий 😢</p>';
    });

  function taskUrl(item) {
    return base + "task.html?path=" + encodeURIComponent(item.path) +
      "&subject=" + encodeURIComponent(item.subject) +
      "&icon=" + encodeURIComponent(item.icon);
  }

  function cardHtml(item) {
    var img = item.icon === "📐"
      ? "assets/img/subject-math.jpg"
      : "assets/img/subject-default.jpg";
    return '<a class="card" href="' + taskUrl(item) + '">' +
      '<img src="' + img + '" alt="" loading="lazy">' +
      '<div class="card-body">' +
      '<div class="card-title">' + escapeHtml(item.title) + "</div>" +
      '<div class="card-meta">' + escapeHtml(item.subject) + "</div>" +
      "</div></a>";
  }

  function render(items) {
    var bySubject = {};
    items.forEach(function (it) {
      (bySubject[it.subject] = bySubject[it.subject] || []).push(it);
    });

    main.innerHTML = Object.keys(bySubject).map(function (subject) {
      var list = bySubject[subject];
      return '<section class="subject">' +
        '<div class="subject-header"><span class="icon">' + list[0].icon + "</span>" +
        "<h2>" + escapeHtml(subject) + "</h2></div>" +
        '<div class="cards">' + list.map(cardHtml).join("") + "</div></section>";
    }).join("") || '<p class="empty">Заданий пока нет — добавь .md файл в папку предмета.</p>';

    fullHtml = main.innerHTML;
    initSearch(items);
  }

  function initSearch(items) {
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      if (!q) {
        main.innerHTML = fullHtml;
        empty.hidden = true;
        return;
      }
      var found = items.filter(function (it) {
        return (it.title + " " + it.subject).toLowerCase().indexOf(q) !== -1;
      });
      empty.hidden = found.length > 0;
      main.innerHTML = found.length
        ? '<section class="subject"><div class="cards">' +
          found.map(cardHtml).join("") + "</div></section>"
        : "";
    });
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }
})();
