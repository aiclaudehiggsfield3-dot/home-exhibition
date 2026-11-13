// 진행사항 기록. 새 항목은 배열 맨 앞에 추가 (최신이 위)
// media: {type:"image"|"video", src, caption}, links: {label, href}
window.PROJECT = {
  title: "home — 인터랙티브 전시 제작 기록",
  subtitle: "AI 기반 영상 제작 워크샵 기말 프로젝트 · Unreal Engine 5.4",
  status: "배치 4안 비교 중",
  next: [
    "A(사회) 영상 실제 파일로 교체 (Content/Movies/A_society.mp4)",
    "4가지 배치 중 최종안 결정",
    "인터랙션 ① 문 센서 → 장면 전환 (키보드로 먼저, 이후 아두이노)"
  ]
};

window.PROGRESS = [
  {
    date: "2026-11-13", time: "21:40",
    title: "배치별 관객 시점 워크스루 영상",
    tags: ["영상", "Unreal"],
    body: [
      "4가지 배치 모두 입구 → A 복도 → 문 → 소파(영상 시청) → 출구까지 관객 시점 영상(각 30초)을 렌더했다.",
      "B 화면에는 실제 집 영상이 들어갔고, A는 아직 테스트 영상이다.",
      "안 3에서 화면 하나가 검게 나오던 문제를 시퀀스 미디어 트랙으로 해결했다."
    ],
    media: [{ type: "video", src: "assets/2026-11-13_walkthrough_compare.mp4", caption: "4개 배치 동시 비교" }],
    links: []
  },
  {
    date: "2026-11-13", time: "21:20",
    title: "시작 맵과 부감샷 시점 설정",
    tags: ["Unreal"],
    body: [
      "프로젝트를 열면 바로 L_Current 레벨이 열리도록 시작 맵을 바꿨다.",
      "레벨마다 비스듬히 내려다보는 부감샷 시점을 저장했고, 천장은 위에서 보면 투명한 한 면짜리 판으로 바꿨다."
    ],
    media: [], links: []
  },
  {
    date: "2026-11-13", time: "20:55",
    title: "4가지 배치 레벨 + 벽면 영상 재생 준비",
    tags: ["Unreal", "배치"],
    body: [
      "스크립트 하나(build_layouts.py)로 기존 계획, 안 1(화면 축소), 안 2(가벽 이동), 안 3(가로로 나누기) 레벨 4개를 만든다.",
      "벽면 화면은 Media Plate로 만들어 Play 시 자동 재생·반복된다. 영상은 Content/Movies의 A_society.mp4, B_home.mp4를 같은 이름으로 교체하면 된다.",
      "방 조명은 어둡게, 노출은 고정해 화면이 가장 밝게 보이도록 맞췄다."
    ],
    media: [{ type: "image", src: "assets/2026-11-13_layouts_compare.jpg", caption: "4가지 배치 렌더 비교" }],
    links: []
  },
  {
    date: "2026-11-13", time: "19:55",
    title: "배치 검토: 공간이 좁다",
    tags: ["보고서", "배치"],
    body: [
      "기존 계획을 그대로 3D로 지어보니 B 공간에서 소파와 화면 사이가 84cm, 화면 시야각이 약 76°로 너무 가까웠다.",
      "배정 벽 조건을 지키는 대안 3가지를 비교했고, 시청 거리가 가장 긴 안 3(가로로 나누기)을 우선 검토안으로 정했다."
    ],
    media: [{ type: "image", src: "assets/2026-11-13_report_preview.jpg", caption: "배치 검토 보고서" }],
    links: [{ label: "배치 검토 보고서", href: "reports/layout_review.html" }]
  },
  {
    date: "2026-11-13", time: "19:10",
    title: "Unreal로 공간 구조 생성",
    tags: ["Unreal", "구조"],
    body: [
      "Python 스크립트로 3m × 3m 공간(A 1.2m / B 1.8m), 가벽·문·출구, 소파, 영상 면, 조명, 카메라를 치수대로 생성했다.",
      "빌드업 회의 내용대로 소파 앞쪽 대각선 방향에 출구를 추가했다."
    ],
    media: [
      { type: "image", src: "assets/2026-11-13_first_top.jpg", caption: "처음 지은 공간 (위에서)" },
      { type: "image", src: "assets/2026-11-13_first_b.jpg", caption: "B 공간 소파 뒤 시점" }
    ],
    links: [
      { label: "오브젝트 크기·위치 정리", href: "reports/objects_current.html" },
      { label: "처음 세운 전시 구조 계획", href: "reports/structure_plan_original.html" }
    ]
  }
];
