# 📊 Yahoo Finance 뉴스 슬랙 브리핑 봇

이 스크립트는 Yahoo Finance에서 **미국 매크로 경제** 뉴스 3개와 **AI/테크 기업** 뉴스 3개(총 6개)의 최신 기사를 크롤링하여 지정된 슬랙(Slack) 채널로 알림을 전송하는 파이썬 스크립트입니다.

---

## 🛠️ 준비 사항

### 1. 활성 작업 디렉토리 설정 권장
이 프로젝트를 사용하시기 전에, 에디터나 IDE에서 현재 폴더(`C:\Users\dah22\.gemini\antigravity\scratch\yahoo_finance_slack_bot`)를 **활성 워크스페이스(Active Workspace)**로 설정하시는 것을 강력히 권장합니다.

### 2. 패키지 설치
스크립트 실행에 필요한 라이브러리를 설치합니다.
```bash
pip install -r requirements.txt
```

### 3. 슬랙 웹훅 URL 환경변수 설정
스크립트는 환경변수 `SLACK_WEBHOOK_URL`에 설정된 주소로 알림을 보냅니다. 실행하기 전에 환경변수를 등록해야 합니다.

#### 💻 Windows (Command Prompt - cmd)
```cmd
set SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXXXX/YYYYY/ZZZZZ"
```

#### 🐚 Windows (PowerShell)
```powershell
$env:SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXXXX/YYYYY/ZZZZZ"
```

#### 🐧 Linux / macOS (Bash)
```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXXXX/YYYYY/ZZZZZ"
```

---

## 🚀 실행 방법

환경변수가 올바르게 설정되었다면 아래 명령어로 스크립트를 실행할 수 있습니다.

```bash
python crawler.py
```

### ⚙️ 동작 흐름
1. Yahoo Finance의 `Economic News` 카테고리와 `Tech News` 카테고리에서 각각 최신 뉴스 3개씩(총 6개)을 파싱합니다.
2. 기사 목록 중 시황 단순 알림(예: "U.S. markets closed" 등)과 같은 불필요한 기사는 필터링합니다.
3. 상대 경로로 반환된 링크를 절대 경로로 가공합니다.
4. `SLACK_WEBHOOK_URL` 환경변수를 통해 슬랙 채널에 카드 뉴스 형태(Block Kit 구성)로 깔끔하게 포맷팅된 메시지를 전송합니다.
