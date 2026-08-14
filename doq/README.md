# 🌱 다시, 시작 — 청년 리스타트 플랫폼

취업 준비로 지친 청년들이 아주 작은 행동부터 시작해서 다시 세상과 연결될 수 있도록 돕는
자기계발 웹앱이에요. Streamlit + OpenAI + 공공데이터를 결합한 팀 프로젝트입니다.

## ✨ 주요 기능

| 화면 | 설명 |
|---|---|
| 💭 리스타트 지수 체크 | 오늘의 에너지·의욕·불안도를 간단히 체크해보는 셀프 진단 |
| 💙 AI 마음 케어 | 오늘의 소소한 퀘스트 완료 + AI에게 마음 털어놓고 5분 행동 제안받기 |
| 💰 공공 지원금 한눈에 | 미취업 기간에 맞는 청년 지원 정책을 카드로 확인 |
| ✨ AI 공백기 변환기 | 쉬는 동안 했던 활동을 자소서용 직무 역량 문장으로 변환 |

## 📁 폴더 구조

```
.
├── app.py                       # 메인 앱 (페이지 구성, 사이드바, 3개 탭)
├── requirements.txt             # 필요한 패키지 목록
├── data/
│   └── policies.py              # 청년 지원 정책 샘플 데이터 + 필터 함수
├── utils/
│   └── ai_helper.py             # OpenAI 호출 함수 (AI 마음 케어 / 공백기 변환기)
├── .streamlit/
│   └── secrets.toml.example     # API 키 설정 예시 (실제 키는 복사한 뒤 secrets.toml에)
└── .gitignore
```

역할을 나눠서 작업하기 좋은 구조예요. 예를 들어 한 명은 `app.py`의 UI/레이아웃을,
한 명은 `utils/ai_helper.py`의 프롬프트를, 한 명은 `data/policies.py`의 정책 데이터를
각자 브랜치에서 작업하고 나중에 합치면 충돌이 훨씬 적어요.

## 🚀 로컬에서 실행하기

1. 이 저장소를 클론하거나 다운로드해요.
2. 패키지를 설치해요.
   ```bash
   pip install -r requirements.txt
   ```
3. OpenAI API 키를 설정해요.
   - `.streamlit/secrets.toml.example` 파일을 복사해서 `.streamlit/secrets.toml`로 이름을 바꿔요.
   - 그 안의 값을 본인의 OpenAI API 키로 바꿔요. (키 발급: https://platform.openai.com/api-keys)
   - `secrets.toml`은 `.gitignore`에 포함되어 있어서 GitHub에는 올라가지 않아요.
4. 앱을 실행해요. (반드시 프로젝트 최상위 폴더에서 실행해야 `data`, `utils` import가 정상 동작해요.)
   ```bash
   streamlit run app.py
   ```

## ☁️ Streamlit Community Cloud에 배포하기

1. 이 프로젝트를 GitHub 저장소에 push해요. (`.streamlit/secrets.toml`은 자동으로 제외돼요.)
2. https://share.streamlit.io 에 접속해서 GitHub 계정으로 로그인해요.
3. "New app" → 저장소/브랜치/`app.py` 선택 → Deploy를 눌러요.
4. 배포 후 앱 관리 화면(오른쪽 아래 ⋮ 메뉴) → **Settings → Secrets**에 아래처럼 입력해요.
   ```toml
   OPENAI_API_KEY = "sk-...여기에 실제 키..."
   ```
5. 저장하면 앱이 자동으로 재시작되면서 API 키가 반영돼요.

## 🔒 API 키 관련 주의사항

- OpenAI API 키는 **절대 코드에 직접 작성하거나 GitHub에 올리지 마세요.** 키가 유출되면
  다른 사람이 내 계정의 사용료로 API를 쓸 수 있어요.
- 반드시 `st.secrets`를 통해서만 키를 불러오도록 되어 있어요 (`utils/ai_helper.py` 참고).
- 만약 실수로 키를 커밋했다면, 바로 OpenAI 계정에서 해당 키를 폐기(revoke)하고 새로 발급하세요.

## 🔜 다음 단계로 발전시켜볼 아이디어

- **실시간 공공데이터 연동**: 지금 `data/policies.py`는 샘플 데이터예요. 한국고용정보원이
  제공하는 '온통청년 청년정책 Open API'(공공데이터포털에도 등록되어 있어요)를 연동하면
  정책을 자동으로 최신 상태로 유지할 수 있어요. 온통청년(youthcenter.go.kr) 회원가입 후
  [마이페이지 > OPEN API]에서 인증키를 신청하고, [이용안내 > OPEN API 소개] 문서에서
  정확한 요청 방식을 확인하면 돼요. (HTTPS 요청 → XML 응답 방식)
- **대화 기록 영구 저장**: 지금은 브라우저 세션이 끝나면 기록이 사라져요. Google Sheets나
  SQLite 등을 연결하면 사용자별 기록을 이어서 볼 수 있어요.
- **리스타트 지수 히스토리**: 매일 체크한 지수를 그래프로 보여주면 변화 추이를 스스로
  확인할 수 있어요.

## ⚠️ 안내

이 앱의 AI 마음 케어 기능은 전문 심리상담을 대체하지 않아요. 정말 힘든 순간에는
정신건강 위기상담전화(1577-0199) 또는 자살예방상담전화(1393)처럼 실제 전문가의 도움을
받는 게 가장 중요해요. 그래서 앱 사이드바에도 이 안내가 항상 보이도록 넣어뒀고,
위기 신호로 보이는 입력은 AI를 부르기 전에 코드 단에서 먼저 걸러서 상담 정보를
안내하도록 만들어뒀어요.
