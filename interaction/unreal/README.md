# 언리얼 레벨 블루프린트 (L_Current) — CCTV와 매칭

`L_Current_OSC.t3d` = 레벨 블루프린트 노드 백업 (텍스트). 망가졌을 때 되살리는 용도.
되살리기: 터미널 `LANG=en_US.UTF-8 pbcopy < L_Current_OSC.t3d` → 레벨 블루프린트 빈 곳 클릭 → **영문 입력 상태에서** ⌘V → 빨간 변수 노드 우클릭 "변수 생성" → 컴파일 → 저장

## 현실 ↔ 언리얼 매칭
- CCTV 바닥 좌표(cm) **= 언리얼 X·Y 좌표** (전시장 300 × 300cm, 왼쪽 위 모서리가 0,0)
- 천장 카메라(EX_Cam_TopView) 화면: 오른쪽 = +X, 아래 = +Y → CCTV 화면과 같은 방향
- 구역은 언리얼 도면에서 가져옴 → `../unreal_layout.json` (지하철 칸 Y 0~77 · 집 Y 77~300 · 소파 · 출구 — 11/19 홈페이지 배치로 다시 지음, 재건축 스크립트 `Saved/rb1119a.py`)

## 레벨에 추가한 것
| 이름 | 역할 |
|---|---|
| EX_Visitor | 관객 형체 (실루엣 원기둥, 높이 170cm) |
| EX_VisitorEye | 관객 1인칭 눈 카메라 — 몸 중심에서 **앞으로 30cm**(몸 밖) · 눈높이 160cm · 6° 아래 · 14mm · **화면 꽉 채움**(비율 고정 끔) · 이 카메라만 노출 보정 +1.5 (수동 노출, 물리 카메라 노출 끔 — 플레이 화면에서 맞춘 값). 미리보기 `docs/eyecam_1119.png` |
| S_TempMusic | 임시 음악 (서지오 파일 나오면 교체) — Content/Exhibition/Audio |
| S_TempFire · S_TempSubway · S_TempStatic | 임시 모닥불·지하철·채널 지지직 소리 (직접 합성, 원본 `temp_sounds/`) — 서지오 파일로 교체 |
| EX_Snd_Fire (AmbientSound_0) · EX_Snd_Subway (AmbientSound_1) | 소리 액터 (자동 재생 끔) — 블루프린트가 켜고 끔. Exhibition/Sound 폴더 |
| EX_QR_Screen (StaticMeshActor_116) | 출구 옆 QR 화면 — 머티리얼 M_QR (Tex 텍스처 × Show 밝기) |
| EX_Fan (StaticMeshActor_0) | 노란 반투명 시야 부채꼴 (SM_Fan 90cm·60°, M_Fan) — 관객 눈 카메라에 붙어 같이 돎. 천장 위 약 246cm라 천장 CCTV에만 보이고 관객 눈 화면에는 안 보임. 형체와 같이 숨김/보임 |
| EX_LookRef (TargetPoint_0) | 바라보는 방향 저장용 기준점 (보이지 않음, Movable) |
| PL_TV | TV 채널 목록 (0 B_home · 1 A_society) — MediaPlate가 이 목록을 씀 |
| 화면 나누기 | 왼쪽 = 천장 CCTV, 오른쪽 = 관객 눈 (DefaultEngine.ini: 2인 화면 세로 분할) |

## 블루프린트가 하는 일
| 신호 | 반응 |
|---|---|
| 시작 | 8000번 포트 열기 · 집 조명 끔 · 관객 형체 숨김 · 집 TV 끔 · 화면 둘로 나누기 · 음악 아주 작게 시작 |
| `/home/enter` | 관객 등장 준비 · QR 화면 끔 |
| `/home/pos x y` | 형체가 그 자리로 부드럽게 이동하고 가는 방향을 봄 (첫 위치면 바로 나타남) |
| `/home/door` | 집 구역에 들어섬 = 문 열고 들어옴 → **집 조명 켬 + TV 영상 재생 + 지하철 소리 3초에 걸쳐 잦아듦** |
| `/home/sit 1` | 음악 목표 볼륨 0.35 이상으로 |
| `/home/look 각도` | 보이지 않는 기준점 EX_LookRef(TargetPoint_0)의 방향을 바꿈 → 매 프레임 형체가 그 방향으로 부드럽게 돎 (눈 카메라·부채꼴도 같이) |
| `/home/train` | 지하철 소리 켬 (1초 페이드인) |
| `/home/touch blanket` | 음악 +0.2 · **모닥불 소리** 켬 (이미 나고 있으면 그대로) |
| `/home/touch remote` | 음악 +0.2 · **TV 채널 바꿈** (B_home ↔ A_society) + 지지직 소리 |
| 앉아 있는 동안 | 목표 볼륨이 초당 0.01씩 커짐, 실제 볼륨은 천천히 따라감 |
| `/home/exit` | 2초 뒤 **리셋**: 조명·형체 숨김, TV 끔, 볼륨 0, 모닥불·지하철 소리 끔 → 다음 관객을 플레이 중에 바로 받음 |
| `/home/result` | QR PNG를 텍스처로 읽어 **QR 화면에 표시** (다음 관객 `/home/enter` 때 꺼짐) |

## 블루프린트 고치는 법 (11/19)
- 그래프는 `gen_bp1119.py`가 만든다: `python3 gen_bp1119.py <Saved 폴더>` → `bp_v4.t3d`(11/19 17시 그래프) + 새 기능 = `bp_v5.t3d` (= 이 폴더의 `L_Current_OSC.t3d`).
- 새 변수는 없음 (소리는 AmbientSound 액터, QR은 그 자리에서 머티리얼 인스턴스 생성) → 붙여 넣고 **컴파일만** 하면 됨.
- 채널 바꾸기 주의: MediaPlate `Open()`은 항상 0번부터, 플레이어 `Next()`는 같은 영상만 다시 틂 → 플레이어의 `PlayOnOpen`을 켜고 `OpenPlaylistIndex(PL_TV, 지금이 A_society면 0 아니면 1)`.
