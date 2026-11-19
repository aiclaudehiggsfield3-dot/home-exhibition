#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Home Sweet Home — 게임처럼 조작하는 관객 시연 (카메라 대신 쓰는 서브 프로그램)

카메라 없이 노트북에서 WASD로 걷고 마우스로 시야를 돌려, 언리얼에 카메라와 같은 OSC 신호를 보낸다.
판단 규칙(입장 0.8초 · 지하철 칸 · 문 0.4초 · 소파 1.2초 · 출구 3초 · QR)은 home_tracker.py의 Tracker 그대로.

조작 (키보드 자리로 읽어서 한글 입력 상태에서도 됨)
  스페이스 / 창 클릭   관객 등장 (지하철 입구에서) — 클릭하면 마우스가 창에 잡혀 시야 조작
  W A S D (방향키)     위 · 왼쪽 · 아래 · 오른쪽으로 걷기 (Shift = 빨리)
  마우스 좌우          바라보는 방향 돌리기 (시야 부채꼴)
  1 담요 만짐   2 리모컨 만짐   3 TV 만짐(켜기)   0 지금 강제 퇴장   9 동선 지우기
  ESC                  마우스 풀기 → 한 번 더 누르면 끝
  가벽은 문으로만 지나갈 수 있고, 출구 틈(아래 벽 왼쪽)으로 나가면 화면 밖과 같음.

  pip3 install pygame          (처음 한 번)
  python3 home_mouse.py         (기록·QR은 results/mouse/)
  python3 home_mouse.py --no-osc
"""
import argparse, os, sys, time, json
import faulthandler
faulthandler.enable()                                         # 비정상 종료(Segmentation fault) 때 어느 줄인지 남김
from pathlib import Path
import numpy as np
import cv2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import home_tracker as ht                                     # 같은 규칙·OSC·QR 사용
from unreal_game import UnrealGame                          # 언리얼을 게임 창으로 같이 켜고 끔
from session_record import SessionRecorder                  # 시연 기록 폴더 자동 저장

try:
    import pygame
except ImportError:
    sys.exit("pygame이 필요해요. 터미널에서 한 번만:  pip3 install pygame")

S, PAD, PANEL = 2.0, 34, 360          # 1cm = 2px, 바닥 둘레 여백, 오른쪽 안내판 폭
BODY = 15                             # 몸 반지름(cm) — 벽에 이만큼 못 붙음
WALK, RUN = 110.0, 200.0              # cm/초
SENS = 0.25                           # 마우스 1px당 몇 도 도는지
FONT = next((f for f in ("/System/Library/Fonts/AppleSDGothicNeo.ttc", "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
                         "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
                         "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
             if os.path.exists(f)), None)
ZONE_COL = {"train": (200, 160, 90), "home": (60, 120, 200), "sofa": (60, 140, 255), "exit": (90, 220, 120)}
ZONE_KO = {"train": "지하철 칸", "home": "집", "sofa": "소파", "exit": "출구"}
EV_KO = {"enter": "입장", "train": "지하철 칸 → 지하철 소리", "door": "문 → 지하철 소리 잦아듦", "sit": "소파 (1이면 조명)", "touch": "만짐 (tv면 TV 켜짐)",
         "exit": "퇴장", "result": "QR"}


def ko_text(img, items):
    """[(글, (x, y), 크기, BGR색)] 를 한글로 그린다."""
    if not items:
        return img
    try:
        from PIL import Image, ImageDraw, ImageFont
        if not FONT:
            raise ImportError
        im = Image.fromarray(img[:, :, ::-1]); d = ImageDraw.Draw(im)
        cache = {}
        for text, xy, size, col in items:
            f = cache.get(size) or cache.setdefault(size, ImageFont.truetype(FONT, size))
            d.text(xy, text, font=f, fill=(col[2], col[1], col[0]))
        return np.array(im)[:, :, ::-1].copy()
    except Exception:
        for text, xy, size, col in items:
            cv2.putText(img, text.encode("ascii", "replace").decode(), (xy[0], xy[1] + size), cv2.FONT_HERSHEY_SIMPLEX, size / 30, col, 1)
        return img


class MouseTracker(ht.Tracker):
    """카메라 대신 조작 위치를 '사람'으로 넘긴다. 나머지 판단은 Tracker 그대로."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.mouse = None             # (x, y) 화면 픽셀, None이면 사람 없음
        self.T = dict(self.T, pos_send_s=0.02)   # 게임식은 잡음이 없으니 매 프레임 보내 언리얼 1인칭이 바로 따라오게

    def person_detect(self, frame, t):
        if self.mouse is None:
            return None, None
        x, y = self.mouse
        r = BODY * S
        a = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        cnt = np.stack([x + r * np.cos(a), y + r * np.sin(a)], 1).astype(np.int32)
        return (float(x), float(y), cnt), None

    def markers_detect(self, frame):
        return {}                     # 물건은 숫자 키로


