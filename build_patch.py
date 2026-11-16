"""Build an overwrite-ready Korean localization patch for Kingdom.py from reviewed JSONL outputs."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "vendor"))

import polib
import validate_revisions

TARGET_REL = {
    "main": Path("Kingdom_Data/StreamingAssets/Localization/ko.po"),
    "story": Path("Kingdom_Data/StreamingAssets/Mods/story/lang/ko.po"),
}
DEFAULT_GAME_PATH = r"C:\Program Files (x86)\Steam\steamapps\common\Kingdom.py"


def read_jsonl(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8-sig").splitlines()
        if line.strip()
    ]


def build(root: Path, patch_root: Path, game_path: str) -> dict:
    manifest = {
        Path(item["backup"]).parts[1]: item
        for item in json.loads((root / "source_manifest.json").read_text(encoding="utf-8"))
        if Path(item["backup"]).name == "ko.po"
    }

    master_rows = read_jsonl(root / "master.jsonl")
    master_by_id = {row["id"]: row for row in master_rows}
    assert len(master_by_id) == len(master_rows) == 7929

    by_scope_index = {(row["scope"], row["entry_index"]): row for row in master_rows}
    assert len(by_scope_index) == 7929

    revisions: dict[str, str] = {}
    for rev_file in sorted((root / "results").glob("*.reviewed.jsonl")):
        for row in read_jsonl(rev_file):
            rid = row["id"]
            assert rid not in revisions, f"Duplicate revision ID: {rid}"
            revisions[rid] = row["ko_revised"]
    assert set(revisions) == set(master_by_id), "Revision ID set mismatch"

    apply_root = patch_root / "Kingdom.py"
    backup_root = patch_root / "backup_original" / "Kingdom.py"
    stats: dict[str, dict] = {}

    for scope, rel_path in TARGET_REL.items():
        orig_path = root / "originals" / scope / "ko.po"
        orig_bytes = orig_path.read_bytes()
        assert hashlib.sha256(orig_bytes).hexdigest() == manifest[scope]["sha256"]

        raw_text = orig_bytes.decode("utf-8")
        assert "\r" not in raw_text, f"Unexpected CR in {orig_path}"
        blocks = raw_text.split("\n\n")

        po_orig = polib.pofile(str(orig_path), encoding="utf-8")
        assert len(po_orig) == len(blocks) - 1, f"{scope}: block count mismatch"

        changed_in_scope = 0
        out_blocks = [blocks[0]]

        for idx, entry in enumerate(po_orig):
            assert not entry.obsolete
            m = by_scope_index[(scope, idx)]
            assert (entry.msgctxt or None) == m["msgctxt"]
            assert entry.msgid == m["en"]
            assert (entry.msgid_plural or None) == m["en_plural"]

            if entry.msgid_plural:
                orig_ko = entry.msgstr_plural[0]
                prefix = "msgstr[0] "
            else:
                orig_ko = entry.msgstr
                prefix = "msgstr "
            assert orig_ko == m["ko_original"]

            revised_ko = revisions[m["id"]]
            block_lines = blocks[idx + 1].splitlines()
            assert len(block_lines) >= 2 and block_lines[-1].startswith(prefix), (
                f"Unexpected PO block layout in {scope}[{idx}]: {block_lines}"
            )

            if revised_ko != orig_ko:
                changed_in_scope += 1
                block_lines[-1] = f'{prefix}"{polib.escape(revised_ko)}"'

            out_blocks.append("\n".join(block_lines))

        patched_text = "\n\n".join(out_blocks)
        if raw_text.endswith("\n") and not patched_text.endswith("\n"):
            patched_text += "\n"

        out_file = apply_root / rel_path
        out_file.parent.mkdir(parents=True, exist_ok=True)
        out_file.write_bytes(patched_text.encode("utf-8"))

        bak_file = backup_root / rel_path
        bak_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(orig_path, bak_file)

        # Roundtrip parse & validate patched .po output.
        po_patched = polib.pofile(str(out_file), encoding="utf-8")
        assert len(po_patched) == len(po_orig)
        assert po_patched.metadata == po_orig.metadata

        po_revisions = []
        actual_diffs = 0
        for idx, entry in enumerate(po_patched):
            m = by_scope_index[(scope, idx)]
            assert (entry.msgctxt or None) == m["msgctxt"]
            assert entry.msgid == m["en"]
            assert (entry.msgid_plural or None) == m["en_plural"]
            actual_ko = entry.msgstr_plural[0] if entry.msgid_plural else entry.msgstr
            assert actual_ko == revisions[m["id"]], f"Roundtrip mismatch at {m['id']}"
            if actual_ko != m["ko_original"]:
                actual_diffs += 1
            po_revisions.append({"id": m["id"], "ko_revised": actual_ko, "note": ""})

        scope_master = {r["id"]: r for r in master_rows if r["scope"] == scope}
        val = validate_revisions.validate(scope_master, po_revisions, set(scope_master))
        assert not val["missing_ids"] and not val["errors"] and not val["warnings"], val
        assert val["changed"] == actual_diffs == changed_in_scope

        stats[scope] = {
            "entries": len(po_patched),
            "changed": changed_in_scope,
            "bytes": out_file.stat().st_size,
            "sha256": hashlib.sha256(out_file.read_bytes()).hexdigest(),
            "orig_sha256": manifest[scope]["sha256"],
        }

    zip_path = patch_root / "Kingdom.py_ko_patch.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for rel_path in TARGET_REL.values():
            zf.write(apply_root / rel_path, arcname=rel_path.as_posix())

    with zipfile.ZipFile(zip_path, "r") as zf:
        assert zf.testzip() is None
        names = sorted(zf.namelist())
        expected_names = sorted(p.as_posix() for p in TARGET_REL.values())
        assert names == expected_names, names
        for scope, rel_path in TARGET_REL.items():
            assert hashlib.sha256(zf.read(rel_path.as_posix())).hexdigest() == stats[scope]["sha256"]

    readme_text = f"""# Kingdom.py 한국어 교정 패치 안내

