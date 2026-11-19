# 인수인계: 기말 'home' 전시 — 2026-11-19 저녁 기준 (새 Claude는 이 파일부터 읽고 시작)

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

---

## 0. 먼저 연결하기 (새 Claude가 맥에 접근하는 법)

1. **맥 폴더 연결**
   - Claude 데스크톱 앱에서 이 채팅의 + 메뉴 → **Add folder**로 아래 두 폴더를 연결해요.
     - `/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/home-exhibition` ← GitHub 저장소(홈페이지 + 인터랙션 코드)
     - `/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1` ← 언리얼 프로젝트 (위 폴더를 포함해요)
   - 연결되면 `device_bash`에서 `$HOME/mnt/home-exhibition`, `$HOME/mnt/AICLASS_prototype1`로 보여요.
   - device_bash는 리눅스 VM이에요. 맥 프로그램(파이썬 카메라, 언리얼)은 직접 실행하지 못해요.
2. **맥에 파일 쓰기**
   - Claude 작업 공간에서 만든 파일 → `/mnt/user-data/outputs/`에 저장 → `device_commit_files`로 맥 경로에 써요.
   - ⚠️ **같은 이름으로 다시 보내면 캐시 때문에 옛 파일이 써져요. 보낼 때마다 이름을 바꿔요** (예: ht17.py, ht18.py…).
   - 보낸 뒤 `sha1sum`으로 맥 쪽 파일을 확인해요. JPG는 메타데이터가 붙어서 해시가 달라지는데, 이건 정상이에요.
   - device_bash에서 `rm`은 막혀 있어요. 지울 파일은 `mv`로 옮겨요.
3. **언리얼 조작 (컴퓨터 사용)**
   - `computer_resolve_access(["com.epicgames.UnrealEditor"])` → `computer_request_access`
   - 언리얼 화면은 백그라운드 캡처가 안 돼서 **full control**이 필요해요.
   - **입력기가 한글이면 ⌘C·⌘V가 안 먹어요.** 작업 전에 `ctrl+space`로 영문으로 바꾸고, 끝나면 사용자에게 한글로 되돌리라고 알려요.
   - 언리얼 Python 실행: 콘솔(Cmd 칸)을 **Python**으로 바꾼 뒤 아래 도우미를 한 번 정의해요.
     `R=lambda n:exec(open('/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/Saved/'+n).read(),globals())`
     그 다음 `Saved/`에 스크립트를 보내고 `R('파일.py')`로 실행해요. 결과는 `Saved/*.txt`로 쓰게 해서 device_bash로 읽어요.
   - 긴 명령을 직접 타이핑하면 중간에 끊겨요. 항상 파일로 보내서 `R()`로 실행해요.
4. **홈페이지**: https://aiclaudehiggsfield3-dot.github.io/home-exhibition/ (GitHub Pages, Push 후 1~3분 뒤 반영)

---

## 1. 지금 상태 한 줄
CCTV(카메라) → Python 감지 → OSC → **언리얼 블루프린트**까지 한 바퀴가 돌아가요. 아이폰 카메라와 손으로 실물 테스트도 성공했어요.
**지금 하던 일: 소니 A7 IV를 USB 웹캠으로 연결하는 중** (연결 방법 안내까지 했고, 실제 연결·셋업은 아직이에요).

## 2. 확정된 설계 (11/18 노션 회의 반영)
| 요소 | 내용 |
|---|---|
| 흐름 | 지하철 칸 → 손잡이 잡으면 안내방송·"도착하겠습니다" 음악 → 정차 → 집으로 들어감 |
| 지하철 달리는 화면 | **희망사항** (확정 아님) |
| 집 문 열림 | 불 켜짐 + TV 영상 재생 + CCTV 녹화 시작, 문 닫히면 지하철 소리 끊김 |
| TV 영상 | **미정** (모닥불이 아닐 수도 있음) |
| 담요 / 리모컨 | 담요 → 모닥불 소리, 리모컨 → 채널 변경 |
| 소리 | **서지오 담당**. 시간이 지날수록 볼륨이 커짐 |
| 퇴장 | 출구 옆 화면에 QR + 동선 타임랩스 |
| 인터랙션 구현 | **언리얼 블루프린트 필수** (교수님 지시). 센서·QR·장비는 정지원 담당 |

