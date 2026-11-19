#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Home Sweet Home — 마우스 시연 (카메라 대신 쓰는 서브 프로그램)

카메라 없이 노트북에서 마우스로 '관객'을 움직여 언리얼에 같은 OSC 신호를 보낸다.
판단 규칙(입장 0.8초 · 지하철 칸 · 문 0.4초 · 소파 1.2초 · 출구 3초 · QR)은 home_tracker.py의 Tracker를 그대로 쓴다.
→ 카메라를 달고 나면 home_tracker.py로 바꾸기만 하면 언리얼 쪽은 손댈 필요 없음.

조작 (숫자 키라서 한글 입력 상태에서도 됨)
  왼쪽 클릭        관객 등장 → 마우스 위치 = 관객 발 위치
  오른쪽 클릭/스페이스  관객 잠깐 멈춤(화면에서 사라짐) / 다시 나타남
  마우스를 바닥 밖으로  화면 밖으로 나간 것과 같음 (출구 근처에서 나가면 1.5초 뒤 퇴장)
  1 담요 만짐   2 리모컨 만짐   3 손잡이 잡음(/home/handle — 언리얼은 아직 반응 없음)
  0 지금 강제 퇴장   9 동선 지우기   ESC 끝내기

  python3 home_mouse.py                  (결과는 results/mouse/ 에 따로 저장)
  python3 home_mouse.py --no-osc         (언리얼 없이 규칙만 확인)
