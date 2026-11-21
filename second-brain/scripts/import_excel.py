"""
엑셀(과제정보, 과제별 연구원정보) → Obsidian 노트 변환

사용법 (second-brain 폴더에서):
    pip install openpyxl
    python scripts/import_excel.py 과제정보.xlsx 연구원정보.xlsx

- 모든 처리는 내 PC 안에서만 이루어집니다 (외부 전송 없음).
- 이미 있는 노트는 덮어쓰지 않고, 자동 생성 구역만 갱신합니다.
- 엑셀 열 이름이 다르면 아래 COLUMNS의 후보 목록에 추가하세요.
"""
import re
import sys
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook

# 열 이름 후보 (엑셀 첫 행에서 처음 일치하는 것을 사용)
COLUMNS = {
    "과제번호": ["과제번호", "과제 번호", "과제코드", "과제ID", "관리번호"],
    "과제명": ["과제명", "과제 명", "연구과제명", "과제명(국문)"],
    "사업명": ["사업명", "세부사업명", "사업"],
    "지원기관": ["지원기관", "전문기관", "주관기관", "발주처", "지원 기관"],
    "책임자": ["연구책임자", "책임자", "과제책임자"],
    "시작일": ["시작일", "연구시작일", "협약시작일", "과제시작일"],
    "종료일": ["종료일", "연구종료일", "협약종료일", "과제종료일"],
    "연구비": ["연구비", "총연구비", "정부출연금", "당해연도연구비"],
    "상태": ["상태", "진행상태", "과제상태"],
    "성명": ["성명", "이름", "연구원명", "참여연구원"],
    "소속": ["소속", "소속기관", "기관"],
    "학과": ["학과", "부서", "소속학과"],
    "직위": ["직위", "직급", "구분"],
    "역할": ["역할", "참여구분", "참여형태"],
    "참여율": ["참여율", "참여율(%)"],
}

BASE = Path(__file__).resolve().parent.parent / "상담"
AUTO_START = "<!-- 자동생성 시작: 엑셀에서 가져온 내용, 직접 수정하지 마세요 -->"
AUTO_END = "<!-- 자동생성 끝 -->"


def safe(name):
    return re.sub(r'[\\/:*?"<>|#^\[\]]', "_", str(name)).strip()


def cell(v):
    if v is None:
        return ""
    if hasattr(v, "strftime"):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float) and v.is_integer():
        v = int(v)
    return str(v).strip()


def read_rows(path):
    ws = load_workbook(path, read_only=True, data_only=True).active
    rows = ws.iter_rows(values_only=True)
    header = [cell(h) for h in next(rows)]
    mapping = {}
    for key, candidates in COLUMNS.items():
        for c in candidates:
            if c in header:
                mapping[key] = header.index(c)
                break
    print(f"[{Path(path).name}] 인식한 열: {', '.join(mapping) or '없음'}")
    unknown = [h for h in header if h and h not in sum(COLUMNS.values(), [])]
    if unknown:
        print(f"  인식 못 한 열(무시됨): {', '.join(unknown)}")
    out = []
    for r in rows:
        if not any(r):
            continue
        out.append({k: cell(r[i]) if i < len(r) else "" for k, i in mapping.items()})
    return out


def upsert(path, header_text, auto_body):
    block = f"{AUTO_START}\n{auto_body}\n{AUTO_END}"
    if path.exists():
        text = path.read_text(encoding="utf-8")
        if AUTO_START in text:
            text = re.sub(re.escape(AUTO_START) + r".*?" + re.escape(AUTO_END),
                          lambda _: block, text, flags=re.S)
        else:
            text = text.rstrip() + "\n\n" + block + "\n"
        status = "갱신"
    else:
        text = header_text + "\n" + block + "\n\n## 상담 이력\n- \n\n## 후속 조치\n- [ ] \n\n## 메모\n"
        status = "생성"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return status


