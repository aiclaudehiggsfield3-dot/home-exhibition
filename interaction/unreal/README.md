# 언리얼 레벨 블루프린트 (L_Current) — OSC 받기

`L_Current_OSC.t3d` = 레벨 블루프린트 노드를 텍스트로 저장한 것. 블루프린트가 망가졌을 때 되살리는 용도.

**되살리는 법:** 터미널에서 `LANG=en_US.UTF-8 pbcopy < L_Current_OSC.t3d` → 레벨 블루프린트 빈 곳 클릭 → (영문 입력 상태에서) ⌘V → 컴파일 → 저장

## 지금 하는 일 (ver 3단계)
| 받는 신호 | 언리얼 반응 |
|---|---|
| 게임 시작 | 8000번 포트 열기, 집 조명(EX_Light_B_Warm_1·2) 끔 |
| `/home/enter` | 집 조명 켬 + 화면에 표시 |
| `/home/exit` | 집 조명 끔 + 화면에 표시 |
| `/home/sit` `/home/touch` `/home/result` | 화면에 표시 (소리 연결 예정) |
| `/home/pos` | 아무것도 안 함 (1초에 5번 오는 위치 신호) |

시험: 플레이 중 Python 콘솔에서 신호를 직접 보내 확인 — 시작 OFF → enter 후 ON → exit 후 OFF.