class Walker:
    """WASD 이동 + 벽(바깥 벽 · 문만 열린 가벽) 막기. 좌표는 cm (언리얼 X·Y와 같음)."""
    def __init__(self, W, H, U):
        self.W, self.H = W, H
        self.door = U.get("door") or [[190, 77], [270, 77]]
        self.ent = U.get("entrance") or [[0, 0], [0, 72]]
        self.gap = U.get("exit_gap") or [[10, H], [90, H]]
        self.wall_y = float(self.door[0][1])
        self.spawn = (BODY + 2.0, (self.ent[0][1] + self.ent[1][1]) / 2)
        self.x, self.y = self.spawn

    def reset(self):
        self.x, self.y = self.spawn

    def move(self, dx, dy):
        nx, ny = self.x + dx, self.y + dy
        (d0, _), (d1, _) = self.door
        wy, half = self.wall_y, BODY * 0.6
        in_door = lambda x: d0 + BODY <= x <= d1 - BODY
        if abs(self.y - wy) < half and not in_door(nx):              # 문틀 안에서는 옆으로 못 나감
            nx = self.x
        if not in_door(nx):                                           # 가벽: 문 구간이 아니면 못 지나감
            ny = min(ny, wy - half) if self.y < wy else max(ny, wy + half)
        in_ent = self.ent[0][1] + BODY <= ny <= self.ent[1][1] - BODY  # 입구(왼쪽 벽 지하철 칸)
        in_gap = self.gap[0][0] + BODY <= nx <= self.gap[1][0] - BODY  # 출구 틈(아래 벽)
        nx = max(nx, -60.0 if in_ent else BODY); nx = min(nx, self.W - BODY)
        ny = max(ny, BODY); ny = min(ny, self.H + 60.0 if in_gap else self.H - BODY)
        self.x, self.y = nx, ny

    def inside(self):
        return 0 <= self.x <= self.W and 0 <= self.y <= self.H


