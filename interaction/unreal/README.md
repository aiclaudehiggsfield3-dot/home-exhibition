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
| `/home/door` | 집 구역에 들어섬 = 문 열고 들어옴 → **지하철 소리 2초에 걸쳐 잦아듦** |
| `/home/sit 1` / `0` | 1: **집 조명 켬 + 관객 눈 카메라 높이 115cm·시선 -14°** (EX_VisitorEye 상대 위치 66.67, 0, 17.65) / 0: 눈높이 160cm·-6°로 되돌림 |
| `/home/touch tv` | **TV 영상 재생(F_TVOPEN) + TV 소리(EX_Snd_TV) 켬** |
| `/home/level 음악 TV 모닥불` | **소리 세 갈래 (11/19 22:40)**: 첫 값 → 음악 목표 볼륨(TargetVol, 1.5 속도로 따라감) · 둘째 → EX_Snd_TV 볼륨 · 셋째 → EX_Snd_Fire 볼륨. 계산은 Python이 함 |
| `/home/look 각도` | 보이지 않는 기준점 EX_LookRef(TargetPoint_0)의 방향을 바꿈 → 매 프레임 형체가 그 방향으로 부드럽게 돎 (눈 카메라·부채꼴도 같이) |
| `/home/train` | 지하철 소리 켬 (1초 페이드인) |
| `/home/touch blanket` | **모닥불 소리** 켬 (이미 나고 있으면 그대로) — 볼륨은 `/home/level` |
| `/home/meter 글자` | **관리자 계기판**: PrintString(Key HOME_METER, 1.5초)로 화면 왼쪽 위에 덮어씀. 신호 이름 디버그 글자는 이제 로그로만 |
| `/home/touch remote 횟수` | **채널 = 횟수 % PL_TV 채널 수** (TEST_CH1·2·3, B_home, A_society) + 지지직 |
| 반응 속도 | 형체 위치 따라가기 12 · 방향 따라가기 20 (예전 4·5) — 1인칭 고개가 바로 따라오게 |
| `/home/exit` | 2초 뒤 **리셋**: 조명·형체 숨김, TV 끔, 볼륨 0, 모닥불·지하철·TV 소리 끔 → 다음 관객을 플레이 중에 바로 받음 |
| `/home/result` | QR PNG를 텍스처로 읽어 **QR 화면에 표시** (다음 관객 `/home/enter` 때 꺼짐) |

## 블루프린트 고치는 법 (11/19)
- 그래프는 `gen_bp1119.py`가 만든다: `python3 gen_bp1119.py <Saved 폴더> <EX_Snd_TV 내부 이름>` → `bp_v4.t3d`(11/19 17시 그래프) + 새 기능 = `bp_v9.t3d` (= 이 폴더의 `L_Current_OSC.t3d`). (bp_v5 = 소리 세 갈래 전, bp_v6 = 조명·TV가 문에서 켜지던 판, bp_v7 = 앉기 눈높이·채널 돌리기 전)
- ⚠️ 붙이기 함정 (11/19): ① **입력기가 한글이면 Cmd+V가 그래프에 안 먹음** → 붙일 때만 영문. ② 그래프는 **두 번 클릭**한 뒤 ⌘A·Delete·⌘V (첫 클릭은 창 활성화). ③ 확인은 `os.system('pbcopy < /dev/null')`로 클립보드를 비운 뒤 ⌘A⌘C — 안 비우면 실패해도 원본이 남아 '성공'처럼 보임. ④ 에셋 저장은 `save_loaded_asset` 말고 `EditorAssetLibrary.save_asset(경로, only_if_is_dirty=False)` (PL_TV가 저장 안 돼 있었음).
- EX_Snd_TV(임시 소리 S_TempTV, TV 자리 71·186·90)는 `Saved/ue1119g.py`가 만든다 (에디터 '백그라운드에서 CPU 덜 사용'도 끔).
- 새 변수는 없음 (소리는 AmbientSound 액터, QR은 그 자리에서 머티리얼 인스턴스 생성) → 붙여 넣고 **컴파일만** 하면 됨.
- 채널 바꾸기 주의: MediaPlate `Open()`은 항상 0번부터, 플레이어 `Next()`는 같은 영상만 다시 틂 → 플레이어의 `PlayOnOpen`을 켜고 `OpenPlaylistIndex(PL_TV, 지금이 A_society면 0 아니면 1)`.