def person_key(p):
    org = p.get("학과") or p.get("소속") or ""
    return f"{p['성명']} ({org})" if org else p["성명"]


def main(task_file, people_file):
    tasks = {t["과제번호"]: t for t in read_rows(task_file) if t.get("과제번호")}
    people = [p for p in read_rows(people_file) if p.get("성명")]

    by_task = defaultdict(list)
    by_person = {}
    person_tasks = defaultdict(list)
    for p in people:
        k = person_key(p)
        by_person.setdefault(k, p)
        by_task[p.get("과제번호", "")].append((k, p))
        person_tasks[k].append(p)

    agencies = defaultdict(list)
    stats = defaultdict(int)

    for no, t in tasks.items():
        name = safe(f"{no} {t.get('과제명', '')}")[:120]
        agency = t.get("지원기관", "")
        if agency:
            agencies[agency].append((name, t))
        rows = "\n".join(
            f"| [[{k}]] | {p.get('역할', '')} | {p.get('참여율', '')} |" for k, p in by_task.get(no, [])
        ) or "| (연구원 정보 없음) | | |"
        body = (
            "## 과제 정보\n"
            f"- 과제번호: {no}\n- 사업명: {t.get('사업명', '')}\n"
            f"- 지원기관: {f'[[{safe(agency)}]]' if agency else ''}\n"
            f"- 연구책임자: {t.get('책임자', '')}\n"
            f"- 기간: {t.get('시작일', '')} ~ {t.get('종료일', '')}\n"
            f"- 연구비: {t.get('연구비', '')}\n- 상태: {t.get('상태', '')}\n\n"
            "## 참여 연구원\n| 연구원 | 역할 | 참여율 |\n|---|---|---|\n" + rows
        )
        head = f"---\ntype: 과제\n과제번호: \"{no}\"\ntags: [과제]\n---\n# {t.get('과제명', no)}\n"
        stats["과제 " + upsert(BASE / "과제" / f"{name}.md", head, body)] += 1

    for k, p in by_person.items():
        rows = []
        for q in person_tasks[k]:
            t = tasks.get(q.get("과제번호", ""), {})
            tname = safe(f"{q.get('과제번호', '')} {t.get('과제명', '')}")[:120]
            ag = t.get("지원기관", "")
            rows.append(
                f"| {t.get('시작일', '')[:4]} | [[{tname}]] | {f'[[{safe(ag)}]]' if ag else ''} "
                f"| {q.get('역할', '')} | {q.get('참여율', '')} | {t.get('상태', '')} |"
            )
        body = (
            "## 기초정보\n"
            f"- 소속: {p.get('소속', '')}\n- 학과: {p.get('학과', '')}\n- 직위: {p.get('직위', '')}\n\n"
            "## 과제 이력\n| 연도 | 과제 | 지원기관 | 역할 | 참여율 | 상태 |\n|---|---|---|---|---|---|\n"
            + "\n".join(rows)
        )
        head = f"---\ntype: 연구자\n구분: {p.get('직위', '')}\n소속: {p.get('소속', '')}\ntags: [상담대상, 연구자]\n---\n# {k}\n"
        stats["연구자 " + upsert(BASE / "연구자" / f"{safe(k)}.md", head, body)] += 1

    for ag, lst in agencies.items():
        rows = "\n".join(
            f"| [[{n}]] | {t.get('사업명', '')} | {t.get('책임자', '')} | {t.get('상태', '')} |" for n, t in lst
        )
        body = "## 우리 기관 과제\n| 과제 | 사업명 | 책임자 | 상태 |\n|---|---|---|---|\n" + rows
        head = f"---\ntype: 지원기관\ntags: [상담대상, 지원기관]\n---\n# {ag}\n"
        stats["지원기관 " + upsert(BASE / "지원기관" / f"{safe(ag)}.md", head, body)] += 1

    print("\n완료:", ", ".join(f"{k} {v}개" for k, v in sorted(stats.items())))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2])
