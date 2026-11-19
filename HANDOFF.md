# 인수인계: 기말 'home' 전시 — 2026-11-19 21:15 기준 (새 Claude는 이 파일부터 읽고 시작)

사용자: **정지원** (영상학과 25학번). 인터랙션 담당.
- 3인 팀: 정지원 · 서지오(사운드) · 최아원.
- 수업: 2026-2 AI 기반 영상 제작 워크샵 기말.
- 크리에이티브 브릿지 페스티벌(크브페) 지원작 「Home Sweet Home」.

**말투·진행 방식**
- 해요체를 써요. 이유를 먼저 설명하고 단계별로 진행해요.
- 오류는 바로 고치고, 가능하면 "알아서 끝까지" 진행해요.
- 한자어는 漢字(음: 뜻) 형식으로 써요.
- **커밋을 안내할 때는 매번 답변 맨 아래에 Summary(제목)와 Description(설명)을 복사하기 좋게 줘요.**
- 커밋과 푸시는 사용자가 GitHub Desktop에서 직접 해요.
- 터미널 명령은 **한 줄씩, 주석(#) 없이** 줘요. zsh가 `#`을 오류로 처리해요.
- 사용자는 짧게 말해요 ("다시 ㄱㄱ", "카메라 1번임"). 맥락을 보고 바로 진행해요.

---

## 0. 먼저 연결하기 (새 Claude가 맥에 접근하는 법)

1. **맥 폴더 연결**: `device_request_folder_access`로 아래 **한 폴더만** 요청하면 돼요 (저장소가 그 안에 있어요).
   - `/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1`
   - `device_bash`에서는 `$HOME/mnt/AICLASS_prototype1` (저장소는 `.../AICLASS_prototype1/home-exhibition`)로 보여요.
   - device_bash는 리눅스 VM이에요. 맥 프로그램(카메라·언리얼)은 직접 실행하지 못하고, 인터넷도 막혀 있어요 (pip 설치 불가).
2. **맥에 파일 쓰기**: device_bash에서 **바로 쓰거나 고치면** 돼요 (heredoc, `python3`로 읽고-고치고-쓰기). 고치기 전에 `results/`나 `Saved/backup_1119/`에 백업해요.
   - device_bash에서 `rm`은 막혀 있어요. 지울 파일은 `mv`로 `_to_delete/`에 옮겨요.
   - ⚠️ 감지 프로그램을 VM에서 시험하면(`--video`) **results/에 가짜 visit 기록이 생기고 counter.txt가 올라가요.** 시험 뒤 `_to_delete/`로 옮기고 counter를 되돌려요.
3. **언리얼 조작 (컴퓨터 사용)**
   - `computer_resolve_access(["com.epicgames.UnrealEditor"])` → `computer_request_access` → 언리얼 화면은 백그라운드 캡처가 안 돼서 `computer_request_full_control`이 필요해요. 30분 안 쓰면 권한이 만료돼요.
   - **입력기가 한글이면 타이핑이 깨져요.** 작업 전에 `ctrl+space`로 영문으로 바꾸고, 끝나면 사용자에게 한글로 되돌리라고 알려요.
   - 하단 콘솔은 이미 **Python** 모드예요 (좌표 약 (468, 863), 화면 1372×891 기준). 에디터를 다시 켰으면 도우미를 다시 정의해요.
     `R=lambda n:exec(open('/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/Saved/'+n).read(),globals())`
   - 스크립트는 `Saved/`에 쓰고 `R('파일.py')`로 실행해요. 결과는 `Saved/*.txt`로 쓰게 해서 device_bash로 읽어요. 같은 이름 재사용도 괜찮지만 헷갈리지 않게 새 이름(rb1119b.py…)을 써요.
   - ▶ 버튼 약 (451,103), ■ 정지 약 (502,103).
   - OSC 시험: 플레이 중 콘솔에 `R('p5.py');osc('/home/enter',1);osc('/home/pos',150.0,200.0);osc('/home/door')`
   - 끝나면 `computer_release_full_control`.
4. **홈페이지**: https://aiclaudehiggsfield3-dot.github.io/home-exhibition/ (GitHub Pages, Push 후 1~3분 뒤 반영)

---

## 1. 지금 상태 한 줄
카메라 → Python 감지(**YOLO 사람 형체 인식**) → OSC → 언리얼 블루프린트까지 실제 방에서 한 바퀴 돌아가요 (A7 IV + 삼각대, visit 12·14 성공: 소파 앉음 → 출구 3초 퇴장).
언리얼 L_Current는 **홈페이지 최신 배치(위 지하철 80 · 아래 집 220)로 다시 지었어요.**
**11/19 21시: 블루프린트 확장 완료** — 퇴장 = 리셋(플레이 계속), 담요=모닥불 소리, 리모컨=TV 채널, 지하철 칸=지하철 소리(문에서 끊김), 퇴장 QR을 언리얼 QR 화면에 표시. OSC 시험 통과.
**다음 할 일: A7 대신 아이폰을 달고(아래 카메라 메모의 ⚠️ 방향 주의), 셋업(네 모서리)을 새로 해서 시험해요.**

## 2. 확정된 설계 (11/18 노션 회의 + 홈페이지 02 공간 소개)
| 요소 | 내용 |
|---|---|
| 공간 | 3×3m. **위쪽 지하철 칸(안쪽 폭 70, 천장 215) / 가벽(문 80, X 190~270, 집 쪽으로 열림) / 아래쪽 집(300×220, 벽 240)** |
| 흐름 | 지하철 칸 → 손잡이 잡으면 안내방송·"도착하겠습니다" 음악 → 정차 → 문 열고 집으로 → 출구(아래쪽 벽 X 10~90) |
| 지하철 달리는 화면 | **희망사항** (확정 아님) |
| 집 문 열림 | 불(3500K 스탠드 2개) 켜짐 + TV 영상 재생 + CCTV 녹화 시작, 문 닫히면 지하철 소리 끊김 |
| 집 가구 | 브라운관 TV+TV장(왼쪽 벽, 오른쪽을 봄) · 작은 소파 101×67(오른쪽, TV를 봄) · 담요 · 리모컨 · 러그 · 스탠드 2 · 선반 · 화분 |
| TV 영상 | **미정** |
| 담요 / 리모컨 | 담요 → 모닥불 소리, 리모컨 → 채널 변경 |
| 소리 | **서지오 담당**. 머물수록 모든 소리 볼륨이 커짐 |
| 퇴장 | 출구 옆 화면에 QR + 동선 타임랩스 |
| 인터랙션 구현 | **언리얼 블루프린트 필수** (교수님 지시). 센서·QR·장비는 정지원 담당 |

배치의 기준 치수는 **`experience.html`** (3D 체험, 단위 m, x 왼→오, z 지하철(0)→집(3)) 이에요. 언리얼 X = x×100, 언리얼 Y = z×100.

## 3. 인터랙션 시스템
```
카메라(아이폰 예정 / A7 IV) → home_tracker.py (Python·OpenCV·YOLO = 눈)
   → OSC 127.0.0.1:8000 → 언리얼 레벨 블루프린트 (L_Current = 뇌)
   → 퇴장 시 QR 창 + r.html 결과 페이지(동선 애니메이션)
```
### 현실 ↔ 언리얼 매칭 (11/19 20:30 새 도면)
- 전시장 **300 × 300cm**. CCTV 바닥 좌표(cm) = 언리얼 X·Y. 천장 카메라(EX_Cam_TopView) 화면은 오른쪽 +X, 아래 +Y.
- 구역 (`interaction/unreal_layout.json` → config에 들어가 있음)
  - train: Y 0~77 전체 / home: Y 77~300 전체
  - sofa: X 190~275, Y 155~275 / exit: X 5~95, Y 255~300
- **셋업 네 모서리 (새 기준)**: 1 왼쪽 위(지하철 입구 쪽) · 2 오른쪽 위(지하철 칸 끝) · 3 오른쪽 아래(소파 뒤 스탠드) · 4 왼쪽 아래(출구 쪽). 화면 위치로 자동 정렬되니, **카메라 화면에서 지하철 칸이 위쪽에 오게** 달아요.
- ⚠️ 지금 config의 `floor_px`는 A7 삼각대 때 찍은 것 → **카메라를 바꾸면 `--setup` 다시**.

### Python 감지 (`interaction/home_tracker.py`)
- **사람 감지**: `person_detector` = **yolo**(현재) / bg(빈 방과 비교, 예전).
  - YOLO 분할 모델 `yolov8n-seg.pt`(interaction/ 안, git 제외)로 사람 윤곽만 마스크로 써요 → 그림자·가구·TV 화면은 사람이 아님. 소파에 가만히 있어도 안 사라짐.
  - ultralytics가 없으면 bg 방식으로 자동 전환. 맥은 mps(GPU)로 돌아요. 설정: yolo_conf 0.35, yolo_imgsz 640.
- **위치점**: `point_mode` = **foot**(현재) / finger(손 시연) / tip / center.
  - foot은 "nadir(카메라 바로 아래 점)에 가장 가까운 윤곽 끝 = 발". 지금 `nadir_px = [960, 3240]`(화면 아래 바깥) → **비스듬히 찍을 때용**: 윤곽의 가장 아래 끝이 발.
  - **천장에서 수직으로** 찍으면 `nadir_px`를 `null`로 바꿔요 (화면 가운데 = 바로 아래).
  - smooth_n 5, tip_band 0.85.
- **규칙**: 입장(바닥 안 0.8초) · 집 진입(집 구역 0.4초 → `/home/door`) · 소파(1.2초) · 출구(3초 → 퇴장, QR 창) · 다음 관객(화면 1초 비어야).
- **물건**: ArUco 마커(1·3 담요, 2 리모컨, `markers_A4.pdf`). 실물 테스트 아직(인쇄 필요).
- **OSC**: `/home/enter id`, `/home/pos x y`, `/home/door`, `/home/sit 1|0`, `/home/touch 이름 횟수`, `/home/exit 머문초`, `/home/result url qr경로`
- 카메라를 못 열면 `[진단]` 줄이 원인을 알려 줘요 (못 열림 / 화면 없음 / 새까만 화면).
- 터미널 창을 닫아도(SIGHUP) 영상·기록을 마무리하고 끝나요. 그래도 끌 때는 **ESC**가 제일 안전해요.
- 결과: `interaction/results/` (visit_XXXX.json, qr, 원본 영상 — git 제외). 지금 visit 16까지. `results/_to_delete/`는 시험 찌꺼기(사용자가 직접 지움).
- 설정: `interaction/config.json` (git 제외). 백업: `results/config.backup_1119.json`(아이폰 손 시연), `results/config.backup_finger_1119.json`, `Saved/backup_1119/config_before_rebuild.json`.

### 맥 Python 환경 (3.9)
- 기본: `pip3 install --default-timeout=200 --retries 10 -r requirements.txt`
- YOLO: `pip3 install --default-timeout=200 --retries 10 -r requirements_yolo.txt` (**설치 완료**: ultralytics 8.4.215, torch 2.8)
- ultralytics 설치 때문에 **opencv-python 5.1 → 4.11.0.86, numpy 2.0 → 1.26.4**로 바뀌었어요. 지금 코드는 이 버전에서 돌아가요. 함부로 올리지 말아요.

### 자주 쓰는 명령 (맥 터미널, 한 줄씩)
```
cd "/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/home-exhibition/interaction"
python3 home_tracker.py --list-cameras
caffeinate -d python3 home_tracker.py --camera 번호 --setup
caffeinate -d python3 home_tracker.py --camera 번호 --save-raw results/이름.mp4
```
- 카메라 번호: 지금 config는 1(A7 IV). 아이폰은 예전에 0이었어요. 연결 기기에 따라 바뀌니 `--list-cameras`로 확인.
- **시험할 때는 항상 `--save-raw`**를 붙여요. 그 영상으로 Claude가 `--video`로 다시 돌려 볼 수 있어요 (단, VM에는 YOLO가 없어서 VM 재생은 bg 방식이에요).
- 끄기: ESC / 창 닫기 / Ctrl+C. 한글 입력 상태에서는 q가 안 먹어요.
- 프로그램을 켤 때는 화면 밖으로 비켜 있어요 (bg 방식은 처음 화면을 배경으로 기억해요).

### 카메라 메모
- **다음은 아이폰(연속성 카메라)을 천장 모서리에** 달기로 했어요. 가볍고, 자동 전원 꺼짐·발열 걱정이 적어요. 1배 렌즈 ≈ 26mm.
- ⚠️ 셋업은 네 점을 화면 위치(x+y)로 자동 정렬해요 → **화면 위쪽에 지하철 칸**이 와야 하고, 모서리에서 대각선으로 찍어 바닥이 마름모로 보이면 정렬이 틀릴 수 있어요. 그래서 **출구 쪽(아래쪽) 벽 가운데 천장에서 지하철 쪽을 45~60° 내려다보게** 다는 걸 추천 (입구 쪽에 달려면 화면 180° 회전 옵션을 코드에 넣어야 함).
- (예전 메모) 추천 각도: 입구 쪽 천장 모서리에서 45~60° 아래로. 완전 수직(바로 위)은 YOLO가 정수리만 보여서 인식이 떨어질 수 있고, 2.4m 천장에서 26mm로는 3×3m가 다 안 들어와요 (≈2.4m만). 수직으로 갈 거면 먼저 10초 `--save-raw`로 찍어서 인식률을 확인해요.
- A7 IV를 쓸 때: USB Streaming, HD 1080p 30p, M 모드(셔터 1/60) · ISO · WB · MF 고정, 자동 전원 끄기 "높음", USB 3 케이블.

### 언리얼 (UE 5.4, 프로젝트 AICLASS_prototype1, 시작 맵 **L_Current**)
- **11/19 20:30에 L_Current를 홈페이지 배치로 다시 지었어요** — 스크립트 `Saved/rb1119a.py`, 결과 `Saved/rb1119a.txt`.
  - 원래 맵 백업: `Saved/backup_1119/L_Current_before_rebuild.umap` (되돌리려면 언리얼을 끄고 `Content/Exhibition/Maps/L_Current.umap`에 덮어써요).
  - 다시 짓는 방식: 이름이 `EX_`로 시작하는 액터를 지우고 새로 만들되, **블루프린트가 직접 가리키는 6개는 지우지 않고 옮기기만** 해요.
    - PointLight_1 = EX_Light_B_Warm_1 → 스탠드 (48, 94), 3500K
    - PointLight_2 = EX_Light_B_Warm_2 → 스탠드 (282, 286), 3500K
    - MediaPlate_1 = EX_Screen_B_Home → 브라운관 유리 (71, 186, z71), 오른쪽을 봄
    - StaticMeshActor_27 = EX_Visitor (형체) → 시작 (20, 36)
    - CineCameraActor_0 = EX_VisitorEye (형체에 붙어 있음)
    - CineCameraActor_1 = EX_Cam_TopView (150, 150, 900, 아래를 봄)
    - 그 밖에 EX_PostProcess · EX_PlayerStart · EX_WalkCam도 지킴.
  - 새 액터: 바닥·벽·가벽·천장(아래를 보는 한 면 판 → 천장 CCTV에서 투명), 지하철 소품, 집 가구, QR_Screen, CCTV_Dome, 지하철 조명 2, 카메라(Cam_A_Subway · Cam_B_Door · Cam_B_OverSofa). 폴더 Exhibition/Structure · Subway · Home.
  - 확인: ▶ 플레이 → 왼쪽 천장 CCTV 화면에 위 지하철 / 아래 집. OSC 시험으로 조명 켜짐 + 형체 이동 확인.
- **다른 배치 레벨**: L_Opt1~5D, L_Opt5B(예전 본안, 홈페이지와 소파·TV·러그·스탠드가 조금 다름). 생성 스크립트 원본은 `Saved/build_layouts_bak_1116.py`(도우미 함수 참고용).
- **OSC 플러그인**: 켜 둠.
- **레벨 블루프린트**: 백업 `interaction/unreal/L_Current_OSC.t3d`, 설명 `interaction/unreal/README.md`
  - 시작: 8000 포트 열기, 집 조명 끔, 형체 숨김, 집 TV 끔, **화면 2분할**(왼쪽 천장 CCTV / 오른쪽 관객 눈), 임시 음악 아주 작게
  - pos: 형체가 그 자리로 부드럽게 이동하고 그쪽을 바라봄 (눈 카메라가 따라감)
  - train: 지하철 소리 페이드인 (EX_Snd_Subway) / door: 조명 켬 + TV 재생 + 지하철 소리 1.5초 페이드아웃
  - sit: 음악 목표 볼륨 ≥0.35 / touch: +0.2, **blanket → 모닥불(EX_Snd_Fire)**, **remote → 채널 B_home↔A_society(PL_TV) + 지지직** / 앉아 있는 동안 초당 +0.01
  - enter: QR 화면 끔 / result: QR PNG를 읽어 EX_QR_Screen(M_QR)에 표시
  - exit: 2초 뒤 **리셋** (조명·형체 숨김, TV 끔, 볼륨 0, 소리 끔) — 플레이는 계속, 다음 관객 바로 받음
  - 그래프 생성기: `interaction/unreal/gen_bp1119.py` (bp_v4 + 새 기능 → bp_v5 = `L_Current_OSC.t3d`). 새 변수 없음 → 붙여 넣고 컴파일만.
  - 채널 주의: MediaPlate `Open()`은 항상 0번부터, 플레이어 `Next()`는 같은 영상 재시작 → `PlayOnOpen` 켜고 `OpenPlaylistIndex`로 바꿈.
  - 상태 확인 스크립트: 플레이 중 `R('p5.py');R('st1119.py');st('태그')` → `Saved/st1119.txt` (소리·TV·QR·조명·형체)
  - 변수: OSCServer, MusicComp, TargetLoc, Active, Snap, Seated, TargetVol, Vol
- S_TempMusic · S_TempFire · S_TempSubway · S_TempStatic (`Content/Exhibition/Audio`, 임시 합성 소리, 원본 `interaction/unreal/temp_sounds/`) → 서지오 파일로 교체 예정. DefaultEngine.ini: 2인 화면 세로 분할 (원본 DefaultEngine.ini.bak2).
- **블루프린트 고치는 법**: 그래프 전체 복사 → 콘솔에서 `pbpaste > Saved/파일.t3d` → Python으로 새 t3d → `LANG=en_US.UTF-8 pbcopy < Saved/새파일.t3d` → 그래프 ⌘A Delete ⌘V → 빨간 변수 노드 우클릭 "변수를 생성합니다" → 컴파일 → 저장.
- 언리얼은 다른 창을 보고 있으면 느려질 수 있어요 → 에디터 개인설정 → "백그라운드에서 CPU 덜 사용" 해제.
- 언리얼은 영상을 녹화하지 않아요. 언리얼 화면도 남기려면 ⌘⇧5 화면 녹화.

## 4. 바로 다음 할 일 (순서대로)
1. **아이폰을 천장 모서리에 달기** → `--list-cameras` → `--setup`(새 네 모서리 기준) → 언리얼 ▶ → `--save-raw results/phone1.mp4`로 한 바퀴 (입구 → 집 → 소파 앉기 → 출구 3초).
   - 걷는 도중에 사용자가 "지금"이라고 하면 Claude가 언리얼 화면을 찍어서 형체가 따라오는지 확인하기로 했어요.
   - 끝나면 visit json + 영상으로 발 위치·구역 판정 확인. 수직 촬영이면 `nadir_px: null`.
2. ArUco 마커 인쇄 → 담요·리모컨 인식 실물 테스트 (언리얼 쪽 모닥불·채널은 11/19 연결 완료).
3. 서지오 소리 파일을 받으면 S_TempMusic 교체 + 지하철 소리 / 문 닫히면 끊김 연결.
4. 실제 전시용: TV 화면 무시 구역(YOLO라 덜 급함), 손잡이 감지 방법, 실제 공간 크기 측정, 천장 CCTV 화면에 동선 선 그리기. (퇴장 리셋은 11/19 완료)
5. 크브페 지원서 제출 (**11/23 월 23:59**, transmediastudy@gmail.com, HWP+PDF) — 다른 팀원 진행 상황 확인.

## 5. 진행 상황을 알 수 있는 파일
| 무엇 | 어디 |
|---|---|
| **전체 기록(날짜별 버전·작업)** | 홈페이지 `history.html`, 데이터 `data/history.js` (WORKLOG에 작업을 덧붙임, 마지막 11/19 20:30) |
| 홈페이지 목록 | `index.html` → 01 기획 의도 · 02 공간 소개(`space.html`) · 03 가구 정리(`furniture.html`) · 04 확정된 내용 · 05 직접 체험(`experience.html`, **배치 기준 치수**) · 06 인터랙션·장비 · 07 전체 기록 |
| 인터랙션 설명·규칙·OSC 표 | `interaction/README.md` |
| 언리얼 쪽 설명 | `interaction/unreal/README.md` |
| 테스트 결과 사진 | `interaction/docs/` |
| 가상 시연 검증 | `interaction/sim_demo.py`, `sim_check.py` |
| 실방 테스트 영상 | `interaction/results/a7_room2.mp4` (A7 삼각대, YOLO, 3222프레임 — 아직 분석 안 함) |
| 언리얼 작업 스크립트·결과·백업 | `AICLASS_prototype1/Saved/` (rb1119a.py, ue1119a~d.py, gen_bp1119.py, bp_v4/v5.t3d, st1119.py, p5.py, layout.json, backup_1119/) |
| GitHub 커밋 | 마지막 **ver14.2** (a78f332). `git log --oneline -5`로 확인 |

홈페이지 페이지는 **HTML을 직접 고쳐요**. 공통 nav는 각 파일 위쪽에 있어요.

## 6. 커밋할 때 주의
- `.DS_Store`가 목록에 보이면 체크를 빼요.
- `config.json`, `results/`, `*.pt`(YOLO 모델)는 git 제외예요.
- 언리얼 맵(.umap)은 저장소 밖이라 커밋 목록에 안 떠요.
- 이 HANDOFF.md 갱신은 아직 커밋 전이에요.

## 7. 사용량 아끼는 법
- 새 채팅은 이 파일만 읽고 시작해요.
- 큰 HTML이나 로그는 필요한 부분만 grep으로 봐요.
- 화면 캡처는 꼭 필요할 때만, 축소(scale 0.6~0.7)해서 찍어요.
- 안 쓰는 커넥터는 꺼요.
