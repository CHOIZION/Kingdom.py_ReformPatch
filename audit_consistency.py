"""Audit cross-batch Korean localization consistency across all reviewed batches."""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RESIDUAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("안식시키 (must be 안식을 주다/안식에 들게 하다)", re.compile(r"안식시키")),
    ("흥청망청 (must be 폭식/폭식 중)", re.compile(r"흥청망청")),
    ("제목 줄 / 창 상단 (must be 제목 표시줄)", re.compile(r"제목\s*줄|코드\s*창\s*상단")),
    ("머리글 .po (must be 헤더)", re.compile(r"머리글")),
    ("rules/에 규칙 이름을 딴 (must be 슬롯 이름을 딴)", re.compile(r"rules/에\s*규칙\s*이름을\s*딴")),
    ("경비 초소 (must be 초소)", re.compile(r"경비\s*초소")),
    ("화재 감독관/감시꾼 (must be 화재 감시원)", re.compile(r"화재\s*(?:감독관|감시꾼)")),
    ("도시 경비대 (must be 마을 경비대)", re.compile(r"도시\s*경비대")),
    ("난방 장작/통나무 혼용", re.compile(r"장작\s*(?:\{\d+\}|\d+)|불\s*땔\s*장작|장작을\s*(?:두\s*배|더\s*때|다\s*쓰|때요)|통나무\s*반\s*개")),
    ("메뉴 ASCII 화살표 (->)", re.compile(r"메뉴\s*->|->\s*(?:테마|모드)")),
    ("URL <섬> 태그 (<island> 통일)", re.compile(r"<섬>")),
    ("비계수 자원 '개' 단위사", re.compile(r"(?:곡물|목재|석재|철)\s*(?:\{\d+\}|%[^%]+%)\s*개")),
    ("동적 토큰 조사 충돌", re.compile(r"items\[\{\d+\}\][은는이가]|%key:[A-Za-z_]+%[은는이가을를]")),
]


def load_entries(root: Path) -> list[dict]:
    entries: list[dict] = []
    for batch_file in sorted((root / "gemini_batches").glob("*.jsonl")):
        stem = batch_file.stem
        rev_file = root / "results" / f"{stem}.reviewed.jsonl"
        if not rev_file.exists():
            print(f"[WARN] missing reviewed file: {rev_file.name}")
            continue
        src_map = {
            obj["id"]: obj
            for line in batch_file.read_text(encoding="utf-8").splitlines()
            if line.strip()
            for obj in (json.loads(line),)
        }
        for line in rev_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rev = json.loads(line)
            src = src_map[rev["id"]]
            entries.append(
                {
                    "batch": stem,
                    "id": rev["id"],
                    "en": src.get("en", ""),
                    "ru": src.get("ru", ""),
                    "ko_orig": src.get("ko_original", ""),
                    "ko": rev["ko_revised"],
                    "note": rev.get("note", ""),
                    "ctx": src.get("context", ""),
                }
            )
    return entries


