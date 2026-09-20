/* Страница задания: рендер Markdown, видимая «Самостоятельная работа»,
   скрытые «Ответы» с кнопкой «Показать ответы» */
(function () {
  "use strict";

  var params = new URLSearchParams(location.search);
  var path = params.get("path");
  var subject = params.get("subject") || "";
  var icon = params.get("icon") || "📘";
  var article = document.getElementById("content");
  var base = location.pathname.replace(/task\.html$/, "");

  if (subject) {
    document.getElementById("crumb-subject").textContent = icon + " " + subject;
  }

  if (!path) {
    article.innerHTML = '<p class="empty">Задание не указано.</p>';
    return;
  }

  fetch(base + path)
    .then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.text();
    })
    .then(function (md) { renderMarkdown(md); })
    .catch(function () {
      article.innerHTML = '<p class="empty">Не удалось загрузить задание 😢 ' +
        '<a href="index.html">К списку заданий</a></p>';
    });

  function renderMarkdown(md) {
    if (typeof marked === "undefined") {
      // CDN недоступен — показываем текст как есть
      article.innerHTML = "";
      var pre = document.createElement("pre");
      pre.style.whiteSpace = "pre-wrap";
      pre.textContent = md;
      article.appendChild(pre);
      return;
    }

    marked.setOptions({ breaks: true, gfm: true });
    article.innerHTML = marked.parse(md);

    // Заголовок вкладки — из первого h1
    var h1 = article.querySelector("h1");
    if (h1) document.title = h1.textContent + " — Piter.school";

    wrapSections();
    fixImagePaths();
    renderMath();
  }

  /* Картинки из .md лежат рядом с файлом в content/ — чиним относительные пути */
  function fixImagePaths() {
    var dir = path.substring(0, path.lastIndexOf("/") + 1);
    Array.prototype.forEach.call(article.querySelectorAll("img"), function (img) {
      var src = img.getAttribute("src");
      if (src && !/^(https?:)?\/\//.test(src) && src.charAt(0) !== "/" && src.indexOf("data:") !== 0) {
        img.src = base + dir + src;
      }
    });
  }

  /* Оборачиваем разделы h2: «Самостоятельная работа» — в зелёный блок,
     «Ответы» — в скрытый блок с кнопкой */
  function wrapSections() {
    var nodes = Array.prototype.slice.call(article.children);
    var i = 0;
    while (i < article.children.length) {
      var el = article.children[i];
      if (el.tagName !== "H2") { i++; continue; }
      var text = el.textContent.toLowerCase();

      if (text.indexOf("самостоятельн") !== -1) {
        wrapUntilNextH2(el, "hw-section");
        i++; // блок-обёртка теперь один элемент на месте h2
      } else if (text.indexOf("ответ") !== -1) {
        wrapAnswers(el);
        break;
      } else {
        i++;
      }
    }
  }

  /* Переносит h2 и все узлы до следующего h2 в div с классом cls.
     Возвращает число поглощённых узлов. */
  function wrapUntilNextH2(h2, cls) {
    var box = document.createElement("div");
    box.className = cls;
    article.insertBefore(box, h2);
    var count = 0;
    var node = h2;
    while (node && !(node !== h2 && node.tagName === "H2")) {
      var next = node.nextSibling;
      box.appendChild(node);
      count++;
      node = next;
    }
    return count;
  }

  function wrapAnswers(h2) {
    var btn = document.createElement("button");
    btn.className = "answers-toggle";
    btn.type = "button";
    btn.textContent = "🙈 Показать ответы";

    var box = document.createElement("div");
    box.className = "answers-box";

    article.insertBefore(btn, h2);
    article.insertBefore(box, h2);
    var node = h2;
    while (node) {
      var next = node.nextSibling;
      box.appendChild(node);
      node = next;
    }

    btn.addEventListener("click", function () {
      var open = box.classList.toggle("open");
      btn.textContent = open ? "🙉 Скрыть ответы" : "🙈 Показать ответы";
    });
  }

  function renderMath() {
    if (typeof renderMathInElement === "function") {
      renderMathInElement(article, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "\\[", right: "\\]", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false }
        ],
        throwOnError: false
      });
    }
  }
})();
