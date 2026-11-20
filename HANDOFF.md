# 인수인계: 기말 'home' 전시 — 2026-11-20 15:20 기준 (새 Claude는 이 파일부터 읽고 시작)

사용자: **정지원** (영상학과 25학번). 인터랙션 담당.
- 3인 팀: 정지원 · 서지오(사운드) · 최아원.
- 수업: 2026-2 AI 기반 영상 제작 워크샵 기말.
- 크리에이티브 브릿지 페스티벌(크브페) 지원작 「Home Sweet Home」.

**말투·진행 방식**
- **답변은 한국어로** 해요 (사용자가 명시적으로 요청함). 해요체. 이유를 먼저 설명하고 단계별로 진행해요.
- 오류는 바로 고치고, 가능하면 "알아서 끝까지" 진행해요. 다 하면 실제로 확인(플레이·VM 시험)까지 하고 결과를 말해요.
- 한자어는 漢字(음: 뜻) 형식으로 써요.
- **커밋을 안내할 때는 답변 맨 아래에 Summary(제목)와 Description(설명)을 복사하기 좋게 줘요.** 사용자가 "나중에 한 번에 커밋"이라고 하면 묶어서 줘요.
- 커밋과 푸시는 사용자가 GitHub Desktop에서 직접 해요.
- 터미널 명령은 **한 줄씩, 주석(#) 없이** 줘요. zsh가 `#`을 오류로 처리해요.
- 사용자는 짧게 말해요 ("다시 ㄱㄱ", "다시해바"). 맥락을 보고 바로 진행해요.

## ★ 다른 컴퓨터에서 이어 하는 경우 (11/20 추가)
- 언리얼 프로젝트(레벨·에셋)는 원래 저장소 밖이라 **`transfer/unreal_project_1120.zip`** 에 넣어 둠. 순서는 **`transfer/README.md`**: UE 5.4 설치 → zip 풀기 → 이 저장소를 `AICLASS_prototype1/` **안에** clone → `transfer/config.json`을 `interaction/config.json`으로 → pip 설치 → `시연시작.command`.
- 아래 내용에 나오는 `/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1` 은 **원래 맥 경로**. 다른 컴퓨터에서는 zip을 푼 곳으로 바꿔 읽어요. 새 Claude는 `get_device_info`로 연결된 폴더를 먼저 확인해요.
- 언리얼 콘솔 도우미는 경로 없는 버전을 써요: `R=lambda n:exec(open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())+n).read(),globals())` (zip의 `Saved/` 스크립트는 이 방식으로 고쳐 둠, 사본 `transfer/ue_scripts/`).
- 전체 정리·문제점·발전 방향: **`interaction/docs/정리_문제점_방향_1120.md`** (원본은 정지원 계정의 Claude 문서, 그림 포함).

## ★ 지금 바로 알아야 할 것 (11/20 15:20)
**11/20 상태**: ver14.8까지 커밋 완료(TV 채널 반복 고침). 그 뒤 작업 정리·문제점·발전 방향을 문서로 만듦 → 다음 단계는 **'실제 방에서 한 바퀴'** (실제 장치 출력 · 카메라 자리 · 실물 인식). 크브페 지원서 마감 11/23(월) 23:59. 자세히는 위 정리 파일의 '바로 다음 할 일'과 '팀이 정할 것'.

**실행**: Finder에서 `home-exhibition/시연시작.command` 더블클릭 → 언리얼 게임 창(왼쪽, 천장 CCTV | 관객 눈) + 시연 창(오른쪽)이 한 화면에 뜸 → 시연 창 클릭 → WASD·마우스(Q/E)·**C 소파 앉기**·3 TV·2 리모컨(다음 채널)·1 담요·0 퇴장 → ESC 두 번으로 끝 → 언리얼 닫힘 + `results/mouse/sessions/<날짜_시각>/시연기록.html` 자동으로 열림. 실제 카메라는 `카메라시연.command`(아직 카메라로 미시험).

**감독 모니터 = 언리얼 화면 왼쪽(천장 CCTV)** (사용자와 정리). 소리를 언리얼이 내니까 소리 계기판도 여기. Python 창은 '카메라가 사람을 잘 잡나' 보는 기술 확인용.
- 관리자 소리 계기판: Python `meter_lines()`(home_tracker.py)가 각 소리 단계 0~5(누적/`grow_s`를 5칸)와 **겹침 단계 0~5**((배율-1)/`overlap_gain`, CALM/MILD/UNCOMFORTABLE/UNPLEASANT)를 글자로 만들어 0.5초마다 `/home/meter` → 언리얼 PrintString(Key HOME_METER, 1.5초)로 화면 왼쪽 위에 덮어씀. ⚠️ 언리얼 OSC 글자는 한글(UTF-8)이 깨져서 **영어·ASCII만**. 정식 UMG 위젯은 Python으로 못 만들어 에디터에서 손으로 해야 함(필요하면 다음 작업).

**블루프린트 = bp_v10** (`Saved/gen_bp1119.py . AmbientSound_2` → `bp_v10.t3d`, 노드 137, 붙임·컴파일·저장·시뮬레이트 확인 11/20 00:05). 주요 반응: 문 = 지하철 2초 페이드아웃 · 앉음 = 조명 + 눈높이 115cm(-14°)/일어남 160cm · touch tv = TV 영상+TV 소리 · touch remote 횟수 = 채널(횟수 % PL_TV 5개, **그 채널만 반복**) · level = 세 소리 볼륨 · meter = 계기판.

**⚠️ 알려진 문제 (다음에 고칠 것)**
1. ~~TV 채널이 영상 끝나면 저절로 넘어감~~ → **11/20 고침**. 원인: 다음 번호로 넘기는 건 TV 판(MediaPlate 컴포넌트)이 자기 재생목록으로 직접 함. 해결: 판에 영상 1개짜리 `PL_NOW`를 물리고(`Saved/pl1120.py`, 레벨 저장됨), touch tv/리모컨 때 `PL_NOW.Replace(0, PL_TV.Get(번호))` → 판 `Open()`. 시험 `R('tv1120.py')` → `Saved/tv1120.txt` (CH1 18초 유지 → CH2 18초 유지 → CH3 18초 유지 확인). ⚠️ 플레이 중 Replace가 PL_NOW 에셋을 메모리에서 바꿔서 에디터가 'PL_NOW 저장할까요?'를 물을 수 있음 — 저장해도 무해(TV 켤 때 CH1로 되돌림).
2. 한 화면 분할은 1920×1080(DELL)에서만 확인. 맥북 레티나 화면에서는 언리얼 창 크기가 다르게 잡힐 수 있음 → `config.json`의 `unreal_game.layout:"manual"` + `res`/`pos`로 조절.
3. 원격 조작에서는 마우스로 몸 돌리기가 안 잡혀 E/Q로만 시험함 (실제 마우스는 사용자가 확인 필요).

**언리얼 조작 함정 (11/19 밤에 겪음)**
- 한글 입력기면 그래프에 **⌘V가 안 먹음** → 블루프린트 붙일 때만 `ctrl+space`로 영문, 끝나면 한글로 되돌림 (사용자는 평소 한영 전환 하지 말라고 함 — 붙일 때만 예외).
- 그래프는 **두 번 클릭** 후 ⌘A·Delete·⌘V. ⚠️ 두 번 클릭한 자리가 선(wire) 위면 경유점(Knot)이 생김 → 붙인 뒤 확인 복사는 그래프 왼쪽 빈 곳(450,500 부근) **한 번** 클릭. ⌘C·⌘Z도 한글 입력이면 안 먹음. 그래프 오른쪽 아래(1200,600 부근)는 안 보이는 Claude 창이 겹쳐 있어 키가 거기로 감 → 그래프 왼쪽(480,620) 클릭.
- 붙인 뒤 확인: `os.system('pbcopy < /dev/null')`로 클립보드 비우고 ⌘A⌘C → pbpaste → 노드 수·`bOrphanedPin`. 안 비우면 실패해도 원본이 남아 성공처럼 보임(실제로 빈 그래프가 저장된 적 있음).
- 컴파일·저장 `R('ue1119i.py')`. 에셋 저장은 `EditorAssetLibrary.save_asset(경로, only_if_is_dirty=False)` (`save_loaded_asset`은 조용히 실패한 적 있음).
- 블루프린트 창 앞으로: `unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])` (bp = `unreal.find_object(None,'/Game/Exhibition/Maps/L_Current.L_Current:PersistentLevel.L_Current')`).
- `editor_request_begin_play()`는 UE 5.4에 없음. 시험은 시뮬레이트 `editor_play_simulate()` 또는 `시연시작.command`를 콘솔에서 `subprocess.Popen(['/bin/bash', '.../시연시작.command'], start_new_session=True, stdout=파일)`로 켜서 확인.

<details><summary>11/19 22:50~23:50 작업 기록 (자세히)</summary>

### 22:50 작업
- 소리 세 갈래: Python `update_layers`(home_tracker.py)가 `/home/level 음악 TV 모닥불` 볼륨을 보냄 — tune `grow_s` 60 · `vol_base` · `vol_max` 1.2 · `overlap_gain` 0.8 · `tv_view_deg` 35. 담요 = 만진 뒤 앉아 있는 동안.
- 언리얼: bp_v7 (gen_bp1119.py `. AmbientSound_2`) 붙임·컴파일·저장 완료. EX_Snd_TV = AmbientSound_2 (S_TempTV). 지하철 페이드아웃 2초, 위치 12 · 방향 20 · 음악 1.5 따라가기. '백그라운드 CPU 덜 사용' 끔 (EditorPerProjectUserSettings.ini).
- 확인(시뮬레이트): train → 지하철 켬 / door 1초 뒤 아직 페이드 중, 3초 뒤 꺼짐 · TV 소리 켬 · level 값 그대로 적용 / blanket → 모닥불 / exit → 전부 끔.
- ⚠️ `editor_request_begin_play()`는 UE 5.4에 **없음**(아래 0-3의 옛 메모 틀림). Python 시험은 `unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate()` → 끝 `editor_request_end_play()`. 진짜 2분할 플레이는 사용자가 ▶ 클릭 (컴퓨터 사용으로 ▶ 누르면 Finder가 앞으로 와서 안 먹었음).
- 상태 확인: `R('p5.py');R('st1119b.py');st2('태그')` → `Saved/st1119b.txt` (지하철·TV·모닥불 재생·볼륨, 형체 위치·yaw). `R('pie1119.py');pie('태그')` → 플레이 중인지.
- 게임식 키: scancode로 읽음 + `stop_text_input` (한글 입력기 문제). 백업 `results/home_mouse.backup_1119e_keycode.py`.
- **11/19 23시 (bp_v7)**: 조명은 `/home/sit 1`, TV(영상+소리)는 `/home/touch tv`(TV 앞 55cm 0.8초 / 게임식 3번 키 / 리모컨 먼저 누르면 TV부터)로. 문은 지하철 2초 페이드아웃만. 지하철 임시 소리 새로(덜컥-덜컥 이음새 1.5초 주기 + 차체 울림 + 모터 + 끼익, 옛것 `Saved/backup_1119/S_TempSubway_old.wav`). 시뮬레이트로 확인 완료.
- 블루프린트 붙이기 팁: 블루프린트 창은 콘솔에서 `unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([bp])`로 앞으로 꺼냄(창 클릭하면 다른 앱이 앞으로 옴). 컴파일·저장은 `R('ue1119i.py')`.
- **11/19 23:10 한 번에 실행 + 시연 기록**: `시연시작.command`(더블클릭) = `python3 home_mouse.py` → 언리얼 `-game` 창 자동으로 켬(`interaction/unreal_game.py`) → 끝나면 닫고 `results/mouse/sessions/<날짜_시각>/시연기록.html` 열림(`interaction/session_record.py`). `카메라시연.command` = home_tracker. 옵션 `--no-unreal` `--no-record`. 맥 실험 통과(준비 7~8초). avc1 녹화는 세그폴트 → mp4v만.
- 시험할 때 주의: 예전에 켜 둔 home_mouse가 남아 있으면 같은 8000 포트로 위치를 보내 형체가 두 곳을 오감 → 옛 창은 ESC로 끄고 시험.
- **11/19 23:35 한 화면 분할 · C 앉기 · 테스트 채널 (bp_v8)**: 맥에서 시험 완료 — 1920×1080에서 언리얼 1114×626(왼쪽)·시연 창 806×523(오른쪽), C로 앉으면 눈높이 115cm에서 TV가 보임, 리모컨 CH1→CH2→CH3→B_home→A_society→CH1. 테스트 영상 `Content/Movies/TEST_CH1~3.mp4` (원본 `Saved/ch_src/`, 맥 `avconvert`로 H.264).
- ⚠️ 블루프린트 붙이기·에셋 저장 함정은 `interaction/unreal/README.md` "붙이기 함정" 참고 (한글 입력기면 ⌘V 안 먹음 · 두 번 클릭 · 클립보드 비우고 확인 · save_asset).
- ⚠️ pygame `_sdl2` Window.focus()는 맥에서 Bus error → 뺌. `.command`는 끝날 때 남은 언리얼 게임 창을 pkill.
- 관리자용 소리 크기·겹침 표시: 아직 안 함 (계획만 — 사용자에게 방식 선택 받기).
- 아직: 맥에서 사용자가 게임식 시연으로 직접 듣기 (볼륨·속도 피드백 → config tune 숫자만 바꾸면 됨).

</details>

---

## 0. 먼저 연결하기 (새 Claude가 맥에 접근하는 법)

1. **맥 폴더 연결**: `device_request_folder_access`로 아래 **한 폴더만** 요청해요 (저장소가 그 안에 있어요).
   - `/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1`
   - `device_bash`에서는 `$HOME/mnt/AICLASS_prototype1` (저장소는 `.../AICLASS_prototype1/home-exhibition`)로 보여요.
   - device_bash는 리눅스 VM이에요 (Python 3.10, numpy·cv2·PIL 있음, **YOLO·pygame·qrcode 없음**, 인터넷 막힘). 맥 프로그램(카메라·언리얼)은 직접 실행 못 해요.
2. **맥에 파일 쓰기**: device_bash에서 **바로 쓰거나 고쳐요** (heredoc, `python3`로 읽고-고치고-쓰기). 고치기 전에 `interaction/results/`나 `Saved/backup_1119/`에 백업해요.
   - ⚠️ 클라우드 쪽에서 `device_commit_files`로 보낸 파일이 **VM에서는 옛 내용으로 보이는 일**이 있었어요. 긴 파일은 `gzip | base64`로 만들어 device_bash heredoc에서 `base64 -d | gunzip`으로 쓰고 md5로 확인해요.
   - device_bash에서 `rm`은 막혀 있어요. 지울 파일은 `mv`로 `_to_delete/`에 옮겨요.
   - ⚠️ 감지 프로그램을 VM에서 시험하면(`--video`) **results/에 가짜 visit 기록이 생기고 counter.txt가 올라가요.** 시험 뒤 `_to_delete/`로 옮기고 counter를 되돌려요 (지금 counter = 16).
3. **언리얼 조작 (컴퓨터 사용)** — 11/19에 겪은 함정 정리
   - `computer_resolve_access(["com.epicgames.UnrealEditor"])` → `computer_request_access` → `computer_request_full_control`.
   - **언리얼은 백그라운드 클릭·타이핑을 안 받아요** (자체 UI). `computer_app_screenshot`으로 보기는 되지만, 조작은 **전체 화면 제어**로만 돼요.
   - **스테이지 매니저가 켜져 있으면 전체 화면 캡처가 까맣게 나와요** → 사용자에게 제어 센터에서 꺼 달라고 해요 (11/19 끔).
   - HDMI 외장 모니터를 뺐을 때 언리얼이 확대된 채 입력을 못 받았어요 → **언리얼 재시작**으로 해결. 지금은 노트북 화면만 씀.
   - Claude 앱이 맨 앞이면 `computer_open_application`으로 언리얼을 못 꺼내요 → 사용자에게 **Dock에서 언리얼 클릭**을 부탁해요.
   - 입력기: 사용자는 **한영 전환 하지 말라**고 함 (콘솔 타이핑은 한글 상태에서도 됨). 단 블루프린트 그래프 ⌘V는 한글이면 안 먹어서 **붙일 때만** `ctrl+space`로 영문 → 끝나면 한글로 되돌림.
   - 메인 에디터 창이 화면에 꽉 찼을 때(1372×891 기준): 하단 Python 콘솔 입력 ≈ (430, 862), ▶ ≈ (410, 102). 레벨 블루프린트 창은 따로 뜨고 자기 콘솔이 있어요(창 위치 따라 다름 — 스크린샷으로 확인).
   - 에디터를 다시 켰으면 콘솔에서 도우미를 다시 정의해요:
     `R=lambda n:exec(open('/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/Saved/'+n).read(),globals())`
   - 스크립트는 `Saved/`에 쓰고 `R('파일.py')`로 실행, 결과는 `Saved/*.txt`로 써서 device_bash로 읽어요. 새 이름을 써요(ue1119f.py…).
   - 플레이: ~~editor_request_begin_play~~ (5.4에 없음). 시험은 `editor_play_simulate()` / `editor_request_end_play()` 또는 `시연시작.command`를 콘솔 subprocess로 켜기(위 ★). 저장: `unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)`.
   - OSC 시험(플레이 중): `R('p5.py');osc('/home/enter',1);osc('/home/pos',150.0,150.0);osc('/home/door');osc('/home/look',180.0)`
   - 상태 확인(플레이 중): `R('st1119.py');st('태그')` → `Saved/st1119.txt` (소리·TV·QR·조명·형체). ⚠️ 다른 스크립트가 전역 `OUT`을 바꾸면 그 파일로 써져요.
   - 끝나면 `computer_release_full_control`.
4. **홈페이지**: https://aiclaudehiggsfield3-dot.github.io/home-exhibition/ (GitHub Pages, Push 후 1~3분 뒤 반영)

---

## 1. 지금 상태
- 카메라 → Python 감지(**YOLO 사람 형체 인식**) → OSC → 언리얼 블루프린트까지 실제 방에서 한 바퀴 돌아가요 (A7 IV 삼각대, visit 12·14).
- **11/19 저녁 작업 (전부 언리얼 ▶ 플레이로 확인)**
  - 퇴장 = **리셋**(플레이 계속, 다음 관객 바로), 담요 = 모닥불 소리, 리모컨 = TV 채널(B_home↔A_society)+지지직, 지하철 칸 = 지하철 소리 → 문 지나면 **3초에 걸쳐 잦아듦**, 퇴장 QR을 언리얼 QR 화면에 표시.
  - **관객 1인칭 눈 화면(오른쪽)** 다시: 몸 앞 30cm·눈높이 160cm, 반쪽 화면 꽉 채움, 밝기 +1.5.
  - **바라보는 방향**: Python이 `/home/look 각도`를 보내고, 언리얼 형체가 그 방향으로 돌며 **노란 시야 부채꼴**이 천장 CCTV(왼쪽 화면)에 보여요.
  - **게임식 시연** `home_mouse.py`: 카메라 없이 WASD로 걷고 마우스로 시야를 돌려 같은 OSC를 보냄 (pygame). 손잡이는 **일단 없음**(사용자 결정).
- ⚠️ 아직 실제로 안 돌려 본 것: ① 게임식 시연을 **맥에서 진짜 pygame으로** (VM에서는 가짜 pygame으로만 시험 통과) ② YOLO 자세 인식(어깨로 방향)을 **실제 카메라로**.

## 2. 확정된 설계 (11/18 노션 회의 + 홈페이지 02 공간 소개)
| 요소 | 내용 |
|---|---|
| 공간 | 3×3m. **위쪽 지하철 칸(안쪽 폭 70, 천장 215) / 가벽(문 80, X 190~270, 집 쪽으로 열림) / 아래쪽 집(300×220, 벽 240)** |
| 흐름 | 지하철 칸 → (손잡이·안내방송은 **보류**) → 문 열고 집으로 → 출구(아래쪽 벽 X 10~90) |
| 지하철 달리는 화면 | **희망사항** (확정 아님) |
| 집 문 열림 | 불(3500K 스탠드 2개) 켜짐 + TV 영상 재생 + 지하철 소리 잦아듦 |
| 집 가구 | 브라운관 TV+TV장(왼쪽 벽, 오른쪽을 봄) · 작은 소파 101×67(오른쪽, TV를 봄) · 담요 · 리모컨 · 러그 · 스탠드 2 · 선반 · 화분 |
| TV 영상 | **미정** (지금은 B_home / A_society 임시) |
| 담요 / 리모컨 | 담요 → 모닥불 소리, 리모컨 → 채널 변경 |
| 소리 | **서지오 담당**. 머물수록 소리 볼륨이 커짐 (지금은 임시 합성 소리) |
| 퇴장 | 출구 옆 화면에 QR + 동선 타임랩스 |
| 인터랙션 구현 | **언리얼 블루프린트 필수** (교수님 지시). 센서·QR·장비는 정지원 담당 |

배치 기준 치수는 **`experience.html`** (단위 m, x 왼→오, z 지하철(0)→집(3)). 언리얼 X = x×100, Y = z×100.

## 3. 인터랙션 시스템
```
카메라(아이폰 예정 / A7 IV) → home_tracker.py (Python·OpenCV·YOLO = 눈)
   또는 카메라 없이 → home_mouse.py (게임식 시연, 같은 규칙)
   → OSC 127.0.0.1:8000 → 언리얼 레벨 블루프린트 (L_Current = 뇌)
   → 퇴장 시 QR (언리얼 QR 화면 + Python 창) + r.html 결과 페이지(동선 애니메이션)
```
### OSC 신호 (Python → 언리얼)
| 주소 | 값 | 언리얼 반응 |
|---|---|---|
| `/home/enter` | 관객 번호 | 등장 준비, QR 화면 끔 |
| `/home/pos` | x, y (cm) — 0.1초마다 | 형체가 부드럽게 이동 |
| `/home/look` | 각도(도) — pos와 함께 | 형체·눈 카메라·시야 부채꼴이 그 방향으로 돎 (0=+X 오른쪽, 90=+Y 집 쪽, 180=왼쪽, -90=지하철 쪽) |
| `/home/train` | 없음 | 지하철 소리 1초 페이드인 (관객당 한 번, 문 지나기 전만) |
| `/home/door` | 없음 | 지하철 소리 2초 페이드아웃 (조명·TV는 여기서 안 켬) |
| `/home/sit` | 1 / 0 | 1: 집 조명 켬 + 눈높이 115cm / 0: 눈높이 160cm |
| `/home/touch` | 이름(blanket·remote·tv), 횟수 | blanket → 모닥불, remote → 채널(횟수 % 5)+지지직, tv → TV 영상+TV 소리 |
| `/home/level` | 음악·TV·모닥불 볼륨 | 세 소리 볼륨 적용 (0.25초마다) |
| `/home/meter` | 글자 | 관리자 계기판 (화면 왼쪽 위, 0.5초마다) |
| `/home/exit` | 머문 초 | 2초 뒤 리셋 (조명·형체·부채꼴 숨김, TV 끔, 볼륨 0, 소리 끔) |
| `/home/result` | 주소, QR 경로 | QR PNG(RGB)를 읽어 EX_QR_Screen에 표시 |

### 현실 ↔ 언리얼 매칭
- 전시장 **300 × 300cm**. CCTV 바닥 좌표(cm) = 언리얼 X·Y. 천장 카메라(EX_Cam_TopView) 화면은 오른쪽 +X, 아래 +Y.
- 구역 (`interaction/unreal_layout.json` → config): train Y 0~77 / home Y 77~300 / sofa X 190~275, Y 155~275 / exit X 5~95, Y 255~300. 도면 정보(`unreal`): 입구 X0 Y0~72, 문 X190~270 Y77, 출구 틈 X10~90 Y300, TV (71,186), 스탠드 (48,94)·(282,286).
- **셋업 네 모서리**: 1 왼쪽 위(지하철 입구 쪽) · 2 오른쪽 위(지하철 칸 끝) · 3 오른쪽 아래(소파 뒤 스탠드) · 4 왼쪽 아래(출구 쪽). 자동 정렬(x+y 기준)이라 **카메라 화면 위쪽에 지하철 칸**이 와야 해요.
- ⚠️ 지금 config의 `floor_px`는 A7 삼각대 때 값 → **카메라를 바꾸면 `--setup` 다시**.

### Python 감지 (`interaction/home_tracker.py`)
- **사람 감지**: `person_detector` = **yolo**(`yolov8n-seg.pt`, git 제외) / bg. ultralytics가 없으면 bg로 자동 전환. 맥은 mps.
- **위치점**: `point_mode` = **foot**(현재) / finger / tip / center. `nadir_px = [960, 3240]`(비스듬히 찍을 때). 천장 수직이면 `null`.
- **바라보는 방향 (11/19 새로)**: `facing_mode` = **auto**(YOLO 자세 인식 `yolov8n-pose.pt` — 첫 실행 때 자동 다운로드 — 로 왼·오른 어깨 → 어깨선에 수직인 앞 / 어깨가 안 잡히면 걷는 방향 / 멈추면 마지막 방향) · pose · motion · off. `pose_every` 3, `pose_kp_conf` 0.4, `facing_min_cms` 15, `facing_alpha` 0.35. CCTV 창에 노란 부채꼴(`fan_deg` 60, `fan_cm` 90)과 각도·출처 표시. 함수 `update_facing`, `pose_yaw`, 모듈 함수 `fan_poly`.
- **규칙**: 입장 0.8초 · 지하철 칸 → `/home/train` · 집 구역 0.4초 → `/home/door` · 소파 1.2초 · 출구 3초 → 퇴장(QR) · 다음 관객(화면 1초 비어야).
- **QR**: `save_qr`가 **RGB PNG**로 저장 (1비트 흑백이면 언리얼에서 빨갛게 보였음).
- **물건**: ArUco 마커(1·3 담요, 2 리모컨, `markers_A4.pdf`). 실물 테스트 아직(인쇄 필요).
- 끄기: ESC 가장 안전. 결과: `interaction/results/` (git 제외, visit 16까지). 설정 `interaction/config.json` (git 제외). 코드 백업 `results/home_tracker.backup_1119b.py`(train 추가 전), `backup_1119c.py`(방향 추가 전).

### 카메라 없이: 게임식 시연 (`interaction/home_mouse.py`, pygame)
```
pip3 install pygame
python3 home_mouse.py
```
- 창 클릭/스페이스 = 지하철 입구에서 관객 등장(마우스가 창에 잡힘) · **1인칭 이동**: W/S(↑↓) 보는 방향으로 앞뒤 · A/D 옆걸음, Shift 빨리 · **마우스 좌우·←/→·Q/E = 몸 돌리기** (11/19 22시 화면 기준 → 1인칭 기준으로 바꿈, 백업 `results/home_mouse.backup_1119d_screenwasd.py`) · 1 담요 · 2 리모컨 · 0 강제 퇴장 · 9 동선 지우기 · ESC 마우스 풀기 → 한 번 더 끝.
- 키보드 자리(scancode)로 읽어서 한글 입력 상태에서도 됨. 가벽은 문으로만 통과(`Walker` 클래스), 입구·출구 틈으로 나가면 화면 밖. QR은 창 오른쪽에 20초.
- 판단은 `MouseTracker(ht.Tracker)` — person_detect만 조작 위치로 바꿈, 방향은 `facing_manual`. 기록은 `results/mouse/` (따로 counter).
- VM 시험법: `~/gtest/stub/pygame`(가짜 pygame, 대본으로 키·마우스 입력 + 화면 저장)과 `~/gtest/run.py`. VM 세션이 바뀌면 사라지니 필요하면 다시 만들어요.
- 예전 OpenCV 마우스판 백업: `results/home_mouse.backup_1119_opencv.py`.

### 맥 Python 환경 (3.9)
- 기본: `pip3 install --default-timeout=200 --retries 10 -r requirements.txt`
- YOLO: `pip3 install --default-timeout=200 --retries 10 -r requirements_yolo.txt` (**설치 완료**: ultralytics 8.4.215, torch 2.8)
- ultralytics 때문에 **opencv-python 4.11.0.86, numpy 1.26.4**로 맞춰져 있어요. 함부로 올리지 말아요.
- pygame 2.6.1 설치돼 있음 (맥 /usr/bin/python3 3.9.6).

### 자주 쓰는 명령 (맥 터미널, 한 줄씩)
```
cd "/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/home-exhibition/interaction"
python3 home_tracker.py --list-cameras
caffeinate -d python3 home_tracker.py --camera 번호 --setup
caffeinate -d python3 home_tracker.py --camera 번호 --save-raw results/이름.mp4
python3 home_mouse.py
python3 home_mouse.py --no-unreal
```
- 카메라 번호: config는 1(A7 IV). 아이폰은 예전에 0. `--list-cameras`로 확인. 시험할 때는 항상 `--save-raw`.

### 카메라 메모
- 다음은 **아이폰(연속성 카메라)** 을 천장에. 1배 렌즈 ≈ 26mm.
- ⚠️ **출구 쪽(아래쪽) 벽 가운데 천장에서 지하철 쪽을 45~60° 내려다보게** 추천 (화면 위쪽 = 지하철 칸, 바닥이 사다리꼴). 입구 쪽 모서리에 달면 위아래가 뒤집히고 대각선이면 자동 정렬이 틀릴 수 있음 → 그렇게 달려면 화면 180° 회전 + 찍은 순서대로 쓰는 셋업 옵션을 코드에 넣어야 함.
- 완전 수직은 YOLO 인식·자세 인식이 떨어질 수 있음 (정수리만 보임).
- A7 IV: USB Streaming, 1080p 30p, M 모드(1/60)·ISO·WB·MF 고정, 자동 전원 끄기 "높음", USB 3 케이블.

### 언리얼 (UE 5.4, 프로젝트 AICLASS_prototype1, 시작 맵 **L_Current**)
- L_Current는 11/19 20:30에 홈페이지 배치로 재건축 (`Saved/rb1119a.py`, 원본 백업 `Saved/backup_1119/L_Current_before_rebuild.umap`). 눈 카메라 고치기 전 백업 `Saved/backup_1119/L_Current_before_eyecam.umap`.
- **블루프린트가 가리키는 액터** (이름 바꾸거나 지우면 안 됨)
  | 액터(내부 이름) | 라벨 | 역할 |
  |---|---|---|
  | PointLight_1 · _2 | EX_Light_B_Warm_1 · _2 | 집 스탠드 (48,94)·(282,286), 3500K |
  | MediaPlate_1 | EX_Screen_B_Home | 브라운관 TV. 판이 트는 목록 = **PL_NOW(영상 1개)**, 채널 원본 = PL_TV (0~2 TEST_CH1~3, 3 B_home, 4 A_society) |
  | AmbientSound_2 | EX_Snd_TV | TV 소리 (S_TempTV, TV 자리) |
  | StaticMeshActor_27 | EX_Visitor | 관객 형체 (원기둥, 스케일 0.45·0.45·1.7) |
  | CineCameraActor_0 | EX_VisitorEye | 관객 1인칭 눈 — 형체에 붙음, 몸 앞 30cm·160cm·6° 아래·14mm·비율 고정 끔·**수동 노출 +1.5** |
  | CineCameraActor_1 | EX_Cam_TopView | 천장 CCTV (150,150,900) |
  | AmbientSound_0 · _1 | EX_Snd_Fire · EX_Snd_Subway | 모닥불·지하철 소리 (자동 재생 끔) |
  | StaticMeshActor_116 | EX_QR_Screen | 출구 옆 QR 화면 (M_QR: Tex × Show) |
  | TargetPoint_0 | EX_LookRef | 바라보는 방향 저장용 기준점 (Movable, 안 보임) |
  | StaticMeshActor_0 | EX_Fan | 노란 시야 부채꼴 (SM_Fan 90cm·60°, M_Fan 반투명) — 눈 카메라에 붙음, 천장 위 약 246cm라 **천장 CCTV에만** 보임 |
- ⚠️ **노출 값 주의**: 플레이 화면에서는 값이 **클수록 밝아요**. 미리보기 캡처(`Saved/cap1119.py` → `Saved/eyecam/`)는 반대로 나와서 참고만.
- **레벨 블루프린트**: 백업 `interaction/unreal/L_Current_OSC.t3d`(= `Saved/bp_v5.t3d`, 128노드), 설명 `interaction/unreal/README.md`
  - 시작: 8000 포트, 집 조명 끔, 형체 숨김, TV 끔, 화면 2분할(왼쪽 천장 CCTV / 오른쪽 관객 눈), 임시 음악 아주 작게
  - Tick: Active일 때 형체가 TargetLoc로 이동, **회전은 EX_LookRef 방향으로**(RInterp 5), 앉아 있으면 볼륨 증가
  - 변수: OSCServer, MusicComp, TargetLoc, Active, Snap, Seated, TargetVol, Vol (**새 변수는 안 만듦** — 상태는 액터에 저장)
- **블루프린트 고치는 법 (11/19 방식)**
  1. 생성기 `Saved/gen_bp1119.py`(= `interaction/unreal/gen_bp1119.py`)를 고쳐요. 바탕은 `Saved/bp_v4.t3d`(11/19 17시 원본 그래프) — 여기에 기능을 더해 `bp_v5.t3d`를 만들어요. 함수 `fn` · `literal` · `comp_get` · `self_set` · `link` · `unlink` · `remove`. 핀은 연결·기본값 있는 것만 적으면 언리얼이 나머지를 채워요.
  2. VM에서 `python3 gen_bp1119.py .` (Saved 폴더에서) → "bad links 0" 확인.
  3. 언리얼 레벨 블루프린트 창 콘솔: `import os;os.system('cd "/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/Saved" && LANG=en_US.UTF-8 pbcopy < bp_v5.t3d')`
  4. 그래프 빈 곳 클릭 → ⌘A → Delete → ⌘V → **컴파일**(툴바의 "컴파일" 글자 버튼, 옆 아이콘은 콘텐츠 브라우저라 헷갈림) → "준비 완료" 확인 → 저장.
  5. 확인: 그래프 ⌘A ⌘C → `os.system('pbpaste > ".../Saved/bp_after_xxx.t3d"')` → VM에서 노드 수·`bOrphanedPin=True` 개수(0이어야) 확인.
  - 플레이 중에는 그래프가 읽기 전용이라 붙여넣기가 안 돼요 (먼저 플레이 끄기).
- 채널: `PL_NOW.Replace(0, PL_TV.Get(리모컨 횟수 % PL_TV.Num))` → 판 `Open()` (11/20). 실제 TV 영상이 정해지면 PL_TV 내용만 바꾸면 됨.
- 임시 소리 S_TempMusic · S_TempFire · S_TempSubway · S_TempStatic (`Content/Exhibition/Audio`, 원본 `interaction/unreal/temp_sounds/`) → 서지오 파일이 오면 같은 이름으로 교체.
- 새 에셋: M_QR, M_Fan (Materials), SM_Fan (Meshes, 원본 `interaction/unreal/SM_Fan.obj`), PL_TV (Media).
- DefaultEngine.ini: 2인 화면 세로 분할 (원본 DefaultEngine.ini.bak2). 에디터 개인설정 "백그라운드에서 CPU 덜 사용" 해제 권장. 언리얼 화면 녹화는 ⌘⇧5.

## 4. 바로 다음 할 일 (순서대로)
1. ~~TV 채널 자동 넘어감~~ (11/20 완료).
2. 사용자가 맥에서 직접 시연: 실제 마우스로 몸 돌리기, 지하철 새 소리, 소리 세 갈래 크기·속도(`grow_s` 60초 등) 피드백 → config `tune` 숫자만 바꾸면 됨.
3. **아이폰을 천장에 달기** → `--list-cameras` → `--setup` → `카메라시연.command`로 한 바퀴 (자세 인식 방향 부채꼴, 계기판도 확인).
4. ArUco 마커 인쇄 → 담요·리모컨 실물 테스트.
5. 서지오 소리 파일 받으면 임시 소리(S_TempMusic·Fire·Subway·TV·Static) 같은 이름으로 교체. 실제 TV 영상이 정해지면 PL_TV 교체.
6. (선택) 관리자 계기판을 정식 UMG 위젯으로 / 실제 소리 크기(dB) 측정 추가.
7. 실제 전시용: TV 화면 무시 구역, 실제 공간 크기 측정. 손잡이는 보류.
8. 크브페 지원서 제출 (**11/23 월 23:59**, transmediastudy@gmail.com, HWP+PDF) — 다른 팀원 진행 상황 확인.

## 5. 진행 상황을 알 수 있는 파일
| 무엇 | 어디 |
|---|---|
| **정리·문제점·발전 방향 (11/20)** | `interaction/docs/정리_문제점_방향_1120.md` |
| **다른 컴퓨터로 옮기기** | `transfer/README.md`, `transfer/unreal_project_1120.zip` |
| **전체 기록(날짜별 버전·작업)** | 홈페이지 `history.html`, 데이터 `data/history.js` (WORKLOG에 덧붙임, 마지막 11/19 22:05) |
| 홈페이지 목록 | `index.html` → 01 기획 의도 · 02 공간 소개 · 03 가구 정리 · 04 확정된 내용 · 05 직접 체험(`experience.html`) · 06 인터랙션·장비 · 07 전체 기록 |
| 인터랙션 설명·규칙·OSC 표·게임식 시연 | `interaction/README.md` |
| 언리얼 쪽 설명 | `interaction/unreal/README.md` |
| 테스트 결과 사진 | `interaction/docs/` (eyecam_1119.png 등) |
| 언리얼 작업 스크립트·결과·백업 | `AICLASS_prototype1/Saved/` (gen_bp1119.py, bp_v4/v5.t3d, ue1119a~e.py, cam1119b/c.py, cap1119.py, st1119.py, ev1119.py, p5.py, snd1119/, eyecam/, mouse_test/, backup_1119/) |
| GitHub 커밋 | 마지막 **ver14.8** (9a5e99e, 11/20 채널 고침). ver14.9 = 다른 컴퓨터용 transfer/ + 정리 문서 (사용자가 커밋 예정). `git log --oneline -5` |

## 6. 커밋할 때 주의
- (옛 메모) **ver14.6 때 커밋 목록**: HANDOFF.md, data/history.js, interaction/README.md, interaction/home_mouse.py(게임식), interaction/home_tracker.py(바라보는 방향), interaction/unreal/L_Current_OSC.t3d · README.md · gen_bp1119.py, 새 파일 interaction/unreal/SM_Fan.obj.
- 사용자가 줄 Summary/Description 예시:
  - Summary: `ver14.6: 바라보는 방향·시야 부채꼴 + 게임식 시연(WASD·마우스) · 지하철 소리 잦아들기`
- `.DS_Store`가 목록에 보이면 체크를 빼요. `config.json`, `results/`, `*.pt`는 git 제외. 언리얼 맵(.umap)·에셋은 저장소 밖이라 커밋 목록에 안 떠요.

## 7. 사용량 아끼는 법
- 새 채팅은 이 파일만 읽고 시작해요.
- 큰 HTML·로그·t3d는 필요한 부분만 grep/파이썬으로 요약해서 봐요.
- 화면 캡처는 꼭 필요할 때만, 축소(scale 0.4~0.6)해서 찍어요. 메뉴 막대 입력기 확인은 zoom으로 작게.
- 안 쓰는 커넥터는 꺼요.
