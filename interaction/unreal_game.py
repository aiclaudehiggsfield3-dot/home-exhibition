# -*- coding: utf-8 -*-
"""Python 시연 프로그램과 함께 언리얼을 '게임 창'(-game)으로 켜고 끈다.

- 에디터의 ▶ 를 누르지 않아도 L_Current가 바로 돌아간다 (화면 2분할·OSC 그대로).
- OSC 포트(8000)가 이미 쓰이고 있으면 (에디터에서 ▶ 플레이 중) 새로 켜지 않는다.
- 설정: config.json 의 "unreal_game" (없으면 기본값)
    {"app": 언리얼 실행 파일, "project": .uproject, "map": "/Game/Exhibition/Maps/L_Current",
     "res": [1280, 720], "pos": [0, 30], "ready_timeout_s": 240}
"""
import os
import socket
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_APPS = [
    "/Users/Shared/Epic Games/UE_5.4/Engine/Binaries/Mac/UnrealEditor.app/Contents/MacOS/UnrealEditor",
]
DEFAULT_PROJECT = HERE.parent.parent / "AICLASS_prototype1.uproject"   # interaction → home-exhibition → 프로젝트 폴더


def port_busy(port):
    """UDP 포트를 누가 쓰고 있으면 True (= 언리얼 OSC 서버가 열려 있음)."""
    for host in ("0.0.0.0", "127.0.0.1"):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.bind((host, port))
        except OSError:
            return True
        finally:
            s.close()
    return False


def find_app(U):
    if U.get("app") and Path(U["app"]).exists():
        return U["app"]
    for p in DEFAULT_APPS:
        if Path(p).exists():
            return p
    try:                                            # 맥: 설치된 UnrealEditor.app 찾기
        out = subprocess.run(["mdfind", "kMDItemCFBundleIdentifier == 'com.epicgames.UnrealEditor'"],
                             capture_output=True, text=True, timeout=10).stdout.split("\n")
        for app in out:
            exe = Path(app.strip()) / "Contents" / "MacOS" / "UnrealEditor"
            if app.strip().endswith("UnrealEditor.app") and exe.exists():
                return str(exe)
    except Exception:
        pass
    return None


class UnrealGame:
    def __init__(self, cfg, log=print, log_path=None):
        self.U = dict(cfg.get("unreal_game") or {})
        self.port = int(cfg["osc"]["port"])
        self.log, self.log_path = log, log_path
        self.p = None
        self.status = "꺼짐"

    def start(self):
        if port_busy(self.port):
            self.status = "이미 켜져 있음"
            self.log(f"언리얼: OSC {self.port}번 포트가 이미 열려 있어요 (에디터 ▶ 플레이 중?) → 새로 켜지 않고 그대로 써요")
            return False
        app = find_app(self.U)
        proj = Path(self.U.get("project") or DEFAULT_PROJECT)
        if not app or not proj.exists():
            self.status = "못 켬"
            self.log(f"언리얼: 실행 파일({app}) 또는 프로젝트({proj})를 못 찾았어요 → config.json의 unreal_game.app / project를 확인하세요")
            return False
        (w, h), (x, y) = self.U.get("res", [1280, 720]), self.U.get("pos", [0, 30])
        args = [app, str(proj), self.U.get("map", "/Game/Exhibition/Maps/L_Current"), "-game", "-windowed",
                f"-ResX={w}", f"-ResY={h}", f"-WinX={x}", f"-WinY={y}", "-nosplash",
                # 게임 창이 마우스를 붙잡지 않게 (pygame 창에서 마우스로 시야를 돌려야 해서)
                "-ini:Input:[/Script/Engine.InputSettings]:DefaultViewportMouseCaptureMode=NoCapture",
                "-ini:Input:[/Script/Engine.InputSettings]:DefaultViewportMouseLockMode=DoNotLock"]
        if self.log_path:
            args.append(f"-ABSLOG={self.log_path}")
        self.p = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        self.status = "켜는 중"
        self.log(f"언리얼: 게임 창으로 켜는 중 (pid {self.p.pid}) — 처음엔 30초~1분쯤 걸려요")
        return True

    def wait_ready(self, tick=None):
        """OSC 포트가 열릴 때까지 기다림. tick(남은초)는 창 갱신용. 준비되면 True."""
        if self.status == "이미 켜져 있음":
            return True
        if not self.p:
            return False
        t0, limit = time.monotonic(), float(self.U.get("ready_timeout_s", 240))
        while time.monotonic() - t0 < limit:
            if self.p.poll() is not None:
                self.status = "꺼짐"
                self.log(f"언리얼: 켜다가 꺼졌어요 (코드 {self.p.returncode}) — 로그: {self.log_path}")
                return False
            if port_busy(self.port):
                self.status = "준비됨"
                self.log(f"언리얼: 준비됨 ({time.monotonic() - t0:.0f}초)")
                return True
            if tick and tick(time.monotonic() - t0) is False:
                return False
            time.sleep(0.25)
        self.status = "시간 초과"
        self.log(f"언리얼: {limit:.0f}초 안에 준비되지 않았어요 — 그래도 시연은 계속해요")
        return False

    def stop(self):
        if self.p and self.p.poll() is None:
            self.log("언리얼: 게임 창 닫는 중")
            self.p.terminate()
            try:
                self.p.wait(15)
            except subprocess.TimeoutExpired:
                self.p.kill()
        self.p = None