def main():
    ap = argparse.ArgumentParser(description="Home Sweet Home 게임식 시연 (카메라 대신)")
    ap.add_argument("--config", default=str(HERE / "config.json"))
    ap.add_argument("--results", default=str(HERE / "results" / "mouse"), help="기록·QR 저장 폴더 (실제 관객 기록과 따로)")
    ap.add_argument("--no-osc", action="store_true")
    ap.add_argument("--no-unreal", action="store_true", help="언리얼을 같이 켜지 않음 (에디터 ▶로 따로 켤 때)")
    ap.add_argument("--no-record", action="store_true", help="시연 기록 폴더를 만들지 않음")
    args = ap.parse_args()

    cfg = ht.load_cfg(Path(args.config))
    W, H = cfg["floor_cm"]
    fw, fh = int(PAD * 2 + W * S), int(PAD * 2 + H * S)
    cfg["floor_px"] = [[PAD, PAD], [PAD + W * S, PAD], [PAD + W * S, PAD + H * S], [PAD, PAD + H * S]]   # 화면 픽셀 ↔ cm
    cfg["nadir_px"] = None
    cfg["tune"]["facing_mode"] = "motion"          # 방향은 마우스가 정함 (facing_manual)
    Z = cfg["zones"]
    cm2px = lambda x, y: (int(round(PAD + x * S)), int(round(PAD + y * S)))
    try:
        U = json.loads((HERE / "unreal_layout.json").read_text(encoding="utf-8")).get("unreal", {})
    except Exception:
        U = {}

    logs = []
    def log(msg):
        print(msg)
        for line in str(msg).strip("\n").split("\n"):
            logs.append(line.strip())
        del logs[:-9]

    rec = None if args.no_record else SessionRecorder(args.results, "mouse", cfg, "게임식 시연")
    if rec:
        log = rec.wrap_log(log)
    osc = ht.Osc(cfg, enabled=not args.no_osc)
    tr = MouseTracker(cfg, (fw, fh), osc, args.results, log=log)
    if rec:
        rec.attach_osc(osc)
        rec.attach_tracker(tr)
    # ---- 한 화면 나눠 쓰기: 왼쪽 언리얼 게임 창, 오른쪽 시연 창 (config unreal_game.layout = "side" 기본 / "manual")
    NW, NH = fw + PANEL, fh
    PW, PH = NW, NH
    UG = cfg.setdefault("unreal_game", {})
    pygame.display.init()
    di = pygame.display.Info()
    SW, SH = di.current_w, di.current_h
    if UG.get("layout", "side") == "side" and SW > 0 and SH > 0:
        TOP = 28                                              # 맥 메뉴 막대 아래
        PW = min(NW, int(SW * float(UG.get("panel_ratio", 0.42))))
        PH = int(NH * PW / NW)
        if PH > SH - TOP - 30:
            PH = SH - TOP - 30; PW = int(NW * PH / NH)
        UW = SW - PW
        UH = min(SH - TOP - 30, int(UW * 9 / 16))
        UG["res"], UG["pos"] = [UW - 2, UH], [0, TOP]
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{UW},{TOP}"
        print(f"화면 {SW}×{SH} → 언리얼 {UW}×{UH} (왼쪽) · 시연 창 {PW}×{PH} (오른쪽)")
    ug = UnrealGame(cfg, log=log, log_path=str(rec.unreal_log) if rec else None)
    import atexit
    atexit.register(ug.stop)                                         # 오류로 끝나도 언리얼 창은 닫음
    if not (args.no_unreal or args.no_osc):
        ug.start()
    wk = Walker(W, H, U)

    # ---- 바닥 그림 (한 번만)
    base = np.full((fh, fw + PANEL, 3), 24, np.uint8)
    cv2.rectangle(base, cm2px(0, 0), cm2px(W, H), (70, 70, 70), -1)
    lab = []
    for k in ("train", "home", "sofa", "exit"):
        if not Z.get(k):
            continue
        pts = np.int32([cm2px(x, y) for x, y in Z[k]])
        over = base.copy()
        cv2.fillPoly(over, [pts], ZONE_COL[k])
        a = 0.35 if k in ("train", "home") else 0.55
        base = cv2.addWeighted(over, a, base, 1 - a, 0)
        cv2.polylines(base, [pts], True, ZONE_COL[k], 2)
        x0, y0 = pts.min(0)
        lab.append((ZONE_KO[k], (int(x0) + 6, int(y0) + 4), 17, (235, 235, 235)))
    (dx0, dy), (dx1, _) = wk.door
    cv2.line(base, cm2px(0, dy), cm2px(dx0, dy), (210, 210, 210), 5)                    # 가벽
    cv2.line(base, cm2px(dx1, dy), cm2px(W, dy), (210, 210, 210), 5)
    cv2.line(base, cm2px(dx0, dy), cm2px(dx1, dy), (40, 200, 255), 2)
    lab.append(("문", (cm2px((dx0 + dx1) / 2, dy)[0] - 8, cm2px(0, dy)[1] + 6), 15, (40, 200, 255)))
    (ex, ey0), (_, ey1) = wk.ent
    cv2.line(base, cm2px(ex, ey0), cm2px(ex, ey1), (90, 255, 255), 6)
    lab.append(("입구", (2, cm2px(0, (ey0 + ey1) / 2)[1] - 30), 13, (90, 255, 255)))
    (gx0, gy), (gx1, _) = wk.gap
    cv2.line(base, cm2px(gx0, gy), cm2px(gx1, gy), (90, 255, 120), 6)
    if U.get("tv"):
        cv2.rectangle(base, cm2px(U["tv"][0] - 18, U["tv"][1] - 25), cm2px(U["tv"][0] + 18, U["tv"][1] + 25), (150, 110, 60), -1)
        lab.append(("TV", cm2px(U["tv"][0] - 10, U["tv"][1] - 10), 14, (255, 255, 255)))
    for lx, ly in U.get("lamps", []):
        cv2.circle(base, cm2px(lx, ly), 9, (80, 200, 255), -1)
    base = ko_text(base, lab)
    help_lines = ["스페이스·클릭: 관객 등장 (마우스 잡힘)", "W/S 앞뒤 · A/D 옆걸음 (보는 방향 기준, Shift 빨리)", "마우스 좌우·←/→·Q/E: 몸 돌리기",
                  "C 소파 앉기/일어나기  1 담요  2 리모컨  3 TV  0 퇴장", "9 동선 지우기   ESC 마우스 풀기 → 끝"]
    base = ko_text(base, [(s, (fw + 16, fh - 140 + i * 25), 16, (170, 170, 170)) for i, s in enumerate(help_lines)])

    # ---- 창
    pygame.init()
    screen = pygame.display.set_mode((PW, PH))
    def show(img):                                            # 그린 화면(원래 크기)을 창 크기에 맞춰 보여 줌
        rgb = np.ascontiguousarray(img[:, :, ::-1])
        surf = pygame.image.frombuffer(rgb.tobytes(), (rgb.shape[1], rgb.shape[0]), "RGB")
        if (PW, PH) != (rgb.shape[1], rgb.shape[0]):
            surf = pygame.transform.smoothscale(surf, (PW, PH))
        screen.blit(surf, (0, 0))
    pygame.display.set_caption("Home Sweet Home - 게임식 시연 (카메라 대신)")
    clock = pygame.time.Clock()
    K = pygame
    try:
        pygame.key.stop_text_input()          # 한글 입력기가 W·A·S·D를 ㅈ·ㅁ·ㄴ·ㅇ으로 가로채지 않게
    except Exception:
        pass
    # 키는 '자리(scancode, USB 표준 번호)'로 읽는다 → 한글/영문 입력 상태와 상관없음
    SC = {"w": 26, "a": 4, "s": 22, "d": 7, "q": 20, "e": 8, "c": 6, "1": 30, "2": 31, "3": 32, "9": 38, "0": 39,
          "right": 79, "left": 80, "down": 81, "up": 82, "lshift": 225, "rshift": 229}
    FWD, BACK, SL, SR = (SC["w"], SC["up"]), (SC["s"], SC["down"]), (SC["a"],), (SC["d"],)   # 1인칭: 보는 방향 기준
    TURN_L, TURN_R, TURN_SPEED = (SC["left"], SC["q"]), (SC["right"], SC["e"]), 120.0       # 방향키·Q/E 회전 (도/초)
    KEY2SC = {K.K_w: SC["w"], K.K_a: SC["a"], K.K_s: SC["s"], K.K_d: SC["d"], K.K_q: SC["q"], K.K_e: SC["e"],
              K.K_c: SC["c"], K.K_1: SC["1"], K.K_2: SC["2"], K.K_3: SC["3"], K.K_9: SC["9"], K.K_0: SC["0"], K.K_UP: SC["up"], K.K_DOWN: SC["down"],
              K.K_LEFT: SC["left"], K.K_RIGHT: SC["right"], K.K_LSHIFT: SC["lshift"], K.K_RSHIFT: SC["rshift"]}
    held = set()                              # 지금 눌려 있는 키 자리
    def sc_of(e):
        sc = getattr(e, "scancode", 0) or 0
        return sc if sc else KEY2SC.get(getattr(e, "key", None), -1)

    st = {"present": False, "grab": False, "yaw": 0.0, "trail": []}
    def set_grab(on):
        st["grab"] = on
        pygame.event.set_grab(on)
        pygame.mouse.set_visible(not on)
        if on:
            pygame.mouse.get_rel()                                     # 쌓인 움직임 버리기
    def appear():
        if not st["present"]:
            wk.reset(); st["yaw"] = 0.0; st["present"] = True; st["sit"] = False
    # 소파 자리 (언리얼 도면): 앉으면 가운데, 일어나면 소파 앞(TV 쪽)으로 한 걸음
    (sx0, sy0), (sx1, sy1) = U.get("sofa") or [[200, 164], [267, 265]]
    seat = ((sx0 + sx1) / 2, (sy0 + sy1) / 2)
    tvp = U.get("tv") or [71, 186]
    def toggle_sit():
        if not st["present"]:
            return
        if st.get("sit"):
            wk.x, wk.y = sx0 - 50.0, seat[1]                   # 소파 앞으로 일어남 (앉음 판정 구역 밖)
            st["sit"] = False
            log("C: 일어남")
        elif sx0 - 60 <= wk.x <= sx1 + 60 and sy0 - 60 <= wk.y <= sy1 + 60:
            wk.x, wk.y = seat
            st["yaw"] = float(np.degrees(np.arctan2(tvp[1] - seat[1], tvp[0] - seat[0])))   # TV를 바라봄
            st["sit"] = True
            log("C: 소파에 앉음 (1.2초 뒤 조명·눈높이 115cm)")
        else:
            log("C: 소파 가까이(60cm 안)에서 눌러 주세요")

    FOCUS_LOST = tuple(getattr(pygame, n) for n in ("WINDOWFOCUSLOST",) if hasattr(pygame, n))
    # ---- 언리얼이 준비될 때까지 기다림 (창에 표시, 창 닫으면 그만)
    def wait_tick(el):
        for e in pygame.event.get():
            if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
                return False
        w = ko_text(base.copy(), [("언리얼 켜는 중…", (fw // 2 - 90, fh // 2 - 30), 30, (0, 200, 255)),
                                   (f"{el:4.0f}초 · 게임 창이 뜨고 화면이 둘로 나뉘면 준비 끝", (fw // 2 - 190, fh // 2 + 14), 17, (220, 220, 220))])
        show(w)
        pygame.display.flip()
    if ug.p is not None and not ug.wait_ready(tick=wait_tick):
        if ug.p is not None and ug.p.poll() is None and ug.status != "시간 초과":
            ug.stop(); pygame.quit()
            if rec:
                rec.unreal_status = ug.status; rec.close()
            return
    if rec:
        rec.unreal_status = ug.status
    # (언리얼 창이 앞에 떠도 시연 창을 한 번 클릭하면 앞으로 옴 — pygame._sdl2 focus는 맥에서 Bus error를 내서 뺌)
    dummy = np.zeros((8, 8, 3), np.uint8)
    t0, prev_state, qr = time.monotonic(), "IDLE", None
    print(f"게임식 시연 · OSC → {cfg['osc']['host']}:{cfg['osc']['port']}{' (꺼짐)' if args.no_osc else ''} · 기록: {args.results}")
    running = True
    try:
        while running:
            dt = min(clock.tick(30) / 1000.0, 0.1)
            t = time.monotonic() - t0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                elif e.type == pygame.KEYUP:
                    held.discard(sc_of(e))
                elif e.type in FOCUS_LOST:
                    held.clear()
                elif e.type == pygame.KEYDOWN:
                    k = sc_of(e); held.add(k)
                    if e.key == pygame.K_ESCAPE or k == 41:
                        if st["grab"]:
                            set_grab(False)
                        else:
                            running = False
                    elif e.key == pygame.K_SPACE or k == 44:
                        if st["present"]:
                            st["present"] = False
                        else:
                            appear()
                    elif tr.state == "IN" and k == SC["1"]:
                        tr.touch(t, "blanket", "키보드 1")
                    elif tr.state == "IN" and k == SC["2"]:
                        tr.touch(t, "remote", "키보드 2")
                    elif tr.state == "IN" and k == SC["3"]:
                        tr.touch(t, "tv", "키보드 3")
                    elif tr.state == "IN" and k == SC["0"]:
                        tr.finish(t, "강제 퇴장(키보드 0)")
                    elif k == SC["9"]:
                        st["trail"] = []
                    elif k == SC["c"]:
                        toggle_sit()
                elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                    if not st["grab"]:
                        set_grab(True)
                    appear()
                elif e.type == pygame.MOUSEMOTION and st["grab"]:
                    st["yaw"] = (st["yaw"] + e.rel[0] * SENS + 180) % 360 - 180

            on = lambda ks: any(k in held for k in ks)
            turn = (1 if on(TURN_R) else 0) - (1 if on(TURN_L) else 0)
            if st["present"] and turn:
                st["yaw"] = (st["yaw"] + turn * TURN_SPEED * dt + 180) % 360 - 180
            f = (1 if on(FWD) else 0) - (1 if on(BACK) else 0)      # 앞(+)/뒤(-)
            r = (1 if on(SR) else 0) - (1 if on(SL) else 0)         # 오른쪽(+)/왼쪽(-) 옆걸음
            if st["present"] and (f or r) and not st.get("sit"):   # 앉아 있는 동안은 고개만 돌림 (C로 일어남)
                sp = RUN if on((SC["lshift"], SC["rshift"])) else WALK
                a = np.radians(st["yaw"])
                fx, fy = np.cos(a), np.sin(a)                     # 앞 방향 (0°=+X, 90°=+Y, 언리얼과 같음)
                rx, ry = -fy, fx                                  # 오른쪽 = 앞에서 시계 방향 90°
                vx, vy = f * fx + r * rx, f * fy + r * ry
                n = (vx * vx + vy * vy) ** 0.5
                wk.move(vx / n * sp * dt, vy / n * sp * dt)

            visible = st["present"] and wk.inside()
            tr.mouse = cm2px(wk.x, wk.y) if visible else None
            tr.facing_manual = st["yaw"] if visible else None
            tr.process(dummy, t)
            if prev_state == "IN" and tr.state == "IDLE":          # 퇴장 → 다음 관객은 다시 스페이스/클릭
                st["present"], st["trail"] = False, []
                tr.need_clear, tr.relearn_until = False, 0.0
            prev_state = tr.state
            if tr.state == "IN" and tr.person is not None and (not st["trail"] or np.hypot(*(np.subtract(st["trail"][-1], tr.person[3]))) > 4):
                st["trail"].append(tuple(map(float, tr.person[3])))
            if tr.last_result is not None and tr.last_result is not (qr or (None,))[0]:
                lr = tr.last_result
                card = ht.qr_card(lr[0], lr[1], lr[2], lr[3]) if lr[2] else None
                qr = (lr, card, time.monotonic() + tr.T.get("qr_show_s", 20.0))
            if qr and (time.monotonic() > qr[2] or tr.state == "IN"):
                qr = None

            # ---- 그리기
            v = base.copy()
            if len(st["trail"]) > 1:
                cv2.polylines(v, [np.int32([cm2px(*p) for p in st["trail"]])], False, (0, 200, 255), 2, cv2.LINE_AA)
            if st["present"]:
                fan = np.int32([cm2px(*p) for p in ht.fan_poly((wk.x, wk.y), st["yaw"], tr.T.get("fan_deg", 60), tr.T.get("fan_cm", 90))])
                ov = v.copy(); cv2.fillPoly(ov, [fan], (0, 220, 255)); v = cv2.addWeighted(ov, 0.35, v, 0.65, 0)
                cv2.polylines(v, [fan], True, (0, 220, 255), 2, cv2.LINE_AA)
                col = (80, 220, 80) if tr.state == "IN" else (0, 200, 255)
                cv2.circle(v, cm2px(wk.x, wk.y), int(BODY * S * 0.7), col, -1, cv2.LINE_AA)
                cv2.circle(v, cm2px(wk.x, wk.y), int(BODY * S * 0.7), (20, 20, 20), 2, cv2.LINE_AA)
            txt, x0 = [], fw + 16
            if tr.state == "IN":
                txt.append((f"관객 #{tr.vid:04d}  ·  {t - tr.t0:4.0f}초", (x0, 18), 22, (120, 255, 120)))
            elif tr.mouse is not None:
                txt.append(("입장 중… (0.8초)", (x0, 18), 22, (0, 200, 255)))
            else:
                txt.append(("대기 — 스페이스나 창 클릭으로 관객 등장", (x0, 18), 17, (200, 200, 200)))
            if st["present"]:
                txt.append((f"위치 X {wk.x:4.0f} Y {wk.y:4.0f} cm · 방향 {st['yaw']:4.0f}°", (x0, 54), 16, (220, 220, 220)))
            room = {"train": "지하철 칸", "home": "집"}.get(tr.room, "-") if tr.state == "IN" else "-"
            flags = []
            if tr.state == "IN":
                flags.append("소파에 앉음" if tr.seated else ("앉는 중…" if tr.sit_since else ""))
                if tr.exit_since:
                    flags.append(f"출구 {max(0.0, tr.T.get('exit_dwell_s', 3.0) - (t - tr.exit_since)):.1f}초 뒤 퇴장")
            txt.append((f"구역: {room}   {'  '.join(f for f in flags if f)}", (x0, 80), 17, (220, 220, 220)))
            if tr.touch_count:
                txt.append(("만짐: " + ", ".join(f"{ht.NAMES_KO.get(k, k)} {n}" for k, n in tr.touch_count.items()), (x0, 106), 17, (220, 220, 220)))
            if not st["grab"]:
                txt.append(("※ 창을 클릭하면 마우스로 시야를 돌려요", (x0, 128), 14, (0, 200, 255)))
            elif tr.state == "IN" and tr.door_sent:                     # 소리 세 갈래 (누적 초 → 볼륨)
                ls, vv = tr.layer_s, tr.vols
                txt.append((f"소리 음악 {vv[0]:.2f}({ls['sofa']:.0f}s) · TV {vv[1]:.2f}({ls['tv']:.0f}s){' ●' if tr.watching_tv else ''} · 모닥불 {vv[2]:.2f}({ls['blanket']:.0f}s)",
                            (x0, 128), 14, (255, 200, 120)))
            txt.append(("보낸 신호 (OSC)" + (" — 꺼짐" if args.no_osc else ""), (x0, 150), 16, (150, 150, 150)))
            for i, (te, name, val) in enumerate(tr.events_out[-8:]):
                vv = " ".join(str(x) for x in val)[:16] if name != "result" else ""
                txt.append((f"{te:6.1f}s /home/{name} {vv} {EV_KO.get(name, '')}", (x0, 174 + i * 22), 14, (200, 230, 255)))
            for i, line in enumerate(logs[-3:]):
                txt.append((line[:40], (x0, 360 + i * 20), 13, (160, 160, 160)))
            v = ko_text(v, txt)
            if qr and qr[1] is not None:                                # 퇴장 QR (오른쪽 판에)
                c = cv2.resize(qr[1], (PANEL - 20, int((PANEL - 20) * qr[1].shape[0] / qr[1].shape[1])))
                h = min(c.shape[0], fh - 20)
                v[10:10 + h, fw + 10:fw + 10 + c.shape[1]] = c[:h]
            if rec:
                rec.frame(v)                                   # 시연 화면 녹화 (15fps)
            show(v)
            pygame.display.flip()
    except KeyboardInterrupt:
        pass
    finally:
        if tr.state == "IN":
            tr.finish(time.monotonic() - t0, "프로그램 종료")
        pygame.quit()
        ug.stop()
        if rec:
            page = rec.close()
            print(f"시연 기록: {page}")
            if sys.platform == "darwin":
                os.system(f'open "{page}"')


if __name__ == "__main__":
    main()
