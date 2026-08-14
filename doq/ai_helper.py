"""
OpenAI API 호출 함수 모음
- Tab 1(AI 마음 케어)과 Tab 3(AI 공백기 변환기)에서 사용해요.
- API 키는 반드시 st.secrets["OPENAI_API_KEY"]로만 불러오고, 코드에 직접 적지 않아요!
"""

import streamlit as st
from openai import OpenAI

# 위기 신호로 볼 수 있는 키워드예요.
# AI의 판단에만 맡기지 않고, 파이썬 코드에서 먼저 한 번 걸러내는 안전장치예요.
CRISIS_KEYWORDS = [
    "죽고싶", "죽어버리", "사라지고싶", "자살", "극단적선택", "자해", "살기싫",
]


def check_crisis_signal(text: str) -> bool:
    """사용자 입력에 위기 신호 키워드가 있는지 확인해요."""
    cleaned = text.replace(" ", "")
    return any(keyword in cleaned for keyword in CRISIS_KEYWORDS)


@st.cache_resource
def _get_client():
    """secrets.toml에 키가 없거나 잘못돼도 앱이 죽지 않도록 안전하게 클라이언트를 생성해요."""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        return None
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


EMPATHY_SYSTEM_PROMPT = """당신은 취업 준비로 지친 청년들의 마음을 다정하게 보듬어주는 AI 메이트 '다시'입니다.

원칙:
1. 절대 평가하거나 조언을 강요하지 않아요. 먼저 충분히 공감하는 것이 최우선이에요.
2. 사용자의 감정을 판단하지 말고, 힘든 마음 자체를 자연스러운 것으로 받아들여주세요.
3. 답변 마지막에 아주 작은 5분짜리 행동 하나를 부담 없이 제안해주세요.
   (예: 산책 10분, 좋아하는 노래 듣기, 관심있는 채용공고 1개 읽어보기, 물 한 잔 마시기)
4. 존댓말을 쓰되 딱딱하지 않고 다정한 톤을 유지하세요.
5. 답변은 3~5문장 이내로 짧게 작성하세요.
6. 절대 의학적 진단을 내리거나 "OO인 것 같아요" 같은 단정적인 표현을 쓰지 마세요.
"""

GAP_YEAR_SYSTEM_PROMPT = """당신은 청년들이 공백기 동안 했던 소소한 일상 활동을,
자기소개서나 이력서에 쓸 수 있는 직무 역량 문장으로 재해석해주는 AI 커리어 코치입니다.

원칙:
1. 사용자가 입력하지 않은 경험을 지어내거나 과장하지 않아요. 실제 활동에서 드러나는
   강점(꾸준함, 자기주도적 학습, 정보 습득력, 관찰력 등)만 진솔하게 짚어내세요.
2. '과장'이 아니라 '재해석'에 집중하세요. 채용 담당자가 읽었을 때 신뢰할 수 있는 톤을 유지하세요.
3. 사용자가 관심 있다고 밝힌 분야가 있다면, 그 분야와 자연스럽게 연결지어 주세요.
4. 아래 형식을 정확히 지켜서 답변하세요.

**핵심 키워드**: (쉼표로 구분한 키워드 3개)

**자소서 활용 예문**
(2~3문장짜리 예문 1개)
"""


def get_empathy_response(user_text: str) -> str:
    """Tab 1: 사용자의 오늘 마음에 공감하고, 5분짜리 작은 행동을 제안해줘요."""
    client = _get_client()
    if client is None:
        return (
            "⚠️ 아직 OpenAI API 키가 연결되지 않았어요. "
            ".streamlit/secrets.toml 파일에 OPENAI_API_KEY를 추가하면 AI 답변을 받을 수 있어요."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # 필요하면 OpenAI 최신 모델 목록에서 더 저렴하거나 최신인 모델로 바꿔도 돼요.
            messages=[
                {"role": "system", "content": EMPATHY_SYSTEM_PROMPT},
                {"role": "user", "content": user_text},
            ],
            max_tokens=300,
            temperature=0.8,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ 잠시 연결에 문제가 생겼어요. 잠시 후 다시 시도해주세요. ({e})"


def convert_gap_activity(user_text: str, interest_field: str = "") -> str:
    """Tab 3: 공백기 활동을 자소서용 직무 역량 문장으로 변환해줘요."""
    client = _get_client()
    if client is None:
        return (
            "⚠️ 아직 OpenAI API 키가 연결되지 않았어요. "
            ".streamlit/secrets.toml 파일에 OPENAI_API_KEY를 추가하면 AI 변환 결과를 받을 수 있어요."
        )

    user_message = f"활동 내용: {user_text}"
    if interest_field:
        user_message += f"\n관심 분야: {interest_field}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": GAP_YEAR_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ 잠시 연결에 문제가 생겼어요. 잠시 후 다시 시도해주세요. ({e})"
