#!/bin/bash
# 더블클릭: 천장 카메라 감지 + 언리얼 게임 창을 한 번에 켬 (카메라 번호는 config.json). 끝나면 시연 기록이 열림.
cd "$(dirname "$0")/interaction" || exit 1
caffeinate -d python3 home_tracker.py "$@"
# 파이썬이 비정상 종료돼도 언리얼 게임 창이 남지 않게
pkill -f "UnrealEditor.*AICLASS_prototype1.uproject.*-game" 2>/dev/null
exit 0