"""
import argparse, os, sys, time, json
from pathlib import Path
import numpy as np
import cv2

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import home_tracker as ht                                     # 같은 규칙·OSC·QR 사용

S, PAD, PANEL = 2.0, 34, 360          # 1cm = 2px, 바닥 둘레 여백, 오른쪽 안내판 폭
FONT = next((f for f in ("/System/Library/Fonts/AppleSDGothicNeo.ttc", "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
                         "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc")
             if os.path.exists(f)), None)
ZONE_COL = {"train": (200, 160, 90), "home": (60, 120, 200), "sofa": (60, 140, 255), "exit": (90, 220, 120)}
ZONE_KO = {"train": "지하철 칸", "home": "집", "sofa": "소파", "exit": "출구"}
EV_KO = {"enter": "입장", "train": "지하철 칸 → 지하철 소리", "door": "문 열고 집으로 → 조명·TV", "sit": "소파", "touch": "만짐",
         "exit": "퇴장", "result": "QR", "handle": "손잡이"}


def ko_text(img, items):
    """[(글, (x, y), 크기, BGR색)] 를 한글로 그린다. 글꼴이 없으면 영어 대체 없이 OpenCV 기본 글꼴."""
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
    """카메라 대신 마우스 위치를 '사람'으로 넘긴다. 나머지 판단은 Tracker 그대로."""
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.mouse = None             # (x, y) 화면 픽셀, None이면 사람 없음

    def person_detect(self, frame, t):
        if self.mouse is None:
            return None, None
        x, y = self.mouse
        r = 15 * S                    # 사람 덩어리 = 지름 30cm 원 (가림 판단용)
        a = np.linspace(0, 2 * np.pi, 16, endpoint=False)
        cnt = np.stack([x + r * np.cos(a), y + r * np.sin(a)], 1).astype(np.int32)
        return (float(x), float(y), cnt), None

    def markers_detect(self, frame):
        return {}                     # 물건은 숫자 키로


def main():
    ap = argparse.ArgumentParser(description="Home Sweet Home 마우스 시연 (카메라 대신)")
    ap.add_argument("--config", default=str(HERE / "config.json"))
    ap.add_argument("--results", default=str(HERE / "results" / "mouse"), help="기록·QR 저장 폴더 (실제 관객 기록과 따로)")
    ap.add_argument("--no-osc", action="store_true")
    args = ap.parse_args()

    cfg = ht.load_cfg(Path(args.config))
    W, H = cfg["floor_cm"]
    fw, fh = int(PAD * 2 + W * S), int(PAD * 2 + H * S)
    cfg["floor_px"] = [[PAD, PAD], [PAD + W * S, PAD], [PAD + W * S, PAD + H * S], [PAD, PAD + H * S]]   # 화면 픽셀 ↔ cm
    cfg["nadir_px"] = None
    Z = cfg["zones"]
    cm2px = lambda x, y: (int(round(PAD + x * S)), int(round(PAD + y * S)))

    logs = []
    def log(msg):
        print(msg)
        for line in str(msg).strip("\n").split("\n"):
            logs.append(line.strip())
        del logs[:-9]

    osc = ht.Osc(cfg, enabled=not args.no_osc)
    tr = MouseTracker(cfg, (fw, fh), osc, args.results, log=log)

    # 바닥 그림 (한 번만)
    base = np.full((fh, fw + PANEL, 3), 24, np.uint8)
    cv2.rectangle(base, cm2px(0, 0), cm2px(W, H), (70, 70, 70), -1)
    lab = []
    for k in ("train", "home", "sofa", "exit"):
        if not Z.get(k):
            continue
        pts = np.int32([cm2px(x, y) for x, y in Z[k]])
        over = base.copy()
        cv2.fillPoly(over, [pts], ZONE_COL[k])
        base = cv2.addWeighted(over, 0.35 if k in ("train", "home") else 0.55, base, 0.65 if k in ("train", "home") else 0.45, 0)
        cv2.polylines(base, [pts], True, ZONE_COL[k], 2)
        x0, y0 = pts.min(0)
        lab.append((ZONE_KO[k], (int(x0) + 6, int(y0) + 4), 17, (235, 235, 235)))
    try:                                            # 언리얼 도면(unreal_layout.json): 가벽·문·입구·출구·TV·스탠드
        U = json.loads((HERE / "unreal_layout.json").read_text(encoding="utf-8")).get("unreal", {})
        if U.get("door"):
            (dx0, dy), (dx1, _) = U["door"]
            cv2.line(base, cm2px(0, dy), cm2px(dx0, dy), (210, 210, 210), 5)            # 가벽
            cv2.line(base, cm2px(dx1, dy), cm2px(W, dy), (210, 210, 210), 5)
            cv2.line(base, cm2px(dx0, dy), cm2px(dx1, dy), (40, 200, 255), 2)
            lab.append(("문", (cm2px((dx0 + dx1) / 2, dy)[0] - 8, cm2px(0, dy)[1] + 6), 15, (40, 200, 255)))
        if U.get("entrance"):
            (ex, ey0), (_, ey1) = U["entrance"]
            cv2.line(base, cm2px(ex, ey0), cm2px(ex, ey1), (90, 255, 255), 6)
            lab.append(("입구", (2, cm2px(0, (ey0 + ey1) / 2)[1] - 30), 13, (90, 255, 255)))
        if U.get("exit_gap"):
            (gx0, gy), (gx1, _) = U["exit_gap"]
            cv2.line(base, cm2px(gx0, gy), cm2px(gx1, gy), (90, 255, 120), 6)
        if U.get("tv"):
            cv2.rectangle(base, cm2px(U["tv"][0] - 18, U["tv"][1] - 25), cm2px(U["tv"][0] + 18, U["tv"][1] + 25), (150, 110, 60), -1)
            lab.append(("TV", cm2px(U["tv"][0] - 10, U["tv"][1] - 10), 14, (255, 255, 255)))
        for lx, ly in U.get("lamps", []):
            cv2.circle(base, cm2px(lx, ly), 9, (80, 200, 255), -1)
    except Exception:
        pass
    base = ko_text(base, lab)
    help_lines = ["왼쪽 클릭: 관객 등장 / 마우스 = 발 위치", "오른쪽 클릭·스페이스: 사라짐 ↔ 다시",
                  "1 담요   2 리모컨   3 손잡이", "0 강제 퇴장   9 동선 지우기   ESC 끝",
                  "바닥 밖으로 나가면 화면 밖과 같음"]
    base = ko_text(base, [(s, (fw + 16, fh - 140 + i * 25), 16, (170, 170, 170)) for i, s in enumerate(help_lines)])

    st = {"on": False, "xy": None, "trail": []}
    def on_mouse(e, x, y, flags, _p):
        if e == cv2.EVENT_MOUSEMOVE or e == cv2.EVENT_LBUTTONDOWN:
            st["xy"] = (x, y)
        if e == cv2.EVENT_LBUTTONDOWN:
            st["on"] = True
        if e == cv2.EVENT_RBUTTONDOWN:
            st["on"] = not st["on"]

    win, qr_win = "Home Sweet Home - MOUSE (카메라 대신)", "QR"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, on_mouse)
    dummy = np.zeros((8, 8, 3), np.uint8)
    t0, prev_state, qr_until, qr_seen, shown = time.monotonic(), "IDLE", 0.0, None, False
    print(f"마우스 시연 · OSC → {cfg['osc']['host']}:{cfg['osc']['port']}{' (꺼짐)' if args.no_osc else ''} · 기록: {args.results}")
    try:
        while True:
            t = time.monotonic() - t0
            xy = st["xy"]
            inside = xy is not None and PAD <= xy[0] <= PAD + W * S and PAD <= xy[1] <= PAD + H * S
            tr.mouse = xy if (st["on"] and inside) else None
            tr.process(dummy, t)
            if prev_state == "IN" and tr.state == "IDLE":          # 퇴장 → 다음 관객은 다시 클릭
                st["on"], st["trail"] = False, []
                tr.need_clear, tr.relearn_until = False, 0.0       # 마우스는 '화면이 빌 때까지' 기다릴 필요 없음
            prev_state = tr.state
            if tr.state == "IN" and tr.person is not None and (not st["trail"] or np.hypot(*(np.subtract(st["trail"][-1], tr.person[3]))) > 4):
                st["trail"].append(tuple(map(float, tr.person[3])))

            # ---- 그리기
            v = base.copy()
            if len(st["trail"]) > 1:
                cv2.polylines(v, [np.int32([cm2px(*p) for p in st["trail"]])], False, (0, 200, 255), 2, cv2.LINE_AA)
            if tr.mouse is not None:
                cv2.circle(v, tuple(map(int, tr.mouse)), int(15 * S), (200, 200, 200), 1, cv2.LINE_AA)
            if tr.person is not None:
                px, py = tr.person[3]
                col = (80, 220, 80) if tr.state == "IN" else (0, 200, 255)
                cv2.circle(v, cm2px(px, py), 11, col, -1, cv2.LINE_AA)
                cv2.circle(v, cm2px(px, py), 11, (20, 20, 20), 2, cv2.LINE_AA)
            txt = []
            x0 = fw + 16
            if tr.state == "IN":
                stay = t - tr.t0
                txt.append((f"관객 #{tr.vid:04d}  ·  {stay:4.0f}초", (x0, 18), 22, (120, 255, 120)))
            elif tr.need_clear:
                txt.append(("퇴장함 — 바닥에서 비켜 있으면 다음 관객 준비", (x0, 18), 17, (0, 200, 255)))
            elif tr.mouse is not None:
                txt.append(("입장 중… (0.8초)", (x0, 18), 22, (0, 200, 255)))
            else:
                txt.append(("대기 — 바닥을 클릭하면 관객 등장", (x0, 18), 19, (200, 200, 200)))
            if tr.person is not None:
                px, py = tr.person[3]
                txt.append((f"위치 X {px:5.0f}  Y {py:5.0f} cm", (x0, 54), 17, (220, 220, 220)))
            room = {"train": "지하철 칸", "home": "집"}.get(tr.room, "-") if tr.state == "IN" else "-"
            flags = []
            if tr.state == "IN":
                flags.append("소파에 앉음" if tr.seated else ("앉는 중…" if tr.sit_since else ""))
                if tr.exit_since:
                    flags.append(f"출구 {max(0.0, tr.T.get('exit_dwell_s', 3.0) - (t - tr.exit_since)):.1f}초 뒤 퇴장")
            txt.append((f"구역: {room}   {'  '.join(f for f in flags if f)}", (x0, 80), 17, (220, 220, 220)))
            if tr.touch_count:
                txt.append(("만짐: " + ", ".join(f"{ht.NAMES_KO.get(k, k)} {n}" for k, n in tr.touch_count.items()), (x0, 106), 17, (220, 220, 220)))
            txt.append(("보낸 신호 (OSC)" + (" — 꺼짐" if args.no_osc else ""), (x0, 142), 16, (150, 150, 150)))
            for i, (te, name, val) in enumerate(tr.events_out[-8:]):
                vv = " ".join(str(x) for x in val)[:22] if name != "result" else ""
                txt.append((f"{te:6.1f}s  /home/{name} {vv}  {EV_KO.get(name, '')}",
                            (x0, 166 + i * 22), 15, (200, 230, 255)))
            for i, line in enumerate(logs[-4:]):
                txt.append((line[:40], (x0, 356 + i * 22), 14, (160, 160, 160)))
            v = ko_text(v, txt)
            cv2.imshow(win, v)

            lr = tr.last_result                                  # 새 결과 → QR 창 (home_tracker와 같음)
            if lr is not None and lr is not qr_seen and lr[2]:
                qr_seen = lr
                cv2.namedWindow(qr_win, cv2.WINDOW_NORMAL)
                cv2.imshow(qr_win, ht.qr_card(lr[0], lr[1], lr[2], lr[3]))
                qr_until = time.monotonic() + tr.T.get("qr_show_s", 20.0)
            if qr_until and (time.monotonic() > qr_until or tr.state == "IN"):
                cv2.destroyWindow(qr_win)
                qr_until = 0.0

            k = cv2.waitKey(30) & 0xFF
            if shown and cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                break
            shown = True
            if k in (27, ord("q")):
                break
            if k == ord(" "):
                st["on"] = not st["on"]
            if tr.state == "IN":
                if k == ord("1"):
                    tr.touch(t, "blanket", "키보드 1")
                if k == ord("2"):
                    tr.touch(t, "remote", "키보드 2")
                if k == ord("3"):
                    log(f"[{t - tr.t0:6.1f}s] 손잡이 잡음")
                    tr.emit(t, "handle", 1)
                if k == ord("0"):
                    tr.finish(t, "강제 퇴장(키보드 0)")
            if k == ord("9"):
                st["trail"] = []
    except KeyboardInterrupt:
        pass
    if tr.state == "IN":
        tr.finish(time.monotonic() - t0, "프로그램 종료")
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass


if __name__ == "__main__":
    main()
