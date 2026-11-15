// 주제별 진행 기록. 새 내용은 해당 주제의 blocks에 추가하고, 작업 기록(log)에 한 줄을 남긴다.
// block 종류: h(소제목) p(문단) list(목록) table(표) media(사진·영상) links(링크) note(강조 박스)
window.PROJECT = {
  title: "home — 인터랙티브 전시 제작 기록",
  subtitle: "AI 기반 영상 제작 워크샵 기말 프로젝트 · Unreal Engine 5.4 · 3m × 3m 체험 전시",
  status: "브라운관·지하철(영상 없음) 확정 → 앉는 가구(소파/리클라이너)만 남음 · 크브페 마감 11/23",
  updated: "2026-11-15 16:10",
  // 큰 흐름. state: done(끝) / now(진행 중) / todo(아직)
  phases: [
    { name: "기획·공간 구조", state: "done" },
    { name: "배치안 5종 + 안 5 변형 8가지", state: "done" },
    { name: "본안 결정 (가구만 남음)", state: "now" },
    { name: "인터랙션 구현 (블루프린트)", state: "todo" },
    { name: "소리·센서·QR", state: "todo" },
    { name: "리허설 · 시연", state: "todo" }
  ],
  // 지금 정해야 하는 것 (홈 화면 상단 카드)
  decision: {
    q: "앉는 가구: 2인 소파 vs 1인 리클라이너",
    pick: "추천: 1인 리클라이너",
    why: "1인 체험이라 자리가 하나면 충분하고, 등받이를 젖히는 동작 자체가 '안주'를 보여 준다. 실물 2인 소파는 폭 140~160이라 자리(122)에 안 들어갈 수 있다.",
    alt: "브라운관 TV · 지하철 칸(손잡이, 영상 없음)은 확정 · 조명은 3500K로 더 희게",
    img: "assets/prev_Opt5C_crt_B_OverSofa.jpg",
    link: "reports/status.html#seat"
  },
  // 다음 할 일. who: 팀 / 지원 / Claude, state: now / todo / done
  next: [
    { title: "앉는 가구 결정 (소파 vs 리클라이너)", detail: "브라운관은 확정. 앉는 가구 하나만 고르면 조명 3500K로 최종 렌더를 뽑는다. 나머지 추천안도 다르면 같이 알려 주기.", who: "팀", time: "10분", state: "now", link: "reports/status.html#decide", linkLabel: "결정 현황 보기" },
    { title: "크브페 지원서 완성·제출 (11/23 23:59)", detail: "채움본을 HWP에 붙이고 사진 11장 넣고 HWP + PDF로 메일 제출.", who: "지원", time: "11/22까지", state: "todo", link: "https://claude.ai/artifact/53y4wg4Gp9aoq7Mgd13yaY", linkLabel: "채움본" },
    { title: "블루프린트 0~2단계", detail: "키 입력 설정(IMC_Home) → 문 열면 TV·조명 켜짐(BP_HomeDoor) → 소파 착석 감지(BP_SitZone).", who: "지원 + Claude", time: "1~2시간", state: "todo", link: "reports/home_interaction.html#guide", linkLabel: "단계별 안내" },
    { title: "소리 파일 5개", detail: "지하철 칸 소리 1개 + 집 소리 0~3단계(점점 이상하고 불편하게) 4개.", who: "팀", time: "반나절", state: "todo" },
    { title: "크브페 지원서 인터랙션 문단", detail: "인터랙션 페이지 맨 아래 긴/짧은 문단을 복사해 붙인다. HWP를 주면 Claude가 채워 줄 수 있다.", who: "지원", time: "20분", state: "todo", link: "reports/home_interaction.html#cbf", linkLabel: "문단 복사하기" },
    { title: "아두이노 문 센서 테스트", detail: "Leonardo + 자석(리드) 스위치 1개 → 문이 열리면 키보드 키 입력처럼 Unreal에 전달.", who: "팀", time: "1시간", state: "todo", link: "reports/home_interaction.html#guide", linkLabel: "아두이노 코드" },
    { title: "CCTV용 마네킹", detail: "Unreal만으로 시연할 때 CCTV 화면에 사람이 보이도록 움직이는 마네킹을 넣는다.", who: "Claude", time: "30분", state: "todo" },
    { title: "결과 QR 이미지", detail: "관객별 QR은 블루프린트로 못 만들어서, 결과 견본 페이지 주소로 QR 하나를 만들어 시연한다.", who: "Claude", time: "10분", state: "todo", link: "reports/result_sample.html", linkLabel: "결과 견본" },
    { title: "(선택) 워크스루 끝 출구 밝히기", detail: "워크스루 영상 끝부분에서 출구 바깥이 어둡게 나온다.", who: "Claude", time: "20분", state: "todo" }
  ],
  // 최근에 끝낸 것
  done: [
    "전체 현황 한 페이지 (ver7)",
    "브라운관 TV 확정 · 지하철 칸 영상 없이 손잡이로 확정",
    "안 5 치수표 (가벽·지하철 칸·가구) 만들기",
    "브라운관/프로젝터 × 가구 4종 = 8가지 비교·점수표",
    "프로젝터 레벨 2개 렌더·워크스루, 추천 4개 동시 비교 영상",
    "인터랙션을 블루프린트 구조로 다시 설계 + 단계별 안내",
    "크브페 지원서용 인터랙션 문단 (긴/짧은)"
  ]
};

