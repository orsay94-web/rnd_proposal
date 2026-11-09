# Second Brain: Claude + Obsidian + 로컬 폴더 + Git

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
- "Inbox 정리해줘"
- "오늘 데일리 노트 만들고 어제 미완료 할 일 옮겨줘"
- "산학협력 과제 공고 노트들을 찾아 비교표를 만들어줘"

## 4. 구조
`00-Inbox` · `10-Projects` · `20-Areas` · `30-Resources` · `40-Archive` · `Daily` · `Templates`
