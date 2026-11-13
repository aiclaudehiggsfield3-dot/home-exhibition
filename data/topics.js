// 주제별 진행 기록. 새 내용은 해당 주제의 blocks에 추가하고, 작업 기록(log)에 한 줄을 남긴다.
// block 종류: h(소제목) p(문단) list(목록) table(표) media(사진·영상) links(링크) note(강조 박스)
window.PROJECT = {
  title: "home — 인터랙티브 전시 제작 기록",
  subtitle: "AI 기반 영상 제작 워크샵 기말 프로젝트 · Unreal Engine 5.4 · 3m × 3m 체험 전시",
  status: "배치 4안 비교 중",
  updated: "2026-11-13 21:55",
  next: [
    "A(사회) 영상을 실제 파일로 교체 (Content/Movies/A_society.mp4)",
    "4가지 배치 중 최종안 결정",
    "인터랙션 ① 문 센서 → 장면 전환 (키보드로 먼저, 이후 아두이노)"
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
        { label: "오브젝트별 크기·위치 정리 (HTML)", href: "reports/objects_current.html" },
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
        ["안 3. 가로로 나누기", "A 300×100 / B 300×200", "160", "약 215", "41°"]
      ]},
      { type: "p", text: "네 안 모두 B 영상은 배정 벽(오른쪽)에 둔다. 시청 거리가 가장 긴 안 3을 우선 검토안으로 제안했다." },
      { type: "media", items: [{ type: "image", src: "assets/2026-11-13_report_preview.jpg", caption: "배치 검토 보고서 첫 화면" }] },
      { type: "links", items: [{ label: "배치 검토 보고서 전문 (HTML)", href: "reports/layout_review.html" }] }
    ]
  },
  {
    id: "layouts", num: "04", title: "4가지 배치 레벨",
    summary: "기존 계획과 안 1·2·3을 각각 Unreal 레벨로 구현",
    blocks: [
      { type: "p", text: "스크립트 하나(build_layouts.py)를 실행하면 레벨 4개(L_Current, L_Opt1, L_Opt2, L_Opt3)가 한 번에 만들어진다. 프로젝트를 열면 L_Current가 바로 열리고, 레벨마다 위에서 비스듬히 내려다보는 부감샷 시점이 저장돼 있다." },
      { type: "media", items: [{ type: "image", src: "assets/2026-11-13_layouts_compare.jpg", caption: "4가지 배치 같은 시점 비교 (위에서 / A 입구 / 소파 뒤 / 모서리)" }] },
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
      { type: "links", items: [{ label: "build_layouts.py", href: "scripts/build_layouts.py" }] }
    ]
  },
  {
    id: "media", num: "05", title: "벽면 영상(프로젝션) 설정",
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
    id: "walkthrough", num: "06", title: "관객 시점 워크스루 영상",
    summary: "배치별 입구 → A → 문 → 소파 → 출구 30초 영상 5종",
    blocks: [
      { type: "p", text: "네 배치 모두 같은 동선으로 관객 시점 영상을 렌더했다. 입구로 들어와 A 복도에서 사회 영상을 보고, 문을 지나 B로 들어가 소파에 앉아 약 6초간 영상을 본 뒤 출구로 나간다." },
      { type: "media", items: [{ type: "video", src: "assets/2026-11-13_walkthrough_compare.mp4", caption: "4개 배치 동시 비교" }] },
      { type: "h", text: "배치별 영상" },
      { type: "media", items: [
        { type: "video", src: "assets/walk_Current.mp4", caption: "기존 계획" },
        { type: "video", src: "assets/walk_Opt1.mp4", caption: "안 1. 화면 축소" },
        { type: "video", src: "assets/walk_Opt2.mp4", caption: "안 2. 가벽 이동" },
        { type: "video", src: "assets/walk_Opt3.mp4", caption: "안 3. 가로로 나누기" }
      ]},
      { type: "note", text: "소파 장면을 보면 기존 계획은 화면이 시야를 꽉 채우고, 안 3은 거실 TV처럼 한눈에 들어온다. 렌더 중 화면 하나가 검게 나오던 문제는 영상 재생을 시퀀스 시간에 맞추는 방식으로 해결했다." },
      { type: "links", items: [{ label: "make_walkthrough.py", href: "scripts/make_walkthrough.py" }] }
    ]
  },
  {
    id: "interaction", num: "07", title: "인터랙션 계획",
    summary: "문 센서 → 소파 착석 → 체류 시간 비교 순으로 구현 예정",
    blocks: [
      { type: "p", text: "팀원 모두 처음 하는 기준으로, 앞 단계가 다음 단계의 기초가 되게 순서를 정했다. 아두이노 Leonardo/Pro Micro를 키보드처럼 인식시키면, Unreal에서는 키 입력만 받으면 되고 시연 때 실물 없이도 키보드로 같은 동작을 보여 줄 수 있다." },
      { type: "table", head: ["순서", "인터랙션", "방법", "상태"], rows: [
        ["①", "문을 열면 장면 전환 (A 소리 줄고 B 영상 시작)", "문틀 자석 센서 → 아두이노 → 키 입력", "예정"],
        ["②", "소파에 앉으면 조명이 따뜻해지고, 일어나면 영상이 멈춤", "방석 밑 압력 센서/버튼", "예정"],
        ["③", "나갈 때 다른 관객 대비 체류 시간 표시", "SaveGame으로 기록 누적 + 화면 UI", "예정"],
        ["④", "리모컨 버튼으로 B 영상 장면 바꾸기", "버튼 추가 + B 영상 2~3개", "여유 시"],
        ["⑤", "움직임 분석 (가만히 있을수록 아늑해짐)", "웹캠 + MediaPipe → OSC", "여유 시"]
      ]}
    ]
  },
  {
    id: "setup", num: "08", title: "작업 환경 · 실행 방법",
    summary: "프로젝트 위치, 스크립트 실행, 자주 쓰는 명령",
    blocks: [
      { type: "table", head: ["항목", "위치·방법"], rows: [
        ["프로젝트 폴더", "문서/Unreal Projects/AICLASS_prototype1"],
        ["레벨", "콘텐츠 드로어 → Exhibition → Maps (시작 맵: L_Current)"],
        ["영상 파일", "Content/Movies"],
        ["스크립트", "Scripts/build_layouts.py, Scripts/make_walkthrough.py"],
        ["워크스루 영상", "워크스루_영상 폴더"],
        ["진행 기록 저장소", "home-exhibition 폴더 (GitHub Desktop)"]
      ]},
      { type: "h", text: "스크립트 실행" },
      { type: "p", text: "Unreal 아래쪽 출력 로그 입력칸(Cmd)에 py \"스크립트 경로\" 를 입력한다. 입력기가 한글이면 앞 글자가 깨질 수 있으니 영문 상태에서 입력한다." },
      { type: "list", items: [
        "공간 다시 짓기: build_layouts.py (EX_로 시작하는 물체를 지우고 새로 지음)",
        "워크스루 다시 찍기: make_walkthrough.py (네 배치 약 3분)",
        "부감샷 시점 바꾸기: build_layouts.py의 OVERHEAD_EYE 값 수정 후 다시 실행"
      ]}
    ]
  }
];

window.LOG = [
  { date: "2026-11-13", time: "21:55", text: "진행 기록 페이지를 주제별 구성으로 바꾸고 워크스루 영상 5종 전체 업로드" },
  { date: "2026-11-13", time: "21:45", text: "진행 기록 저장소(home-exhibition) 생성" },
  { date: "2026-11-13", time: "21:40", text: "배치별 관객 시점 워크스루 영상 렌더" },
  { date: "2026-11-13", time: "21:20", text: "시작 맵(L_Current)과 부감샷 시점 설정" },
  { date: "2026-11-13", time: "20:55", text: "4가지 배치 레벨 + 벽면 영상 재생 준비" },
  { date: "2026-11-13", time: "19:55", text: "배치 검토 보고서: 공간이 좁다, 대안 3가지" },
  { date: "2026-11-13", time: "19:15", text: "오브젝트 크기·위치 정리 문서" },
  { date: "2026-11-13", time: "19:10", text: "Unreal로 공간 구조 첫 생성" }
];