window.TOPICS = [
  {
    id: "concept", num: "01", title: "전시 개요",
    summary: "사회(A)에서 문을 열고 집(B)으로 들어가는 3m × 3m 체험 전시",
    blocks: [
      { type: "p", text: "관객은 어둡고 차가운 A 공간(사회)에서 시작해, 직접 문을 열고 따뜻한 B 공간(집)으로 들어간다. B의 소파에 앉으면 끝이 없는 편안한 영상이 계속 흐르고, 언제 나갈지는 관객이 정한다." },
      { type: "p", text: "주제는 'home'이다. 집은 내 편이 되어 주는 공간이지만, 익숙해지면 안주하게 되는 공간이기도 하다. 나갈 때 머문 시간을 보여 주고, 그 의미는 관객이 판단한다." },
      { type: "h", text: "빌드업 회의에서 정한 방향" },
      { type: "list", items: [
        "소파 앞쪽에 나가는 문을 둔다. 다음 단계로 나아가는 느낌을 주기 위해서다.",
        "출구에서 나가면 할 공간이 없으므로 진짜 출구로 두고 의미를 부여한다.",
        "단순히 몇 분 있었는지가 아니라, 다른 사람들에 비해 얼마나 있었는지와 그 의미를 보여 준다.",
        "인터랙션을 더 다양하게: 버튼을 누르면 영상 등이 바뀌고, 움직임 분석으로 반응이 바뀌게 한다."
      ]},
      { type: "h", text: "설치 규격" },
      { type: "table", head: ["규격", "대응"], rows: [
        ["전시 공간 3m × 3m", "A와 B로 나눠 배치 (배치안별로 비율이 다름)"],
        ["배정 벽면 1면", "B 영상은 배정 벽(오른쪽)에만 투사, A 영상은 직접 세우는 가벽에 투사"],
        ["벽·천장 고정 시 방식 기재", "가벽과 문틀은 바닥에 서는 자립 구조"],
        ["기자재 대여 불가", "프로젝터 2대, PC, 스피커, 소파 직접 준비"],
        ["유선 인터넷 불가", "인터넷 없이 PC에서 오프라인 실행"]
      ]},
      { type: "links", items: [{ label: "처음 세운 전시 구조 계획 (HTML)", href: "reports/structure_plan_original.html" }] }
    ]
  },
  {
    id: "structure", num: "02", title: "공간 구조 만들기",
    summary: "기존 계획을 Unreal에 치수 그대로 지은 첫 버전",
    blocks: [
      { type: "p", text: "Twinmotion 대신 Unreal Engine 5.4에서 Python 스크립트로 공간을 지었다. 스크립트에 숫자(cm)로 치수를 적어 두면 실행할 때마다 똑같이 지어지고, 레이아웃을 바꿀 때는 숫자만 고치면 된다." },
      { type: "h", text: "구성 (기존 계획 기준)" },
      { type: "table", head: ["항목", "크기·위치 (cm)"], rows: [
        ["전체", "300 × 300, 벽 높이 240, 벽 두께 10"],
        ["A 사회 / B 집", "A 120 × 300 / B 180 × 300 (가벽 X=120)"],
        ["문", "폭 80 × 높이 210. 입구(위쪽 벽 왼쪽), A→B 문(가벽 아래쪽), 출구(위쪽 벽 오른쪽 끝)"],
        ["A 영상", "가벽의 A쪽 면, 폭 190"],
        ["B 영상", "오른쪽 배정 벽, 폭 220"],
        ["소파", "75 × 160, 영상 벽을 바라봄"],
        ["조명", "A 6500K 차가운 조명 1개, B 2700K 따뜻한 조명 2개"]
      ]},
      { type: "media", items: [
        { type: "image", src: "assets/2026-11-13_first_top.jpg", caption: "위에서 본 첫 버전" },
        { type: "image", src: "assets/2026-11-13_first_a.jpg", caption: "A 사회 · 입구 시점" },
        { type: "image", src: "assets/2026-11-13_first_b.jpg", caption: "B 집 · 소파 뒤 시점" },
        { type: "image", src: "assets/2026-11-13_first_corner.jpg", caption: "B 집 · 출구 모서리 시점" }
      ]},
      { type: "note", text: "처음에는 실내가 하얗게 날아가서 노출을 고정하는 설정을 추가했고, 눈높이에서 시야를 가리던 A 프로젝터는 천장 쪽으로 올렸다." },
      { type: "links", items: [
        { label: "오브젝트별 크기·위치 정리 — 처음 계획 (HTML)", href: "reports/objects_current.html" },
        { label: "첫 버전 스크립트", href: "scripts/build_exhibition_v1.py" }
      ]}
    ]
  },
  {
    id: "review", num: "03", title: "배치 검토: 공간이 좁다",
    summary: "B 공간 소파–화면 84cm, 시야각 76° → 대안 3가지 검토",
    blocks: [
      { type: "p", text: "기존 계획을 3D로 지어 보니, A 공간은 의도대로 좁고 차가웠지만 B 공간은 '편안한 집'보다 꽉 막힌 느낌에 가까웠다." },
      { type: "table", head: ["지표", "값", "의미"], rows: [
        ["소파 앞면 → 영상 벽", "84cm", "출구로 가는 동선도 이 사이를 지나야 함"],
        ["앉은 자리 → 화면", "약 140cm", "폭 220cm 화면을 가까이서 봄"],
        ["화면 시야각", "약 76°", "거실 TV(30~40°)의 두 배. 고개를 돌려야 화면 끝이 보임"],
        ["소파 뒤 여유", "10cm", "가벽에 붙어 있어 뒤로 뺄 수 없음"]
      ]},
      { type: "note", text: "근본 원인은 B 공간의 폭(180cm)이다. 소파가 오른쪽 벽을 바라보는 한, 소파 깊이와 시청 거리가 모두 이 안에 들어가야 한다." },
      { type: "h", text: "대안" },
      { type: "table", head: ["안", "공간 분할", "화면 폭", "시청 거리", "시야각"], rows: [
        ["기존 계획", "A 120 / B 180", "220", "약 140", "76°"],
        ["안 1. 화면 축소", "그대로", "150", "약 140", "56°"],
        ["안 2. 가벽 이동", "A 90 / B 210", "180", "약 170", "56°"],
        ["안 3. 가로로 나누기", "A 300×100 / B 300×200", "160", "약 215", "41°"],
        ["안 4. 안 3 수정 (스케치)", "A 300×100 / B 300×200", "160", "약 240", "37°"]
      ]},
      { type: "p", text: "안 1~3은 B 영상을 배정 벽(오른쪽)에 둔다. 시청 거리가 가장 긴 안 3을 우선 검토안으로 제안했고, 이후 사용자 스케치를 바탕으로 B 영상을 왼쪽 벽으로 옮긴 안 4를 추가했다." },
      { type: "media", items: [{ type: "image", src: "assets/2026-11-13_report_preview.jpg", caption: "배치 검토 보고서 첫 화면" }] },
      { type: "links", items: [{ label: "배치 검토 보고서 전문 (HTML)", href: "reports/layout_review.html" }] }
    ]
  },
  {
    id: "layouts", num: "04", title: "5가지 배치 레벨",
    summary: "기존 계획과 안 1·2·3·4를 각각 Unreal 레벨로 구현",
    blocks: [
      { type: "p", text: "스크립트 하나(build_layouts.py)를 실행하면 레벨 5개(L_Current, L_Opt1~L_Opt4)가 한 번에 만들어진다. 프로젝트를 열면 L_Current가 바로 열리고, 레벨마다 위에서 비스듬히 내려다보는 부감샷 시점이 저장돼 있다." },
      { type: "media", items: [{ type: "image", src: "assets/2026-11-14_layouts_compare5.jpg", caption: "5가지 배치 같은 시점 비교 (위에서 / A 입구 / 소파 뒤 / 모서리)" }] },
      { type: "h", text: "기존 계획 (L_Current)" },
      { type: "media", items: [
        { type: "image", src: "assets/layout_Current_TopView.jpg", caption: "위에서" },
        { type: "image", src: "assets/layout_Current_B_OverSofa.jpg", caption: "소파 뒤 · 화면 220" }
      ]},
      { type: "h", text: "안 1. 화면 축소 (L_Opt1)" },
      { type: "media", items: [
        { type: "image", src: "assets/layout_Opt1_TopView.jpg", caption: "위에서" },
        { type: "image", src: "assets/layout_Opt1_B_OverSofa.jpg", caption: "소파 뒤 · 화면 150" }
      ]},
      { type: "h", text: "안 2. 가벽 이동 (L_Opt2)" },
      { type: "media", items: [
        { type: "image", src: "assets/layout_Opt2_TopView.jpg", caption: "위에서" },
        { type: "image", src: "assets/layout_Opt2_A_Entrance.jpg", caption: "A 입구 · 복도 폭 80" },
        { type: "image", src: "assets/layout_Opt2_B_OverSofa.jpg", caption: "소파 뒤 · 화면 180" }
      ]},
      { type: "h", text: "안 3. 가로로 나누기 (L_Opt3)" },
      { type: "media", items: [
        { type: "image", src: "assets/layout_Opt3_TopView.jpg", caption: "위에서" },
        { type: "image", src: "assets/layout_Opt3_A_Entrance.jpg", caption: "A 3m 복도" },
        { type: "image", src: "assets/layout_Opt3_B_OverSofa.jpg", caption: "소파 뒤 · 화면 160" },
        { type: "image", src: "assets/layout_Opt3_B_Corner.jpg", caption: "출구 모서리에서 본 B" }
      ]},
      { type: "note", text: "안 3에서는 A→B 문이 B 쪽으로 열리면 B 화면을 가려서, A 쪽으로 열리도록 바꿨다." },
      { type: "h", text: "안 4. 안 3 수정 (L_Opt4)" },
      { type: "p", text: "11/13 손스케치를 바탕으로 안 3을 고쳤다. A 복도와 입구는 그대로 두고, B에서는 영상을 왼쪽 벽으로 옮기고 소파를 오른쪽 벽에 붙여 왼쪽 화면을 바라보게 했다. 출구는 아래쪽 벽 왼쪽 끝으로 옮겨, 영상 앞을 지나 나가는 동선이 된다." },
      { type: "media", items: [{ type: "image", src: "assets/layout_Opt4_plan.png", caption: "안 4 배치도 (위에서 본 모습)" }] },
      { type: "table", head: ["항목", "안 3", "안 4"], rows: [
        ["B 영상 위치", "오른쪽 배정 벽", "왼쪽 벽"],
        ["소파", "왼쪽, 오른쪽 화면을 봄", "오른쪽, 왼쪽 화면을 봄"],
        ["A→B 문", "가벽 210~290", "가벽 190~270 (A 쪽으로 열림)"],
        ["출구", "아래쪽 벽 오른쪽", "아래쪽 벽 왼쪽 끝"],
        ["시청 거리 / 시야각", "약 215cm / 41°", "약 240cm / 37°"]
      ]},
      { type: "media", items: [
        { type: "image", src: "assets/layout_Opt4_TopView.jpg", caption: "위에서" },
        { type: "image", src: "assets/layout_Opt4_A_Entrance.jpg", caption: "A 3m 복도" },
        { type: "image", src: "assets/layout_Opt4_B_OverSofa.jpg", caption: "소파 뒤 · 왼쪽 벽 화면 160" },
        { type: "image", src: "assets/layout_Opt4_B_Corner.jpg", caption: "출구 모서리에서 본 B" }
      ]},
      { type: "note", text: "안 4는 B 영상이 배정 벽(오른쪽)이 아닌 왼쪽 벽에 오지만, 규격과 상관없이 이 배치로 진행하기로 했다(11/13 22:36). 스케치에는 A→B 사이가 뚫려 있었지만, 문 센서 인터랙션을 위해 80cm 문을 넣었다." },
      { type: "links", items: [{ label: "build_layouts.py", href: "scripts/build_layouts.py" }] }
    ]
  },
  {
    id: "subway-home", num: "05", title: "안 5 · 지하철에서 집으로",
    summary: "사회를 폭 80 지하철 칸으로 줄이고 집을 넓힘 · 브라운관 TV · 가구 구성 4가지",
    blocks: [
      { type: "p", text: "사회(A)는 폭 80cm의 좁은 지하철 칸으로 줄이고, 영상 없이 공간 디자인만으로 표현했다. 손잡이와 봉, 글자 없는 광고 라이트박스, 초록 노선 LED, 차가운 형광등, 낮은 천장(215), 벽에 붙인 사람 실루엣 판으로 '꽉 찬 지하철'을 만든다. 그만큼 집(B)은 300×220으로 넓어졌다." },
      { type: "list", items: [
        "B 영상은 프로젝터 대신 왼쪽 벽 TV장 위 작은 브라운관 TV로 보여 준다 (소파에서 191cm). 프로젝터 안은 3D 미리보기에서 바꿔 볼 수 있다.",
        "사회→집 문은 집 쪽으로 열리고(경첩 오른쪽), 도어클로저로 저절로 닫힌다. 문이 열리는 범위에는 가구를 두지 않는다.",
        "천장 CCTV(가벽 위 돔 카메라)에서 소파·담요·리모컨·TV·출구가 한 화면에 들어온다. 인터랙션에 쓴다.",
        "가구는 있어도 되고 없어도 되도록 4가지 구성으로 남겼다. 모든 구성에서 소파 위 담요와 리모컨은 기본으로 둔다.",
        "문 앞 동선이 꺾이는 곳의 손잡이는 키 큰 사람 머리에 닿지 않게 뺐다."
      ]},
      { type: "media", items: [{ type: "image", src: "assets/2026-11-15_opt5_compare.jpg", caption: "안 5 가구 구성 4가지 × 카메라 5대 (Unreal)" }] },
      { type: "links", items: [{ label: "안 5 치수표: 가벽·지하철 칸·가구 (HTML)", href: "reports/objects_v5.html" }] },
      { type: "links", items: [{ label: "3D 미리보기 · 가구 켜고 끄기 · 브라운관/프로젝터 전환 (HTML)", href: "reports/home_v5_design.html" }] },
      { type: "table", head: ["구성", "가구", "머물게 하는 것", "나가게 하는 것"], rows: [
        ["A 기본", "러브시트, 담요, 리모컨", "TV와 소파, 담요만 남은 단순한 집", "방이 비어 출구가 늘 보임"],
        ["B 거실", "+ 러그, 스탠드, 화분, 선반", "스탠드 불빛과 TV — 누구나 아는 거실", "가구가 가벽 쪽에 몰려 출구 쪽은 비어 있음"],
        ["C 1인 자리", "리클라이너, 사이드 테이블, 스탠드, 선반", "손 닿는 곳에 다 있는 '나만의 자리'", "자리가 하나라 다음 사람에게 비켜 줘야 함"],
        ["D 생활감", "+ 택배 상자, 빨래 바구니, 옷 행거, 슬리퍼", "어수선하지만 내 물건으로 찬 집", "문 앞 슬리퍼 ↔ 깨끗한 출구"]
      ]},
      { type: "media", items: [
        { type: "image", src: "assets/layout_Opt5A_A_Subway.jpg", caption: "지하철 칸 입구 (모든 구성 같음)" },
        { type: "image", src: "assets/layout_Opt5B_B_OverSofa.jpg", caption: "B 거실 · 소파 뒤에서 본 브라운관" },
        { type: "image", src: "assets/layout_Opt5C_B_Door.jpg", caption: "C 1인 자리 · 문에서 본 집" },
        { type: "image", src: "assets/layout_Opt5D_TopView.jpg", caption: "D 생활감 · 위에서" }
      ]},
      { type: "note", text: "자동 검사: 모든 구성에서 가구가 관객 동선에서 40cm 이상 떨어져 있고, 문이 열리는 범위에 걸리지 않으며, 소파에서 브라운관을 가리지 않는다. 렌더 스크립트(shots5.py)가 같은 카메라를 여러 번 찍던 문제는 카메라 번호를 먼저 올리도록 고쳤다." },
      { type: "h", text: "브라운관 / 프로젝터 × 가구 변형 비교 (11/15)" },
      { type: "p", text: "B 영상을 브라운관으로 볼 때와 프로젝터(왼쪽 벽 160)로 볼 때를 각각, 가구를 거의 비운 안(기본)부터 많이 채운 안(생활감)까지 4가지씩 8가지로 만들어 비교했다. 집다움·안주 메시지·'문 열면 TV가 켜지는' 연출을 두 배로 계산해 점수를 매겼고, 추천한 안은 Unreal에서 실제로 지었다(프로젝터 안은 새 레벨 L_Opt5PA·L_Opt5PB)." },
      { type: "table", head: ["", "안", "이유"], rows: [
        ["추천 1 · 본안", "브라운관 + 거실", "가구를 가벽 쪽에만 둬 집다움은 높고 소파 주변은 깨끗함. 문 열면 TV가 켜지는 장면과 가장 잘 맞고 CCTV에서 담요·리모컨이 잘 보임"],
        ["추천 2", "브라운관 + 생활감", "익숙해진 집을 가장 직접적으로 보여 줌. 준비물이 많고 화면이 어수선해 보일 수 있음"],
        ["추천 3", "프로젝터 + 거실", "화면 각도가 브라운관의 2배 이상(약 37° vs 16°)이라 영상이 잘 보이고 시연 영상으로 찍기 쉬움. 'TV가 켜진다'는 느낌은 약함"],
        ["참고", "프로젝터 + 기본", "가장 단순하지만 상영실처럼 보여 메시지가 약함"]
      ]},
      { type: "media", items: [{ type: "image", src: "assets/2026-11-15_opt5_reco_compare.jpg", caption: "추천 4가지 Unreal 렌더 — 소파 뒤 / 문에서 본 집 / CCTV" }] },
      { type: "note", text: "채울까 비울까: 비우면 상영실처럼 보이고, 거실 가구와 생활감 물건을 한꺼번에 넣으면 가벽 쪽 같은 자리에서 서로 겹친다. 가구를 가벽 쪽 벽에만 붙이는 '거실' 정도가 동선·문·CCTV에 영향 없이 집다움을 가장 크게 올린다." },
      { type: "links", items: [
        { label: "8가지 변형 비교·점수·추천 (HTML)", href: "reports/home_v5_variants.html" },
        { label: "build_layouts.py (안 5: subway_home, 프로젝터 변형 포함)", href: "scripts/build_layouts.py" },
        { label: "shots5.py (레벨별 렌더 5장)", href: "scripts/shots5.py" }
      ]}
    ]
  },
  {
    id: "media", num: "06", title: "벽면 영상(프로젝션) 설정",
    summary: "Media Plate로 벽에 영상 재생 · 파일만 바꾸면 교체",
    blocks: [
      { type: "p", text: "벽면 화면은 Unreal의 Media Plate로 만들었다. Play를 누르면 자동으로 재생되고 끝나면 반복된다. 네 레벨이 같은 영상 파일을 함께 쓴다." },
      { type: "table", head: ["화면", "파일", "비고"], rows: [
        ["A 사회", "Content/Movies/A_society.mp4", "현재 테스트 영상"],
        ["B 집", "Content/Movies/B_home.mp4", "실제 영상으로 교체됨"]
      ]},
      { type: "h", text: "영상 교체 방법" },
      { type: "list", items: [
        "H.264 · 1920×1080 · mp4로 내보낸다.",
        "Unreal을 끄고, Finder에서 Content/Movies에 같은 이름으로 덮어쓴다.",
        "레벨을 열고 Play를 누르면 재생된다 (편집 화면에서는 검게 보이는 것이 정상).",
        "다른 파일 이름을 쓰려면 Exhibition/Media의 MS_A_society, MS_B_home에서 File Path를 바꾼다."
      ]},
      { type: "h", text: "밝기" },
      { type: "p", text: "실제 프로젝션처럼 화면이 가장 밝게 보이도록 방 조명은 2~4lm 수준으로 어둡게, 노출은 수동으로 고정했다. 화면 전체가 너무 밝거나 어두우면 build_layouts.py의 EXPOSURE 값을 조절한다 (+1 = 두 배 밝게)." },
      { type: "note", text: "맥에서 처음 실행할 때 'Metal Toolchain 없음' 오류가 나면 터미널에서 xcodebuild -downloadComponent MetalToolchain 을 실행한다." }
    ]
  },
  {
    id: "walkthrough", num: "07", title: "관객 시점 워크스루 영상",
    summary: "배치별 입구 → A → 문 → 소파 → 출구 30초 영상 5종",
    blocks: [
      { type: "p", text: "다섯 배치 모두 같은 동선으로 관객 시점 영상을 렌더했다. 입구로 들어와 A 복도에서 사회 영상을 보고, 문을 지나 B로 들어가 소파에 앉아 약 6초간 영상을 본 뒤 출구로 나간다." },
      { type: "media", items: [{ type: "video", src: "assets/2026-11-14_walkthrough_compare5.mp4", caption: "5개 배치 동시 비교" }] },
      { type: "h", text: "배치별 영상" },
      { type: "media", items: [
        { type: "video", src: "assets/walk_Current.mp4", caption: "기존 계획" },
        { type: "video", src: "assets/walk_Opt1.mp4", caption: "안 1. 화면 축소" },
        { type: "video", src: "assets/walk_Opt2.mp4", caption: "안 2. 가벽 이동" },
        { type: "video", src: "assets/walk_Opt3.mp4", caption: "안 3. 가로로 나누기" },
        { type: "video", src: "assets/walk_Opt4.mp4", caption: "안 4. 안 3 수정" }
      ]},
      { type: "note", text: "소파 장면을 보면 기존 계획은 화면이 시야를 꽉 채우고, 안 3은 거실 TV처럼 한눈에 들어온다. 렌더 중 화면 하나가 검게 나오던 문제는 영상 재생을 시퀀스 시간에 맞추는 방식으로 해결했다. 안 4는 소파에서 왼쪽 벽 화면을 정면으로 보며, A 복도 끝(8~10초)에서는 잠깐 막힌 벽을 보고 문 쪽으로 돌아선다." },
      { type: "h", text: "안 5 · 지하철에서 집으로 (11/15)" },
      { type: "p", text: "지하철 칸을 지나 문을 밀고 집으로 들어가, 소파에서 브라운관을 보다가 출구로 나간다. 지하철 칸 끝에서 막힌 벽만 보이지 않도록 문 쪽으로 미리 고개를 돌리게 카메라 방향을 고쳤다." },
      { type: "media", items: [{ type: "video", src: "assets/2026-11-15_opt5_walk_compare.mp4", caption: "안 5 가구 구성 4가지 동시 비교" }] },
      { type: "media", items: [
        { type: "video", src: "assets/walk_Opt5A.mp4", caption: "안 5 A 기본" },
        { type: "video", src: "assets/walk_Opt5B.mp4", caption: "안 5 B 거실" },
        { type: "video", src: "assets/walk_Opt5C.mp4", caption: "안 5 C 1인 자리" },
        { type: "video", src: "assets/walk_Opt5D.mp4", caption: "안 5 D 생활감" }
      ]},
      { type: "h", text: "추천안 비교 (11/15)" },
      { type: "media", items: [{ type: "video", src: "assets/2026-11-15_opt5_reco_walk.mp4", caption: "추천 1 브라운관+거실 · 추천 2 브라운관+생활감 · 추천 3 프로젝터+거실 · 참고 프로젝터+기본" }] },
      { type: "media", items: [
        { type: "video", src: "assets/walk_Opt5PB.mp4", caption: "프로젝터 + 거실" },
        { type: "video", src: "assets/walk_Opt5PA.mp4", caption: "프로젝터 + 기본" }
      ]},
      { type: "links", items: [{ label: "make_walkthrough.py", href: "scripts/make_walkthrough.py" }] }
    ]
  },
  {
    id: "interaction", num: "08", title: "인터랙션 설계 (블루프린트)",
    summary: "문 → TV·조명 · 천장 CCTV 인식 → 불편한 소리 · 퇴장 QR · 모두 Unreal 블루프린트로",
    blocks: [
      { type: "note", text: "교수님 의견에 따라 인터랙션은 Unreal Engine 5 블루프린트로 구현한다. 문·TV·조명·소리 단계·기록·결과 화면은 모두 블루프린트가 처리하고, 센서(아두이노 Leonardo를 키보드처럼)와 웹캠 인식(OSC)은 블루프린트에 신호만 넣는다." },
      { type: "p", text: "집은 관객을 반겨 주지만, 편안함에 몸을 맡길수록 조금씩 불편해진다. 천장 CCTV가 관객이 앉고, 담요를 옮기고, 리모컨을 만지는 것을 알아채 소리를 바꾸고, 나갈 때는 QR 코드로 자신이 이 집에서 어떻게 머물렀는지를 돌려받는다." },
      { type: "table", head: ["#", "트리거", "감지", "반응"], rows: [
        ["1", "문을 엶", "문틀 자석 센서 → 아두이노", "브라운관 지지직 → 집 영상, 2700K 조명 켜짐, 문이 닫히면 지하철 소리 끊김"],
        ["2", "편하게 앉음", "CCTV: 소파 영역 3초 + 등받이로 기댐", "편안한 소리에서 시작해 단계가 오름"],
        ["3", "담요를 옮김", "CCTV: 처음 사진과 담요 영역 비교", "낮은 웅웅거림이 깔림"],
        ["4", "리모컨을 만짐", "CCTV: 손이 리모컨 영역에 1초 (+ 기울기 센서)", "채널 소리가 일그러지고 같은 영상으로 돌아옴"],
        ["5", "오래, 편하게 머묾", "머문 시간 + 2·3·4 누적", "소리 4단계: 편안 → 미세함 → 이상함 → 불편"],
        ["6", "출구로 나감", "출구 문 센서 + CCTV 출구 영역", "QR → 타임랩스, 만진 물건, 다른 관객 평균 대비 머문 시간"]
      ]},
      { type: "media", items: [{ type: "image", src: "assets/layout_Opt5A_CCTV.jpg", caption: "Unreal 안 5A 천장 CCTV 시점 — 소파·담요·리모컨·TV·출구가 한 화면에" }] },
      { type: "h", text: "블루프린트 구성" },
      { type: "table", head: ["블루프린트", "하는 일"], rows: [
        ["BP_HomeDirector", "상태·기록·소리 단계, 입력 받기, 조명·TV·소리 제어, 퇴장 처리 (레벨에 1개)"],
        ["BP_HomeDoor", "경첩이 원점인 문. Timeline으로 집 쪽 90° 열림 → 3초 뒤 저절로 닫힘"],
        ["BP_SitZone · BP_ExitZone", "소파·출구 위 충돌 박스 → OnSeated / OnStoodUp / OnExit"],
        ["BP_Blanket · BP_Remote", "바라보고 E 키(또는 3·4 키)로 만짐 → Director에 알림"],
        ["BP_CCTV", "Scene Capture 2D로 2초마다 타임랩스 프레임 저장"],
        ["SG_Visitors · WBP_Result", "머문 시간 저장(SaveGame) → 평균·순위 → 결과 화면(UMG)과 QR"]
      ]},
      { type: "p", text: "Python으로 지은 레벨의 벽·조명·화면에는 이름과 같은 태그(Light_B_Warm_1, Screen_B_Home, Door_Partition, Blanket, Remote 등)를 붙여 두었다. 블루프린트는 Get All Actors with Tag로 찾기 때문에, 레벨을 다시 지어도 연결이 끊기지 않는다." },
      { type: "links", items: [
        { label: "인터랙션 설계 + 블루프린트 단계별 가이드 + 아두이노 코드 + 지원서 문단 (HTML)", href: "reports/home_interaction.html" },
        { label: "QR 결과 페이지 견본 (예시 데이터)", href: "reports/result_sample.html" }
      ]},
      { type: "note", text: "개인정보: 입구에서 촬영을 알리고, 얼굴 없이 위에서 본 움직임만 기록하며, 결과 페이지는 24시간 뒤 삭제한다. 공개 저장소에는 관객 기록을 올리지 않고 예시 데이터만 둔다. 소리는 75dB 이하, 출구는 잠그지 않는다." },
      { type: "h", text: "시연 (실물 전시 없이)" },
      { type: "list", items: [
        "Unreal 워크스루 영상으로 지하철 칸 → 문 → 집 → 출구를 보여 줌",
        "블루프린트 라이브: 플레이 상태에서 1~6 키로 문·앉기·담요·리모컨·소리 단계·퇴장을 차례로 실행",
        "아두이노 + 자석 센서를 붙인 작은 문을 열면 Unreal 속 문이 열림",
        "퇴장 결과 화면(머문 시간·평균·만진 물건)과 QR → 심사위원 휴대폰으로 견본 결과 페이지"
      ]}
    ]
  },
  {
    id: "setup", num: "09", title: "작업 환경 · 실행 방법",
    summary: "프로젝트 위치, 스크립트 실행, 자주 쓰는 명령",
    blocks: [
      { type: "table", head: ["항목", "위치·방법"], rows: [
        ["프로젝트 폴더", "문서/Unreal Projects/AICLASS_prototype1"],
        ["레벨", "콘텐츠 드로어 → Exhibition → Maps (시작 맵: L_Current)"],
        ["영상 파일", "Content/Movies"],
        ["스크립트", "Scripts/build_layouts.py, make_walkthrough.py, rebuild_one.py, walk_one.py, go.py, shots5.py"],
        ["워크스루 영상", "워크스루_영상 폴더"],
        ["진행 기록 저장소", "home-exhibition 폴더 (GitHub Desktop)"]
      ]},
      { type: "h", text: "스크립트 실행" },
      { type: "p", text: "Unreal 아래쪽 출력 로그 입력칸(Cmd)에 py \"스크립트 경로\" 를 입력한다. 입력기가 한글이면 앞 글자가 깨질 수 있으니 영문 상태에서 입력한다." },
      { type: "list", items: [
        "공간 다시 짓기: build_layouts.py (EX_로 시작하는 물체를 지우고 새로 지음)",
        "워크스루 다시 찍기: make_walkthrough.py (다섯 배치 약 4분)",
        "레벨 하나만: Saved/one.txt에 Opt4처럼 적고 rebuild_one.py(다시 짓기) 또는 walk_one.py(워크스루)",
        "안 5 렌더 사진: Saved/shots.txt에 Opt5A,Opt5B,Opt5C,Opt5D,Opt5PA,Opt5PB 중 원하는 레벨을 적고 shots5.py를 실행할 때마다 한 레벨씩 카메라 5대 (약 40초)",
        "레벨 물체에는 이름과 같은 태그가 붙음 → 블루프린트에서 Get All Actors with Tag로 찾기 (BP_로 시작하는 블루프린트는 다시 지어도 지워지지 않음)",
        "부감샷 시점 바꾸기: build_layouts.py의 OVERHEAD_EYE 값 수정 후 다시 실행"
      ]}
    ]
  }
];