## 3. 인터랙션 시스템 (정지원 작업분, 핵심)
```
카메라(아이폰/A7 IV) → home_tracker.py (Python·OpenCV = 눈)
   → OSC 127.0.0.1:8000 → 언리얼 레벨 블루프린트 (L_Current = 뇌)
   → 퇴장 시 QR 창 + r.html 결과 페이지(동선 애니메이션)
```
### 현실 ↔ 언리얼 매칭
- 언리얼 전시장은 **300 × 300cm**예요. 기차 X 0~120, 집 X 120~300이에요.
- **CCTV 바닥 좌표(cm) = 언리얼 X·Y**예요.
- 천장 카메라(EX_Cam_TopView) 화면은 오른쪽이 +X, 아래가 +Y예요.
- 구역 파일: `interaction/unreal_layout.json` (train · home · sofa · exit)
- 셋업 때 바닥 네 모서리(1 입구 쪽 왼쪽 위 · 2 출구 쪽 오른쪽 위 · 3 TV 쪽 오른쪽 아래 · 4 왼쪽 아래)만 찍어요. 셋업 화면에 미니맵이 떠요.

### Python 감지 규칙 (`interaction/home_tracker.py`)
- **입장**: 바닥 안 어디든 0.8초 이어서 보이면 입장이에요.
- **집 진입**: 집 구역에 0.4초 있으면 `/home/door`를 보내요.
- **소파**: 1.2초 머물면 앉음으로 봐요.
- **출구**: 3초 머물면 퇴장 → QR 창이 자동으로 떠요 (20초 또는 다음 입장 때까지).
- **다음 관객**: 퇴장 뒤 화면이 1초 비어야 받아요.
- **물건**: ArUco 마커로 인식해요 (1·3 담요, 2 리모컨, `markers_A4.pdf`). 실물 테스트는 아직이에요 (인쇄 필요).
- **위치점 모드**: `point_mode` = foot(사람 발) / tip / **finger(손 시연용, 현재 맥 설정)**
  - finger: 피부색만 남겨 그림자를 빼고 손끝을 찾아요.
  - tip_band 0.96, smooth_n 3, pos_send_s 0.1
- **OSC 신호**: `/home/enter id`, `/home/pos x y`, `/home/door`, `/home/sit 1|0`, `/home/touch 이름 횟수`, `/home/exit 머문초`, `/home/result url qr경로`
- 결과 저장: `interaction/results/` (visit_XXXX.json, qr_XXXX.png — git 제외)
- 맥 설정: `interaction/config.json` (git 제외). 백업: `results/config.backup_1119.json`
- 맥 Python은 3.9예요. 설치는 `pip3 install --default-timeout=200 --retries 10 -r requirements.txt`

### 자주 쓰는 명령 (맥 터미널, 한 줄씩)
```
cd "/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/home-exhibition/interaction"
python3 home_tracker.py --list-cameras
python3 home_tracker.py --layout unreal_layout.json
caffeinate -d python3 home_tracker.py --camera 번호 --setup
caffeinate -d python3 home_tracker.py --camera 번호
caffeinate -d python3 home_tracker.py --camera 번호 --save-raw results/test.mp4
```
- 끄기: ESC / 창 닫기 / Ctrl+C. 한글 입력 상태에서는 q가 안 먹어요.
- `--save-raw`로 원본 영상을 저장해 두면 Claude 쪽에서 같은 영상으로 다시 돌려 보며 고칠 수 있어요.
- 아이폰은 카메라 0, 맥북 웹캠은 1이었어요. A7 IV를 연결하면 번호가 바뀌니 `--list-cameras`로 확인해요.

### 언리얼 (UE 5.4, 프로젝트 AICLASS_prototype1, 시작 맵 **L_Current**)
- **OSC 플러그인**: 켜 둠.
- **레벨 블루프린트**: 백업 `interaction/unreal/L_Current_OSC.t3d`, 설명 `interaction/unreal/README.md`
  - 시작: 8000 포트 열기, 집 조명(EX_Light_B_Warm_1·2) 끔, 형체 숨김, 집 TV(EX_Screen_B_Home) 끔, **화면 2분할**(왼쪽 천장 CCTV / 오른쪽 관객 눈), 임시 음악 아주 작게 시작
  - pos: 형체(EX_Visitor)가 그 자리로 부드럽게 이동하고 그쪽을 바라봐요. 눈 카메라(EX_VisitorEye)가 붙어 따라가요.
  - door: 조명 켬 + TV 재생
  - sit: 음악 목표 볼륨 0.35 이상, touch: +0.2, 앉아 있는 동안 초당 +0.01
  - exit: 2초 뒤 **플레이 완전 종료** (다음 관객은 ▶ 다시)
  - 변수: OSCServer, MusicComp, TargetLoc, Active, Snap, Seated, TargetVol, Vol
- **추가한 것**
  - EX_Visitor (원기둥 실루엣) — StaticMeshActor_27
  - EX_VisitorEye — CineCameraActor_0
  - S_TempMusic (`Content/Exhibition/Audio`, 서지오 파일로 교체 예정)
  - DefaultEngine.ini: 2인 화면 세로 분할 (원본 백업 DefaultEngine.ini.bak2)
