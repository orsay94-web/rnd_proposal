# 상담 기초자료 볼트: Claude + Obsidian + 로컬 폴더 + Git

연구자(교수·연구원)와 지원기관의 기초자료·상담 이력을 모아 두고, 상담 전에 Claude로 바로 요약해 보는 용도입니다.

## 1. 설치
1. Obsidian 설치 → **Open folder as vault** → 이 `second-brain` 폴더 선택.
2. Claude Code 설치: `npm install -g @anthropic-ai/claude-code`
3. Git 설치 (Windows는 Git for Windows).

## 2. Git 동기화
```bash
cd second-brain
git init && git add . && git commit -m "init vault"
git remote add origin <비공개 저장소 URL>
git push -u origin main
```
- Obsidian 커뮤니티 플러그인 **Obsidian Git** 설치 → 자동 커밋/푸시 간격(예: 10분) 설정.
- 개인 노트는 반드시 **비공개(private)** 저장소에 올리세요.

## 3. Claude로 사용하기
```bash
cd second-brain
claude
```
Claude는 `CLAUDE.md`의 규칙을 읽고 동작합니다. 예시 요청:
- "홍길동 교수 상담 전 기초자료 요약해줘"
- "방금 상담 내용 기록해줘: 홍길동 교수, 전화, 신규 공고 자격 문의, 참여율 확인해서 회신하기로"
- "후속 조치 안 끝난 것 보여줘"
- "한국연구재단 관련 상담 목록 보여줘"

## 4. 구조
- `상담/연구자/` — 교수·연구원별 노트
- `상담/지원기관/` — 지원기관별 노트
- `상담/상담기록/` — 상담 1건당 노트
- `Templates/` — 연구자 · 지원기관 · 상담기록 템플릿
- `(예시)`로 시작하는 노트는 형식 예시이니 확인 후 삭제하세요.

## 5. 보안
- 상담 내용은 Claude 사용 시 Anthropic 서버로 전송됩니다. 학교 정보보안 지침을 먼저 확인하세요.
- Git 저장소는 반드시 Private. 민감정보(주민번호, 계좌 등)는 기록하지 마세요.