window.LOG = [
  { date: "2026-11-15", time: "16:10", text: "ver7: 전체 현황 한 페이지(status.html) — 결정 현황 15개, 진행률, 다음 할 일, 장비, 크브페 진행, 설계 과정, 버전 기록" },
  { date: "2026-11-15", time: "15:20", text: "안 5 치수표 HTML: 가벽 제작 치수(순수 290 = 185 + 문 80 + 25), 지하철 칸 단면·손잡이, 소파/리클라이너별 가구 치수" },
  { date: "2026-11-15", time: "14:40", text: "홈 화면 개편: 지금 할 일·결정할 것·진행 단계가 첫 화면에 바로 보이게" },
  { date: "2026-11-15", time: "14:30", text: "브라운관/프로젝터 × 가구 8가지 비교 → 본안 브라운관+거실 추천, 프로젝터 레벨 2개 Unreal 렌더·워크스루, 인터랙션을 블루프린트 구현으로 개편(단계별 가이드·아두이노 코드·지원서 문단)" },
  { date: "2026-11-15", time: "14:00", text: "안 5(지하철 칸 → 넓은 집, 브라운관 TV, 가구 4구성) Unreal 렌더 20장·워크스루 4개 완료, 3D 미리보기·인터랙션 설계·QR 결과 견본 페이지 추가" },
  { date: "2026-11-14", time: "02:00", text: "안 4 Unreal 레벨 생성·렌더 4장·워크스루 영상 완료, 5개 배치 비교 시트·동시 비교 영상 갱신" },
  { date: "2026-11-13", time: "22:20", text: "안 4(안 3 수정) 설계: 스케치 기반 배치도·스크립트 추가, 렌더는 맥 연결 복구 후 진행" },
  { date: "2026-11-13", time: "21:55", text: "진행 기록 페이지를 주제별 구성으로 바꾸고 워크스루 영상 5종 전체 업로드" },
  { date: "2026-11-13", time: "21:45", text: "진행 기록 저장소(home-exhibition) 생성" },
  { date: "2026-11-13", time: "21:40", text: "배치별 관객 시점 워크스루 영상 렌더" },
  { date: "2026-11-13", time: "21:20", text: "시작 맵(L_Current)과 부감샷 시점 설정" },
  { date: "2026-11-13", time: "20:55", text: "4가지 배치 레벨 + 벽면 영상 재생 준비" },
  { date: "2026-11-13", time: "19:55", text: "배치 검토 보고서: 공간이 좁다, 대안 3가지" },
  { date: "2026-11-13", time: "19:15", text: "오브젝트 크기·위치 정리 문서" },
  { date: "2026-11-13", time: "19:10", text: "Unreal로 공간 구조 첫 생성" }
];