- **블루프린트 고치는 법**
  1. 그래프 전체 복사(우클릭 → 복사하기)
  2. 콘솔에서 `pbpaste > Saved/파일.t3d`로 저장 → 형식을 읽어요
  3. Python으로 새 t3d를 만들어요
  4. 콘솔에서 `LANG=en_US.UTF-8 pbcopy < Saved/새파일.t3d`
  5. 그래프에서 ⌘A → Delete → ⌘V
  6. 빨간 변수 노드는 노드 몸통을 우클릭 → "변수를 생성합니다"
  7. 컴파일 → 저장
  - 생성 스크립트는 지난 세션 컨테이너에만 있었어요. t3d 백업을 기준으로 다시 만들어요.
- **시험**: 플레이 중 Python 콘솔에서 UDP로 OSC를 직접 보내고 상태를 파일로 읽어요 (`Saved/p5.py`의 osc(), st()).
- 언리얼은 다른 창을 보고 있으면 느려질 수 있어요 → 에디터 개인설정 → "백그라운드에서 CPU 덜 사용" 해제.

## 4. 바로 다음 할 일 (순서대로)
1. **A7 IV 연결 마무리** (안내는 끝, 사용자가 진행 중)
   - 카메라: USB 연결 모드 = USB Streaming, 출력 HD 1080p 30p, **M 모드 · ISO · WB · MF 고정**(자동 노출이면 감지가 깨짐), 24mm
   - USB 3 케이블(USB 2면 720p로 떨어짐), 책상 위 수직 60~80cm
   - `--list-cameras`로 번호 확인 → `--setup`으로 네 모서리 → 언리얼 ▶ → 손 테스트
2. 손끝 추적 실물 재확인. 안 좋으면 `--save-raw`로 영상을 받아서 분석해요.
3. ArUco 마커 인쇄 → 담요·리모컨 인식 실물 테스트 → 언리얼에 담요=모닥불 소리, 리모컨=채널 변경 연결
4. 서지오 소리 파일을 받으면 S_TempMusic 교체 + 지하철 소리 / 문 닫히면 끊김 연결
5. 실제 전시용: TV 화면 무시 구역(움직이는 영상을 사람으로 착각하지 않게), 손잡이 감지 방법, 실제 공간 크기 측정, 천장 CCTV 화면에 동선 선 그리기
6. 크브페 지원서 제출 (11/23 월 23:59, transmediastudy@gmail.com, HWP+PDF) — 다른 팀원 진행 상황 확인

## 5. 진행 상황을 알 수 있는 파일
| 무엇 | 어디 |
|---|---|
| **전체 기록(날짜별 버전·작업)** | 홈페이지 `history.html` (07 전체 기록), 데이터 `data/history.js` (WORKLOG에 작업을 덧붙임, 버전은 GitHub에서 자동) |
| 홈페이지 목록 | `index.html` → 01 기획 의도 · 02 공간 소개 · 03 가구 정리 · 04 확정된 내용 · 05 직접 체험(3D) · 06 인터랙션·장비 · 07 전체 기록 |
| 인터랙션 설명·규칙·OSC 표 | `interaction/README.md` |
| 언리얼 쪽 설명 | `interaction/unreal/README.md` |
| 테스트 결과 사진 | `interaction/docs/` (sim_result_sheet, hand_tracking_after, finger_before_after) |
| 가상 시연 검증 | `interaction/sim_demo.py` (가상 영상 만들기), `sim_check.py` (채점) |
| 지난 기획(보관) | `archive/` (지금 설계 아님) |
| 언리얼 작업 스크립트·결과 | `AICLASS_prototype1/Saved/` (r*.py, p5.py, layout.json, *.txt) |
| GitHub 커밋 기록 | 마지막 사용자 커밋 ≈ ver13.2 ~ ver14 (`git log --oneline -5`로 확인) |

홈페이지 페이지는 지난 세션 컨테이너의 `split.py`로 만들었어요. 그 스크립트는 사라졌으니, 이제는 **HTML을 직접 고쳐요**. 전체 페이지에 공통인 nav는 각 파일 위쪽에 있어요.

## 6. 커밋할 때 주의
- `.DS_Store`가 목록에 보이면 체크를 빼요.
- `config.json`과 `results/`는 git 제외예요.
- 아직 커밋 안 됐을 수 있는 변경: ver14.1 (손끝 추적 finger 모드, finger_before_after.jpg, README, history.js). `git status`로 확인한 뒤 안내해요.

## 7. 사용량 아끼는 법
- 새 채팅은 이 파일만 읽고 시작해요.
- 큰 HTML이나 로그는 필요한 부분만 grep으로 봐요.
- 화면 캡처는 꼭 필요할 때만 찍어요.
- 안 쓰는 커넥터는 꺼요.