def collect_audit_sections(entries: list[dict]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = defaultdict(list)

    def add(sec: str, e: dict, extra: str = "") -> None:
        line = f"[{e['batch']}] {e['id']} | en={e['en']!r} | ru={e['ru']!r} | ko={e['ko']!r}"
        if extra:
            line += f" | {extra}"
        sections[sec].append(line)

    for e in entries:
        en, ru, ko = e["en"], e["ru"], e["ko"]
        enl = en.lower()
        ru_str = ru if isinstance(ru, str) else json.dumps(ru, ensure_ascii=False)
        ctx_str = json.dumps(e["ctx"], ensure_ascii=False)

        if ("lay" in enl and "rest" in enl) or "안식" in ko:
            add("01_lay_to_rest", e)
        if "binge" in enl or "폭식" in ko or "흥청망청" in ko:
            add("02_binge", e)
        if "header" in enl or "제목 표시줄" in ko or "제목 줄" in ko or "머리글" in ko or "헤더" in ko:
            add("03_header", e)
        if "named after" in enl or "규칙 이름" in ko or "슬롯 이름" in ko:
            add("04_slot_naming", e)
        if (
            re.search(r"\bguard\s*(house|post)\b", enl)
            or "warden" in enl
            or "fire watch" in enl
            or "화재 감" in ko
            or "초소" in ko
        ):
            add("05_guard_and_fire", e)
        if re.search(r"\blogs?\b|\bfirewood\b", enl) or "장작" in ko or "통나무" in ko:
            add("06a_log_firewood", e)
        if (
            "wood" in enl
            and any(k in enl for k in ("heat", "burn", "stove", "warm", "winter", "storm"))
        ) or ("дров" in ru_str.lower()):
            add("06b_wood_heating", e)
        if (
            re.search(r"\b(fair|blonde|blond|skin|hair)\b", enl)
            or "appearance" in ctx_str.lower()
            or enl in ("fair", "light", "medium", "dark")
        ):
            add("07_appearance", e)
        if "->" in en or "->" in ko or "→" in ko or "메뉴" in ko:
            add("08_menu_paths", e)
        if re.search(r"\bchild(ren)?\b", enl):
            add("09_children", e)
        if any(k in enl for k in ("for years", "several years", "many years")) or any(
            k in ko for k in ("여러 해", "오랫동안", "수년간")
        ):
            add("10_for_years", e)
        if re.search(r"<[^>\s]{1,30}>", en) or re.search(r"<[^>\s]{1,30}>", ko):
            add("11_placeholders", e)
        if "creature" in enl:
            add("12_creature", e)
        if re.search(r"(요|다|죠|세요|네요|군요|해요|돼요|줘요|나요):\s+[가-힣‘“'\"]", ko):
            add("13a_colon_before_clause", e)
        if ko.count("‘") != ko.count("’") or ko.count("“") != ko.count("”"):
            add("13b_unmatched_curly_quotes", e)
        for ln in ko.split("\n"):
            if "  " in ln.lstrip():
                add("13c_midline_double_space", e)
                break
        if re.search(r"(합|습|입|됩|줍)니다", ko):
            add("13d_formal_nida", e)

    return sections


def find_residuals(entries: list[dict]) -> list[tuple[str, str, str, str]]:
    hits: list[tuple[str, str, str, str]] = []
    for e in entries:
        ko = e["ko"]
        for label, pattern in RESIDUAL_PATTERNS:
            if pattern.search(ko):
                hits.append((label, e["batch"], e["id"], ko))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Project root folder")
    parser.add_argument("--report", type=Path, help="Optional text report output path")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero if any residual pattern hit is detected",
    )
    args = parser.parse_args()

    entries = load_entries(args.root)
    sections = collect_audit_sections(entries)
    residuals = find_residuals(entries)

    print(f"Total audited entries: {len(entries)}")
    print("Audit bucket counts:")
    for sec in sorted(sections):
        print(f"  {sec}: {len(sections[sec])}")
    print(f"Residual defect hits: {len(residuals)}")
    for hit in residuals:
        print(f"  [HIT] {hit[0]} | {hit[1]} {hit[2]} | {hit[3]!r}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        lines = [f"TOTAL ENTRIES AUDITED: {len(entries)}", f"RESIDUAL HITS: {len(residuals)}", ""]
        for hit in residuals:
            lines.append(f"[HIT] {hit[0]} | {hit[1]} {hit[2]} | {hit[3]!r}")
        lines.append("")
        for sec in sorted(sections):
            lines.append(f"=== {sec} ({len(sections[sec])}) ===")
            lines.extend(sections[sec])
            lines.append("")
        args.report.write_text("\n".join(lines), encoding="utf-8")
        print(f"Wrote detailed report: {args.report}")

    return 1 if (args.strict and residuals) else 0


if __name__ == "__main__":
    raise SystemExit(main())
