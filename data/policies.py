"""
청년 취업·마음건강 지원 정책 샘플 데이터

주의: 아래 데이터는 실제 존재하는 정책(2026년 기준 조사)을 바탕으로 정리한
'데모용 샘플'입니다. 지원 금액·자격 요건은 예산/시기에 따라 계속 바뀌기 때문에,
실제 서비스로 발전시킬 때는 아래 두 가지 방법을 참고하세요.

1) 실시간 연동: 한국고용정보원이 '온통청년(youthcenter.go.kr)'을 통해
   청년정책 Open API를 제공해요 (공공데이터포털 data.go.kr에도 동일 API가
   '한국고용정보원_온통청년_청년정책API'라는 이름으로 등록되어 있어요).
   - 온통청년 회원가입 -> [마이페이지 > OPEN API]에서 인증키 신청 (승인 필요)
   - [이용안내 > OPEN API 소개] 문서에서 정확한 엔드포인트/파라미터 확인
     (HTTPS 요청 -> XML 응답 방식)
   - 정확한 URL은 문서 버전에 따라 달라질 수 있어 여기서는 고정해두지 않았어요.
     팀에서 인증키를 받으면 requests + xml.etree.ElementTree 조합으로
     아래 POLICIES와 같은 딕셔너리 리스트로 변환해서 쓰면 돼요.

2) 지금처럼 샘플 데이터로 먼저 완성 -> 발표/데모 이후 실데이터 연동은
   다음 단계 과제로 넘기기 (README.md의 '다음 단계' 참고)
"""

POLICIES = [
    {
        "id": "national_job_support",
        "name": "국민취업지원제도 Ⅰ유형 - 구직촉진수당",
        "org": "고용노동부",
        "summary": "구직활동을 하는 청년에게 매달 생계비를 지원하고, 상담부터 취업 알선까지 함께 도와주는 제도예요.",
        "benefit": "월 60만 원 × 최대 6개월 (총 360만 원) + 취업지원서비스",
        "min_unemployment_months": 0,  # 취업 경험이 없어도 '청년특례유형'으로 신청 가능
        "age_range": "만 15~34세 (청년특례유형)",
        "extra_condition": "기준 중위소득 120% 이하 · 재산 5억 원 이하",
        "how_to_apply": "고용24(work24.go.kr) 온라인 신청 또는 관할 고용센터 방문",
        "url": "https://www.work24.go.kr",
    },
    {
        "id": "youth_challenge",
        "name": "청년도전지원사업",
        "org": "고용노동부 · 지자체 청년센터",
        "summary": "오랫동안 구직활동을 쉬었던 청년이 자신감을 회복하고 다시 도전할 수 있도록 맞춤형 프로그램을 제공해요.",
        "benefit": "단기(5주) / 중기(15주, 참여수당 150만 원) / 장기(25주, 참여수당 250만 원) + 이수·취업 인센티브",
        "min_unemployment_months": 6,  # 최근 6개월간 취업·교육·훈련 이력 없는 '구직단념청년' 기준
        "age_range": "만 18~34세",
        "extra_condition": "최근 6개월간 취업·교육·직업훈련 이력이 없는 구직단념청년",
        "how_to_apply": "고용24(work24.go.kr) 또는 거주지 청년센터",
        "url": "https://www.work24.go.kr",
    },
    {
        "id": "youth_mind_voucher",
        "name": "청년 마음건강 바우처 (전국민 마음투자 지원사업)",
        "org": "보건복지부",
        "summary": "우울·불안 등 정서적 어려움을 겪는 청년에게 전문 심리상담사와의 상담을 지원해요.",
        "benefit": "전문 심리상담 서비스 총 8회 (1회당 7~8만 원 상당, 소득에 따라 본인부담 0~30%)",
        "min_unemployment_months": 0,
        "age_range": "만 19~34세 (지자체별로 39세까지 확대 운영)",
        "extra_condition": "정서적 어려움이 있는 청년이면 신청 가능 (별도 소득 기준 없음)",
        "how_to_apply": "거주지 정신건강복지센터 또는 복지로(bokjiro.go.kr)",
        "url": "https://www.bokjiro.go.kr",
    },
]


def get_matching_policies(unemployment_months: int):
    """
    사용자의 미취업 기간(개월 수)을 기준으로, 신청 조건을 충족하는 정책이
    위쪽에 오도록 정렬해서 반환해요.

    반환값: [(정책 딕셔너리, 조건 충족 여부(bool)), ...]
    """
    def is_eligible(policy):
        return unemployment_months >= policy["min_unemployment_months"]

    ranked = sorted(POLICIES, key=lambda p: not is_eligible(p))
    return [(p, is_eligible(p)) for p in ranked]
