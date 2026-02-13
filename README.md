# Python 테트리스 게임

`pygame`로 만든 간단한 테트리스 프로젝트입니다.

## 실행 방법

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python tetris.py
```

## 조작법

- `←` / `→`: 블록 이동
- `↑`: 블록 회전
- `↓`: 한 칸 빠르게 내리기
- `Space`: 즉시 낙하
- `R`: 게임 재시작
- `Esc`: 게임 종료

## 기능

- 점수/라인/레벨 표시
- 라인 제거 및 레벨 상승
- 다음 블록 미리보기
- 게임 오버 처리 및 재시작
