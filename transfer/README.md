# 다른 컴퓨터에서 이어 하기 (11/20 기준)

저장소(home-exhibition)만으로는 언리얼 레벨·에셋이 없어서 이 폴더에 같이 넣어 둠.

| 파일 | 내용 |
|---|---|
| `unreal_project_1120.zip` | 언리얼 프로젝트 AICLASS_prototype1 (UE 5.4): `.uproject`, `Config/`, `Content/`(L_Current 레벨, PL_TV·PL_NOW, 임시 소리, 테스트 채널 영상), `Saved/`(언리얼 콘솔 도우미 스크립트 + 블루프린트 t3d) |
| `config.json` | `interaction/config.json` 사본 (git 제외 파일이라 여기 둠. 카메라 floor_px 등은 A7 삼각대 때 값) |
| `ue_scripts/` | zip의 `Saved/` 스크립트와 같은 것 — 경로를 `/Users/jiwon/...` 대신 **그 프로젝트의 Saved 폴더**로 자동으로 찾게 고침 |

## 순서
1. **언리얼 5.4** 설치 (Epic Games 런처).
2. `unreal_project_1120.zip`을 원하는 곳에 풀기 → `AICLASS_prototype1/` 폴더가 생김.
3. 이 저장소를 **그 폴더 안에** clone (GitHub Desktop → Clone → 위치를 `AICLASS_prototype1` 안으로). 결과: `AICLASS_prototype1/home-exhibition/`
   - `시연시작.command`가 `home-exhibition`의 한 칸 위에서 `.uproject`를 찾기 때문에 이 배치가 꼭 필요함.
4. `transfer/config.json`을 `interaction/config.json`으로 복사.
5. Python 패키지 (맥 터미널, 한 줄씩):
   ```
   cd 경로/AICLASS_prototype1/home-exhibition/interaction
   pip3 install --default-timeout=200 --retries 10 -r requirements.txt
   pip3 install pygame
   pip3 install --default-timeout=200 --retries 10 -r requirements_yolo.txt
   ```
   (YOLO는 카메라 시연에만 필요. `yolov8n-seg.pt`·`yolov8n-pose.pt`는 첫 실행 때 자동으로 받음)
6. `AICLASS_prototype1.uproject`를 열어 L_Current가 뜨는지 확인 (셰이더 컴파일로 처음엔 오래 걸림).
7. 언리얼 Python 콘솔 도우미 (경로 고정 없음):
   ```
   R=lambda n:exec(open(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir())+n).read(),globals())
   ```
   예: `R('ue1119i.py')` 컴파일·저장, `R('tv1120.py')` TV 채널 시험(결과 `Saved/tv1120.txt`).
8. 게임식 시연: Finder에서 `home-exhibition/시연시작.command` 더블클릭.

## 주의
- **맥 기준**이에요. 윈도우면 `.command` 대신 `python home_mouse.py`로 켜고, 언리얼 실행 파일 경로는 `config.json`의 `"unreal_game": {"app": "...UnrealEditor.exe"}`로 지정해야 해요(시험 안 해 봄).
- 화면 분할은 1920×1080에서만 확인. 다른 해상도면 `config.json`의 `unreal_game.layout:"manual"` + `res`/`pos`.
- 원래 맥의 `Saved/` 옛 스크립트(ue1119a~l 등)와 시연 기록(`interaction/results/`)은 안 옮겼어요. 필요하면 원래 맥에서 가져오기.
- 언리얼에서 레벨·에셋을 고치면 이 zip은 옛것이 됨 → 다시 옮길 땐 zip을 새로 만들어 커밋.
