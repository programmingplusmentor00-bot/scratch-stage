#!/usr/bin/env python3
"""
uploads/ フォルダにある html または sb3 ファイルを
works/ フォルダにコピーし、works.json を更新するスクリプト。

ファイルの命名ルール:
  {作者名}_{作品タイトル}.html  （TurboWarp Packagerで変換済みのHTML）
  {作者名}_{作品タイトル}.sb3   （sb3ファイル）
  例: たろう_ねこのゲーム.html
"""

import json
import re
import shutil
from datetime import date
from pathlib import Path

UPLOADS_DIR = Path("uploads")
WORKS_DIR   = Path("works")
WORKS_JSON  = Path("works.json")

WORKS_DIR.mkdir(exist_ok=True)

if WORKS_JSON.exists():
    with open(WORKS_JSON, encoding="utf-8") as f:
        works: list[dict] = json.load(f)
else:
    works = []

existing_ids = {w["id"] for w in works}

# .html と .sb3 の両方を処理
for path in sorted(list(UPLOADS_DIR.glob("*.html")) + list(UPLOADS_DIR.glob("*.sb3"))):
    stem = path.stem
    ext  = path.suffix  # .html or .sb3

    if "_" in stem:
        author, title = stem.split("_", 1)
    else:
        author, title = "", stem

    work_id = re.sub(r"[^\w\-]", "-", stem, flags=re.UNICODE).strip("-") or stem
    base_id = work_id
    counter = 1
    while work_id in existing_ids:
        work_id = f"{base_id}-{counter}"
        counter += 1

    dest = WORKS_DIR / f"{work_id}{ext}"
    if dest.exists():
        print(f"スキップ（既に登録済み）: {path.name}")
        continue

    print(f"コピー中: {path.name} → works/{work_id}{ext}")
    shutil.copy2(path, dest)

    entry = {
        "id":     work_id,
        "title":  title,
        "author": author,
        "date":   date.today().isoformat(),
        "file":   f"{work_id}{ext}",
        "type":   "html" if ext == ".html" else "sb3",
    }
    works.append(entry)
    existing_ids.add(work_id)
    print(f"  ✅ 追加: {title}（{author}）")

with open(WORKS_JSON, "w", encoding="utf-8") as f:
    json.dump(works, f, ensure_ascii=False, indent=2)

print(f"\n✨ works.json を更新しました（合計 {len(works)} 作品）")
