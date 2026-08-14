import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
from openai import OpenAI
import random
import json

# -------------------------------------------------------------------
# 1. 페이지 및 디자인 기본 설정
# -------------------------------------------------------------------
st.set_page_config(
    page_title="StepBy - 청년 마음건강 & 자아성장",
    page_icon="🌱",
    layout="wide"
)

# 커스텀 CSS 스타일링
st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 3rem; }
.policy-card {
    background-color: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 1.2rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.policy-title { color: #1E293B; font-size: 1.15rem; font-weight: 700; margin-bottom: 0.4rem; }
.policy-tag {
    display: inline-block; background-color: #E0F2FE; color: #0369A1;
    font-size: 0.8rem; padding: 0.2rem 0.6rem; border-radius: 20px; font-weight: 600; margin-bottom: 0.6rem;
}
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
defaults = {
    "user_region": "서울특별시 종로구",
    "user_age": 26,
    "unemployed_months": 8,
    "mood_score": 3,
    "todays_quest": None,
    "quest_completed": False,
    "transformed_result": None
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# -------------------------------------------------------------------
# 2. 백엔드 데이터 및 AI 연동 함수
# -------------------------------------------------------------------
MOCK_POLICIES = [
    {
        "polyBizSrn": "청년도전지원사업",
        "polyItcnCn": "구직 단기·장기 단념 청년을 대상으로 1:1 맞춤형 상담 및 일상 회복 프로그램을 제공하고 참여 수당(최대 300만원)을 지원합니다.",
        "ageInfo": "만 18세 ~ 34세", "rqutPrdCn": "상시 모집", "rqutUrla": "https://www.work.go.kr", "category": "일자리 / 역량강화"
    },
    {
        "polyBizSrn": "국민취업지원제도 (1유형)",
        "polyItcnCn": "취업을 희망하는 청년에게 취업지원서비스와 함께 월 50만원씩 6개월간 구직촉진수당을 지급합니다.",
        "ageInfo": "만 15세 ~ 69세", "rqutPrdCn": "연중 상시", "rqutUrla": "https://www.kua.go.kr", "category": "소득지원 / 일자리"
    },
    {
        "polyBizSrn": "청년월세 특별지원",
        "polyItcnCn": "부모와 별도 거주하는 무주택 청년에게 연 최대 240만원(월 최대 20만원)의 월세를 실비 지원합니다.",
        "ageInfo": "만 19세 ~ 34세", "rqutPrdCn": "지자체별 공고 확인", "rqutUrla": "https://www.bokjiro.go.kr", "category": "주거 / 생활안정"
    },
    {
        "polyBizSrn": "청년 마음건강 바우처 지원사업",
        "polyItcnCn": "청년의 심리 정서 지원 및 번아웃 예방을 위해 전문 심리상담 서비스를 바우처 형태로 지원합니다.",
        "ageInfo": "만 19세 ~ 34세", "rqutPrdCn": "주민센터 문의", "rqutUrla": "https://www.bokjiro.go.kr", "category": "마음건강 / 복지"
    }
]

def get_openai_client():
    api_key = st.secrets.get("OPENAI_API_KEY", None)
    if api_key and api_key != "sk-proj-your-openai-api-key-here":
        return OpenAI(api_key=api_key)
    return None

def check_crisis_keywords(text):
    danger_words = ["죽고 싶", "자살", "끝내고 싶", "세상에서 사라", "살기 싫"]
    return any(word in text for word in danger_words)

def generate_micro_quest(mood_score, mood_text):
    if check_crisis_keywords(mood_text):
        return {
            "is_crisis": True,
            "message": "작성하신 내용에 마음이 많이 아프네요. 혼자 감당하려 하지 마시고, 24시간 언제든 전문가와 이야기해보세요.",
            "quest": "지금 상담전화 109번으로 연결하여 이야기 나누기"
        }
    
    client = get_openai_client()
    if not client:
        quests = [
            "창문 열고 따뜻한 햇살 아래서 깊게 숨 3번 쉬기",
            "따뜻한 물 한 잔 천천히 마시며 어깨 풀기",
            "좋아하는 노래 1곡 듣고 가사 한 줄 적어보기",
            "가벼운 동네 산책 10분 다녀오기"
        ]
        return {
            "is_crisis": False,
            "message": "많이 지친 상태시군요. 오늘 하루는 나에게 아주 작고 친절한 미션을 선물해보세요.",
            "quest": random.choice(quests)
        }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": "당신은 청년 코치입니다. 행동 활성화 기법을 적용해 5분 안에 할 수 있는 쉬운 미션 1개를 제안하세요. JSON 형식: {\"message\": \"공감 문장\", \"quest\": \"미션 내용\"}"},
                {"role": "user", "content": f"마음 점수: {mood_score}/5점, 메모: {mood_text}"}
            ],
            temperature=0.7
        )
        return json.loads(response.choices[0].message.content)
    except Exception:
        return {
            "is_crisis": False,
            "message": "오늘 조금 지치셨군요. 작은 행동 하나가 마음을 가볍게 만들어 줄 수 있어요.",
            "quest": "좋아하는 음료 한 잔 마시며 어깨 스트레칭하기"
        }

def transform_experience_to_resume(raw_experience):
    client = get_openai_client()
    if not client:
        return f"• **[역량 재해석]** {raw_experience} 경험을 통해 자기관리 능력 및 트렌드 탐색 역량을 발전시킴."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "사용자의 일상 활동을 기업 인사담당자가 선호하는 직무 역량 언어로 재구성해주세요. (핵심역량 키워드 및 자소서 활용 문장 2개)"},
                {"role": "user", "content": f"내 일상 활동: {raw_experience}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception:
        return "변환 과정 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

# -------------------------------------------------------------------
# 3. 메인 화면 UI 구성
# -------------------------------------------------------------------
st.title("🌱 StepBy (스텝바이)")
st.caption("청년들의 마음건강 케어부터 일상 성취감, 맞춤형 공공 정책까지 함께합니다.")

# 긴급 상담 안내 바
with st.expander("🚨 마음이 너무 힘드신가요? 24시간 상담 핫라인 안내", expanded=False):
    st.error("""
    혼자 견디기 힘들 때는 망설이지 말고 전문가의 도움을 요청하세요.
    * **정신건강 위기상담전화:** ☎️ **109** (24시간 운영) | **청소년 전화:** ☎️ **1388**
    """)

# 사이드바
with st.sidebar:
    st.header("👤 내 프로필 설정")
    st.session_state["user_region"] = st.text_input("거주 지역", value=st.session_state["user_region"])
    st.session_state["user_age"] = st.number_input("나이 (만)", min_value=15, max_value=39, value=st.session_state["user_age"])
    st.session_state["unemployed_months"] = st.number_input("미취업 기간 (개월)", min_value=0, max_value=60, value=st.session_state["unemployed_months"])

# 메인 탭
tab1, tab2, tab3 = st.tabs([
    "🧘 1. 마음 체크인 & 5분 퀘스트", 
    "📝 2. 일상 경험 ➔ 역량 변환기", 
    "🏛️ 3. 내 맞춤 정책 & 청년 공간 맵"
])

# TAB 1
with tab1:
    st.subheader("오늘 내 마음은 어떤가요?")
    col1, col2 = st.columns([1, 1])
    with col1:
        mood_score = st.slider("현재 내 마음 에너지 점수", 1, 5, value=st.session_state["mood_score"])
        mood_text = st.text_area("솔직한 상태를 메모해보세요.", placeholder="예: 취업 준비로 너무 번아웃되었어...")
        if st.button("🌱 5분 퀘스트 받기", type="primary"):
            if not mood_text.strip():
                st.warning("현재 마음 상태를 적어주세요.")
            else:
                with st.spinner("AI가 미션을 준비하고 있습니다..."):
                    st.session_state["todays_quest"] = generate_micro_quest(mood_score, mood_text)
                    st.session_state["quest_completed"] = False
    with col2:
        if st.session_state["todays_quest"]:
            res = st.session_state["todays_quest"]
            if res.get("is_crisis"):
                st.error(res["message"])
                st.info(f"👉 **추천 미션:** {res['quest']}")
            else:
                st.success(f"💬 \"{res['message']}\"")
                st.markdown(f"### 🎯 오늘의 미션\n**{res['quest']}**")
                completed = st.checkbox("✅ 미션을 완료했어요!", value=st.session_state["quest_completed"])
                st.session_state["quest_completed"] = completed
                if completed:
                    st.balloons()
                    st.success("오늘 나를 위한 작은 한 걸음 성공! 🎉")

# TAB 2
with tab2:
    st.subheader("쉬는 동안 한 소소한 일상, 직무 역량으로 바꿔드립니다")
    raw_exp = st.text_area("어떤 활동을 하셨나요?", placeholder="예: 게임 커뮤니티 활동, 블로그 리뷰 작성...")
    if st.button("✨ 역량 언어로 변환하기"):
        if not raw_exp.strip():
            st.warning("활동 내용을 적어주세요.")
        else:
            with st.spinner("자소서 문장으로 재구성 중입니다..."):
                st.session_state["transformed_result"] = transform_experience_to_resume(raw_exp)
    if st.session_state["transformed_result"]:
        st.info(st.session_state["transformed_result"])

# TAB 3
with tab3:
    st.subheader("🏛️ 맞춤 청년 정책 & 주변 청년 공간")
    p_col1, p_col2 = st.columns([1, 1])
    with p_col1:
        st.markdown("#### 🎁 맞춤 정책 지원금")
        for p in MOCK_POLICIES:
            st.markdown(f"""
            <div class="policy-card">
                <span class="policy-tag">{p['category']}</span>
                <div class="policy-title">{p['polyBizSrn']}</div>
                <p style="color:#475569; font-size:0.88rem;">{p['polyItcnCn']}</p>
                <a href="{p['rqutUrla']}" target="_blank" style="color:#2563EB; font-weight:bold; font-size:0.85rem;">상세보기 ➔</a>
            </div>
            """, unsafe_allow_html=True)
    with p_col2:
        st.markdown("#### 📍 내 주변 청년 공간 & 센터")
        df_centers = pd.DataFrame([
            {"name": "서울시 청년활동지원센터", "lat": 37.5384, "lon": 126.9654, "type": "청년공간"},
            {"name": "종로구 정신건강복지센터", "lat": 37.5794, "lon": 126.9868, "type": "심리상담"},
            {"name": "마포 청년나루", "lat": 37.5505, "lon": 126.9080, "type": "청년공간"}
        ])
        m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)
        for _, row in df_centers.iterrows():
            folium.Marker(
                location=[row["lat"], row["lon"]],
                popup=row["name"],
                icon=folium.Icon(color="blue" if row["type"] == "청년공간" else "green")
            ).add_to(m)
        st_folium(m, width="100%", height=400)
