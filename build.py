#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка сайта Piter.school.

Сканирует папки-предметы в корне репозитория, находит все файлы .md
и создаёт папку site/ со статическим сайтом:
  site/index.html      — главная страница (список предметов и заданий + поиск)
  site/task.html       — страница задания (рендерит Markdown в браузере)
  site/manifest.json   — список всех заданий (обновляется автоматически)
  site/content/...     — копии .md файлов
  site/assets/...      — стили, скрипты, картинки

Как добавить задание: просто положи .md файл в папку предмета и запусти
`python build.py` (или запушь в main — GitHub Action соберёт сам).
"""
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SITE = ROOT / "site"

# Папки, которые не являются предметами
SKIP_DIRS = {".git", ".github", "site", "__pycache__"}

# Эмодзи для известных предметов (остальным — 📘)
SUBJECT_ICONS = {
    "математика": "📐",
    "русский язык": "✏️",
    "литература": "📚",
    "английский язык": "🇬🇧",
    "история": "🏛️",
    "география": "🌍",
    "биология": "🌿",
    "физика": "⚡",
    "химия": "🧪",
    "информатика": "💻",
    "обществознание": "👥",
    "физкультура": "⚽",
    "музыка": "🎵",
    "изо": "🎨",
    "технология": "🔧",
}


def extract_title(md_path: Path) -> str:
    """Берём заголовок задания из первой строки '# ...' файла."""
    try:
        text = md_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = md_path.read_text(encoding="utf-8-sig")
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+)", line.strip())
        if m:
            return m.group(1).strip()
    return md_path.stem


def main() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    # Копируем статику (html/css/js/img лежат в web/)
    web = ROOT / "web"
    if not web.is_dir():
        sys.exit("Ошибка: папка web/ с шаблонами сайта не найдена")
    shutil.copytree(web, SITE, dirs_exist_ok=True)

    manifest = []
    for subject_dir in sorted(ROOT.iterdir(), key=lambda p: p.name.lower()):
        if not subject_dir.is_dir() or subject_dir.name in SKIP_DIRS:
            continue
        md_files = sorted(subject_dir.glob("*.md"), key=lambda p: p.name.lower())
        if not md_files:
            continue
        for md in md_files:
            rel = md.relative_to(ROOT).as_posix()
            target = SITE / "content" / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(md, target)
            manifest.append({
                "subject": subject_dir.name,
                "icon": SUBJECT_ICONS.get(subject_dir.name.lower(), "📘"),
                "file": md.name,
                "title": extract_title(md),
                "path": "content/" + rel,
            })

    (SITE / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    # GitHub Pages: отключаем Jekyll — сайт чисто статический
    (SITE / ".nojekyll").touch()
    print(f"Готово: {len(manifest)} заданий -> {SITE}")
    for item in manifest:
        print(f"  {item['icon']} {item['subject']} / {item['title']}")


if __name__ == "__main__":
    main()
