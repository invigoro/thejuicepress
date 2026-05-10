#!/usr/bin/env python3
"""Import quizzes from PostgreSQL pg_dump into _data/quizzes/*.json + quizzes/*.md."""

from __future__ import annotations

import html
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "juice-press-backup-7-3-22.sql"
DATA_DIR = ROOT / "_data" / "quizzes"
OUT_MD_DIR = ROOT / "quizzes"


def title_to_slug(title: str, fallback_id: str) -> str:
    t = (title or "").strip().lower()
    t = t.replace("\u2019", "'").replace("\u2018", "'")
    t = t.replace("\u201c", '"').replace("\u201d", '"')
    t = t.replace("'", "").replace('"', "")
    t = re.sub(r"[^a-z0-9]+", "-", t)
    t = re.sub(r"-+", "-", t).strip("-")
    return t or f"quiz-{fallback_id}"


def find_copy_block(lines: list[str], table_prefix: str) -> tuple[int, int]:
    needle = f'COPY public."{table_prefix}"'
    start = None
    for i, line in enumerate(lines):
        if needle in line:
            start = i
            break
    if start is None:
        raise SystemExit(f'Could not find COPY for "{table_prefix}"')
    end = None
    for j in range(start + 1, len(lines)):
        if lines[j].strip() == r"\.":  # noqa: SIM116
            end = j
            break
    if end is None:
        raise SystemExit(f'Could not find end of COPY for "{table_prefix}"')
    return start, end


def split_row(line: str) -> list[str]:
    return line.rstrip("\n\r").split("\t")


def parse_iso_datetime(s: str) -> datetime | None:
    s = (s or "").strip()
    if not s or s == r"\N":
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def intro_html_from_db(raw: str) -> str:
    if not raw or raw.strip() == r"\N":
        return ""
    raw = raw.strip()
    if BeautifulSoup is None:
        return f"<p>{html.escape(raw)}</p>"
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup.find_all(["script", "style"]):
        tag.decompose()
    return str(soup) or ""


def result_body_html(raw: str) -> str:
    if not raw or raw.strip() == r"\N":
        return ""
    text = raw.replace("\r\n", "\n").replace("\r", "\n").strip()
    paras = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not paras:
        return ""
    return "".join(f"<p>{html.escape(p)}</p>" for p in paras)


def main() -> None:
    if not SQL_PATH.is_file():
        print(f"Missing SQL dump: {SQL_PATH}", file=sys.stderr)
        sys.exit(1)

    lines = SQL_PATH.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)

    def load_table(name: str) -> list[list[str]]:
        start, end = find_copy_block(lines, name)
        rows = []
        for raw in lines[start + 1 : end]:
            if not raw.strip():
                continue
            rows.append(split_row(raw))
        return rows

    quizzes_rows = load_table("Quizzes")
    questions_rows = load_table("QuizQuestions")
    answers_rows = load_table("QuizQuestionAnswers")
    results_rows = load_table("QuizResults")
    weights_rows = load_table("AnswerResultWeights")

    # weights: answer_id -> { result_id_str: weight }
    weights_by_answer: dict[str, dict[str, int]] = {}
    for cols in weights_rows:
        if len(cols) != 3:
            continue
        aid, rid, w = cols[0], cols[1], cols[2]
        weights_by_answer.setdefault(aid, {})[rid] = int(w)

    questions_by_quiz: dict[str, list[dict]] = {}
    for cols in questions_rows:
        if len(cols) != 4:
            continue
        qid, order, quiz_id, prompt = cols
        questions_by_quiz.setdefault(quiz_id, []).append(
            {"id": qid, "order": int(order), "prompt": prompt}
        )

    for qlist in questions_by_quiz.values():
        qlist.sort(key=lambda x: x["order"])

    answers_by_question: dict[str, list[dict]] = {}
    for cols in answers_rows:
        if len(cols) != 3:
            continue
        aid, qid, label = cols
        wmap = weights_by_answer.get(aid, {})
        answers_by_question.setdefault(qid, []).append(
            {"id": aid, "label": label, "weights": wmap}
        )

    results_by_quiz: dict[str, list[dict]] = {}
    for cols in results_rows:
        if len(cols) != 4:
            continue
        rid, quiz_id, title, content = cols
        slug = title_to_slug(title, rid)
        results_by_quiz.setdefault(quiz_id, []).append(
            {
                "id": int(rid),
                "slug": slug,
                "title": title,
                "contentHtml": result_body_html(content),
            }
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUT_MD_DIR.mkdir(parents=True, exist_ok=True)

    for old_json in DATA_DIR.glob("*.json"):
        old_json.unlink()

    written = 0
    for cols in quizzes_rows:
        if len(cols) < 14:
            continue
        (
            quiz_id,
            url_short,
            title,
            draft_title,
            content,
            _draft_content,
            _created,
            _edited,
            published_on,
            _overwritten,
            published,
            _views,
            _cover,
            random_order,
        ) = (
            cols[0],
            cols[1],
            cols[2],
            cols[3],
            cols[4],
            cols[5],
            cols[6],
            cols[7],
            cols[8],
            cols[9],
            cols[10],
            cols[11],
            cols[12],
            cols[13],
        )

        pub = published.strip().lower() in ("t", "true", "1")
        if not pub:
            continue

        display_title = (title or "").strip() or (draft_title or "").strip()
        if not display_title:
            display_title = f"Quiz {quiz_id}"

        slug = title_to_slug(display_title, quiz_id)
        date_str = None
        dt = parse_iso_datetime(published_on)
        if dt:
            date_str = dt.strftime("%Y-%m-%d")

        q_list = questions_by_quiz.get(quiz_id, [])
        questions_out = []
        for q in q_list:
            ans_list = answers_by_question.get(q["id"], [])
            questions_out.append(
                {
                    "id": q["id"],
                    "order": q["order"],
                    "prompt": q["prompt"],
                    "answers": [
                        {
                            "id": a["id"],
                            "label": a["label"],
                            "weights": a["weights"],
                        }
                        for a in ans_list
                    ],
                }
            )

        results_out = results_by_quiz.get(quiz_id, [])
        used_result_slugs: set[str] = set()
        for r in results_out:
            base = r["slug"]
            s = base
            if s in used_result_slugs:
                s = f"{base}-{r['id']}"
            used_result_slugs.add(s)
            r["slug"] = s

        payload = {
            "quizId": int(quiz_id),
            "urlShortCode": url_short,
            "title": display_title,
            "introHtml": intro_html_from_db(content),
            "randomQuestionOrder": random_order.strip().lower() in ("t", "true", "1"),
            "questions": questions_out,
            "results": results_out,
        }

        json_path = DATA_DIR / f"{slug}.json"
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # layout / quiz / header_exclude / permalink come from _config.yml defaults for path "quizzes/"
        fm = ["---", f'title: "{_yaml_escape(display_title)}"', f"quiz_data_key: {slug}"]
        if date_str:
            fm.append(f"date: {date_str}")
        fm.extend(["---", ""])

        md_path = OUT_MD_DIR / f"{slug}.md"
        md_path.write_text("\n".join(fm), encoding="utf-8")
        written += 1

    print(f"Wrote {written} quizzes to {OUT_MD_DIR.relative_to(ROOT)} and _data/quizzes/")


def _yaml_escape(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


if __name__ == "__main__":
    main()