이 폴더는 `results/*.reviewed.jsonl`의 최종 교정 결과(총 7,929건 중 1,523건 수정)를 게임 원본 `.po` 형식 그대로 반영한 덮어쓰기 패치입니다.

## 포함된 구성
- `Kingdom.py/Kingdom_Data/...` : 교정본이 적용된 패치 폴더 (`Localization/ko.po`, `Mods/story/lang/ko.po`)
- `Kingdom.py_ko_patch.zip` : 위 `Kingdom_Data/...` 폴더 구조 그대로 압축한 배포/보관용 ZIP 파일
- `backup_original/Kingdom.py/Kingdom_Data/...` : 2026-11-15 기준 원본 `ko.po` 복구용 백업

## 적용 방법 (가장 쉬운 방법 1: 탐색기 덮어쓰기)
1. `patch/Kingdom.py/` 안에 있는 **`Kingdom_Data`** 폴더를 복사합니다.
2. 게임 설치 폴더 `{game_path}` 안에 붙여넣고 **대상 폴더의 파일 덮어쓰기**를 선택합니다.
   *(또는 `Kingdom.py_ko_patch.zip` 압축을 `{game_path}` 폴더에 바로 풀어도 동일합니다.)*
3. *참고*: `C:\\Program Files (x86)` 경로 특성상 Windows 관리자 권한 확인 창이 뜰 수 있으며, 덮어쓰기 전 원본은 `backup_original/`에 이미 보관되어 있습니다.

## 적용 방법 (방법 2: PowerShell 명령어 한 번에 복사)
```powershell
Copy-Item -LiteralPath "{apply_root / 'Kingdom_Data'}" -Destination "{game_path}" -Recurse -Force
```

## 원본으로 복구하는 방법
- `patch/backup_original/Kingdom.py/` 안의 **`Kingdom_Data`** 폴더를 게임 설치 폴더에 덮어쓰거나,
- Steam 라이브러리에서 `Kingdom.py` 우클릭 → **속성 → 설치된 파일 → 게임 파일 무결성 검사**를 실행하면 원본으로 복구됩니다.
"""
    (patch_root / "README.md").write_text(readme_text, encoding="utf-8")
    return {"stats": stats, "zip_bytes": zip_path.stat().st_size}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root folder")
    parser.add_argument("--output", type=Path, help="Patch output directory (default: <root>/patch)")
    parser.add_argument("--game-path", default=DEFAULT_GAME_PATH, help="Game directory path for README examples")
    args = parser.parse_args()

    patch_root = args.output or (args.root / "patch")
    summary = build(args.root, patch_root, args.game_path)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
