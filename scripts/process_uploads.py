#!/usr/bin/env python3
"""
uploads/ フォルダにある zip ファイルを展開して
works/ フォルダに配置し、works.json を更新するスクリプト。

zip ファイルの命名ルール:
  {作者名}_{作品タイトル}.zip
  例: たろう_ねこのゲーム.zip

アンダースコアが含まれない場合はファイル名全体を作品タイトルとして使用。
"""

import json
import os
import re
import zipfile
from datetime import date, datetime
from pathlib import Path

UPLOADS_DIR = Path("uploads")
WORKS_DIR   = Path("works")
WORKS_JSON  = Path("works.json")

WORKS_DIR.mkdir(exist_ok=True)

# 既存の works.json を読み込む
if WORKS_JSON.exists():
    with open(WORKS_JSON, encoding="utf-8") as f:
        works: list[dict] = json.load(f)
else:
    works = []

existing_ids = {w["id"] for w in works}

# uploads/ にある zip を処理
for zip_path in sorted(UPLOADS_DIR.glob("*.zip")):
    stem = zip_path.stem  # 拡張子なしファイル名

    # 作者名と作品タイトルをパース
    if "_" in stem:
        author, title = stem.split("_", 1)
    else:
        author, title = "", stem

    # IDは英数字・ハイフンのみに正規化（日本語はそのまま使うと問題になるので）
    work_id = re.sub(r"[^\w\-]", "-", stem, flags=re.UNICODE).strip("-") or stem
    # 重複IDを避けるためにサフィックスを付加
    base_id = work_id
    counter = 1
    while work_id in existing_ids:
        work_id = f"{base_id}-{counter}"
        counter += 1

    work_dir = WORKS_DIR / work_id
    if work_dir.exists():
        print(f"スキップ（既に展開済み）: {zip_path.name}")
        continue

    print(f"展開中: {zip_path.name} → works/{work_id}/")
    work_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(work_dir)
    except zipfile.BadZipFile:
        print(f"  ⚠ 壊れたzipファイルをスキップ: {zip_path.name}")
        work_dir.rmdir()
        continue

    # index.html が直下にない場合、サブフォルダから探して移動
    if not (work_dir / "index.html").exists():
        found = list(work_dir.rglob("index.html"))
        if found:
            import shutil
            sub = found[0].parent
            for item in sub.iterdir():
                shutil.move(str(item), str(work_dir / item.name))
            # 空フォルダを削除
            try:
                sub.rmdir()
            except OSError:
                pass

    # サムネイル候補を探す（thumbnail.png / screenshot.png）
    thumbnail = None
    for name in ("thumbnail.png", "thumbnail.jpg", "screenshot.png", "screenshot.jpg"):
        if (work_dir / name).exists():
            thumbnail = name
            break

    entry = {
        "id":        work_id,
        "title":     title,
        "author":    author,
        "date":      date.today().isoformat(),
        "thumbnail": thumbnail,
    }
    works.append(entry)
    existing_ids.add(work_id)
    print(f"  ✅ 追加: {title}（{author}）")

# works.json を保存
with open(WORKS_JSON, "w", encoding="utf-8") as f:
    json.dump(works, f, ensure_ascii=False, indent=2)

print(f"\n✨ works.json を更新しました（合計 {len(works)} 作品）")
