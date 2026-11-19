#!/usr/bin/env python3
"""Home Sweet Home — 천장 CCTV 감지 프로그램 (시연용)

카메라가 위에서 내려다본 화면으로
  사람 동선 · 소파에 앉음 · 담요/리모컨(ArUco 마커) 변화 · 출구 퇴장
을 알아채고, 언리얼(블루프린트)로 OSC 신호를 보내고, 퇴장하면 결과 QR을 만든다.

  python3 home_tracker.py --setup          현장 설정 (바닥 4점 · 소파 · 출구)  ← 공간이 바뀌면 이것만 다시
  python3 home_tracker.py                  실행 (인식 화면 + OSC 전송)
  python3 home_tracker.py --video a.mp4    영상 파일로 시험

  자주 쓰는 옵션: --camera 1 (카메라 번호) · --no-osc · --list-cameras
  실행 중 키(CCTV 창을 클릭한 뒤): ESC 또는 q 종료 · b 배경 다시 찍기 · r 지금 관객 강제 종료 · s 화면 저장
  창 닫기 버튼이나 터미널 Ctrl+C로 꺼도 기록은 저장된다. (b·r·s는 영문 입력 상태에서)
"""
import argparse, json, math, os, sys, time
from pathlib import Path

import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
DEFAULT_CFG = {
    "camera": 0,
    "frame_size": [1920, 1080],
    "floor_px": None,                 # 화면에서 찍은 바닥 네 모서리 [좌상, 우상, 우하, 좌하] (픽셀)
    "floor_cm": [340, 190],           # 그 네 모서리가 이루는 바닥 크기 (가로, 세로 cm)
    "nadir_px": None,                 # 카메라 바로 아래 지점(화면 픽셀). 비우면 화면 가운데 = 바로 아래를 보고 있을 때
    "zones": {                        # 바닥 좌표(cm) 다각형
        "sofa": [[230, 40], [330, 40], [330, 120], [230, 120]],
        "exit": [[0, 150], [60, 150], [60, 190], [0, 190]],
    },
    "markers": {"1": "blanket", "3": "blanket", "2": "remote", "4": "spare", "5": "spare_small"},
    "osc": {"host": "127.0.0.1", "port": 8000},
    "result_base": "https://aiclaudehiggsfield3-dot.github.io/home-exhibition/r.html",
    "tune": {
        "proc_width": 640,            # 사람 감지용 축소 폭
        "diff_thresh": 26,            # 배경과의 밝기 차이 문턱
        "shadow_remove": True,        # 색은 그대로인데 어두워지기만 한 곳(그림자)은 사람에서 뺌
        "shadow_ratio": [0.3, 0.93],  # 그림자로 볼 밝기 비율 범위 (배경 대비)
        "shadow_chroma": 0.035,       # 이보다 색 차이가 작으면 그림자
        "min_person_frac": 0.006,     # 화면 대비 사람 덩어리 최소 크기
        "move_cm": 12,                # 이만큼 옮겨지면 '만짐'
        "hide_free_s": 1.0,           # 가려진 것도 아닌데 안 보이면 '집어 감'
        "hide_under_s": 4.0,          # 사람 아래에 이만큼 가려지면 '들고 있음'
        "sit_s": 1.2, "stand_s": 1.5,
        "absent_exit_s": 1.5,         # 출구 근처에서 사라지고 이만큼 지나면 퇴장
        "lost_s": 10.0,               # 출구 아닌 곳에서 사라지면 이만큼 기다린 뒤 종료
        "exit_margin_cm": 40,
        "foot_point": True,           # (예전 설정) point_mode가 없을 때만 씀
        "point_mode": "foot",         # finger(손끝: 손 인식 → 피부색) 추천은 손 시연 때
        "person_detector": "bg",      # bg(빈 방 배경과 비교) · yolo(사람 형체 인식: pip3 install ultralytics → 그림자·TV를 사람으로 안 봄)
        "yolo_model": "yolov8n-seg.pt",   # 처음 실행 때 자동으로 받아요 (약 7MB)
        "yolo_conf": 0.35,            # 이보다 확신이 낮으면 사람으로 안 봄
        "yolo_imgsz": 640,            # 인식용 크기 (작을수록 빠름, 480도 가능)
        "use_mediapipe": False,       # True + pip3 install mediapipe → 손 전체가 보일 때 검지 끝을 손 인식으로 (손 일부만 보이면 피부색 방식이 더 안정적)
        "tip_band": 0.85,             # 끝점 후보 범위 (손끝은 0.96)
        "skin_lo": [40, 136, 77], "skin_hi": [255, 180, 130],   # 피부색 범위 (YCrCb)         # 위치로 삼을 점: foot(위에서 본 사람의 발) · tip(손끝: 화면 가장자리에서 가장 먼 끝) · center(덩어리 중심)
        "foot_radius_cm": 15,
        "max_jump_cm": 80,
        "smooth_n": 5,                # 위치는 최근 이만큼의 중간값 (튀는 점 거르기)
        "gate_frac_s": 0.75,          # 초당 화면 폭의 이 비율보다 빨리 튀면, 0.3초 넘게 이어질 때만 인정
        "static_s": 3.0,              # 사람 덩어리가 이 시간 동안 전혀 안 움직이면 가짜(그림자 등)로 보고 배경으로 흡수
        "static_seated_s": 30.0,      # 소파에 앉아 있을 때는 더 오래 기다림
        "static_motion": 2.0,         # 이보다 화면 변화가 작으면 '안 움직임'
            # 한 프레임에 이보다 멀리 떨어진 덩어리는 같은 사람으로 안 봄
        "seat_hold_cm": 50,           # 앉아 있을 때 위치가 이만큼 튀면 1초 이상 이어질 때만 인정
        "ghost_cm": {"blanket": 45, "remote": 15},
        "cover_margin_cm": 20,        # 사람 덩어리에서 이 거리 안이면 '가려진 것'
        "still_cms": 12,              # 사람이 이보다 느리면 '멈춰 있음' (들고 있음 판단은 멈춰 있을 때만 셈)
        "sofa_margin_cm": 35,         # 앉은 뒤에는 소파 영역에서 이만큼 벗어나야 '일어남'
        "entry_edge_cm": 60,          # entry_anywhere가 꺼져 있을 때만: 바닥 가장자리 이 거리 안에서 나타나야 입장
        "entry_anywhere": True,       # 바닥 영역 안 어디든 사람이 1초쯤 보이면 자동 입장
        "entry_s": 0.8,               # 입장으로 볼 때까지 이어서 보여야 하는 시간
        "exit_dwell_s": 3.0,          # 출구 영역 안에 이 시간 동안 있으면 퇴장 → QR
        "clear_s": 1.0,               # 퇴장 뒤 화면이 이만큼 비어야 다음 관객 입장 받음
        "qr_show_s": 20.0,            # QR 창을 띄워 두는 시간 (다음 관객이 들어오면 바로 닫힘)
        "pos_send_s": 0.1, "sample_s": 0.25,
        "door_s": 0.4,                # 집 구역에 이만큼 머물면 '문 열고 들어옴' (/home/door)
    },
}
NAMES_KO = {"blanket": "담요", "remote": "리모컨", "sofa": "소파", "spare": "예비", "spare_small": "예비 소형"}


def load_cfg(path):
    cfg = json.loads(json.dumps(DEFAULT_CFG))
    if path.exists():
        user = json.loads(path.read_text(encoding="utf-8"))
        cfg["_user_tune_keys"] = list(user.get("tune", {}).keys())
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    return normalize_cfg(cfg)


def order_corners(pts):
    """찍은 순서와 상관없이 좌상 · 우상 · 우하 · 좌하로"""
    p = np.float32(pts)
    s, d = p.sum(axis=1), (p[:, 0] - p[:, 1])
    return [p[np.argmin(s)], p[np.argmax(d)], p[np.argmax(s)], p[np.argmin(d)]]


def order_poly(pts):
    """영역 꼭짓점을 둘레 순서로 (지그재그로 찍어도 꼬이지 않게)"""
    p = np.float32(pts)
    c = p.mean(axis=0)
    return p[np.argsort(np.arctan2(p[:, 1] - c[1], p[:, 0] - c[0]))].tolist()


def normalize_cfg(cfg):
    """바닥 모서리 순서가 어긋났으면 바로잡고, 영역 좌표(cm)도 같이 옮긴다."""
    if cfg.get("floor_px") and len(cfg["floor_px"]) == 4:
        old = np.float32(cfg["floor_px"])
        new = np.float32(order_corners(old))
        if not np.allclose(old, new):
            W, H = cfg["floor_cm"]
            Hold = cv2.getPerspectiveTransform(old, np.float32([[0, 0], [W, 0], [W, H], [0, H]]))
            oc = to_floor(Hold, new)                                  # 새 모서리들의 예전 cm 좌표
            nW, nH = float(np.linalg.norm(oc[1] - oc[0])), float(np.linalg.norm(oc[3] - oc[0]))
            Hnew = cv2.getPerspectiveTransform(new, np.float32([[0, 0], [nW, 0], [nW, nH], [0, nH]]))
            for k, poly in list(cfg.get("zones", {}).items()):
                if poly:
                    img = to_floor(np.linalg.inv(Hold), poly)
                    cfg["zones"][k] = [[round(float(x), 1), round(float(y), 1)] for x, y in to_floor(Hnew, img)]
            cfg["floor_px"], cfg["floor_cm"] = new.tolist(), [round(nW, 1), round(nH, 1)]
    for k, poly in list(cfg.get("zones", {}).items()):
        if poly and len(poly) >= 3:
            cfg["zones"][k] = [[round(float(x), 1), round(float(y), 1)] for x, y in order_poly(poly)]
    return cfg


def set_floor_size(cfg, W, H):
    """바닥 크기만 바꾸기 — 영역은 같은 자리(비율)를 유지"""
    oW, oH = cfg["floor_cm"]
    for k, poly in cfg.get("zones", {}).items():
        cfg["zones"][k] = [[round(x * W / oW, 1), round(y * H / oH, 1)] for x, y in poly]
    cfg["floor_cm"] = [W, H]
    return cfg


def floor_homography(cfg, frame_wh):
    W, H = cfg["floor_cm"]
    if cfg.get("floor_px"):
        src = np.float32(cfg["floor_px"])
    else:                              # 바닥을 안 찍었으면 화면 전체 = 바닥
        w, h = frame_wh
        src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([[0, 0], [W, 0], [W, H], [0, H]])
    Hm = cv2.getPerspectiveTransform(src, dst)
    return Hm, np.linalg.inv(Hm)


def to_floor(Hm, pts):
    p = cv2.perspectiveTransform(np.float32(pts).reshape(-1, 1, 2), Hm)
    return p.reshape(-1, 2)


def in_poly(pt, poly, margin=0.0):
    d = cv2.pointPolygonTest(np.float32(poly).reshape(-1, 1, 2), (float(pt[0]), float(pt[1])), True)
    return d >= -margin


# ---------------------------------------------------------------- 결과 주소 (QR)
B36 = "0123456789abcdefghijklmnopqrstuvwxyz"


def b36(n, width=2):
    n = max(0, min(int(round(n)), 36 ** width - 1))
    s = ""
    for _ in range(width):
        s = B36[n % 36] + s
        n //= 36
    return s


def build_result_url(base, vid, stay, floor_cm, zones, samples, events, max_pts=60):
    """결과를 주소 #뒤에 담는다 (서버로 전송되지 않음). r.html이 풀어서 그린다."""
    pts = samples
    if len(pts) > max_pts:
        idx = np.linspace(0, len(pts) - 1, max_pts).round().astype(int)
        pts = [pts[i] for i in idx]
    dt = stay / max(1, len(pts) - 1)
    path = "".join(b36(x) + b36(y) for (_, x, y, _s) in pts)
    zone = lambda poly: "".join(b36(x) + b36(y) for x, y in poly)
    ev = ".".join(f"{name[0]}{b36(t, 2)}" for name, t in events)   # b=담요 r=리모컨 s=소파
    parts = ["v1", str(vid), f"{stay:.0f}", f"{dt:.2f}", f"{floor_cm[0]:.0f}", f"{floor_cm[1]:.0f}",
             zone(zones.get("sofa", [])), zone(zones.get("exit", [])), path, ev]
    return f"{base}#d=" + "~".join(parts)


def save_qr(url, path):
    try:
        import qrcode
    except ImportError:
        print("  (qrcode 패키지가 없어 QR 이미지를 못 만들었어요: pip install qrcode)")
        return None
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=3)
    q.add_data(url); q.make(fit=True)
    img = q.make_image()
    img.save(path)
    return path


def qr_card(vid, stay, qr_path, url, size=(900, 1000)):
    """QR 창에 띄울 그림: 흰 바탕 + QR + 안내 글 (한글 글꼴이 있으면 한글로)."""
    W, H = size
    card = np.full((H, W, 3), 255, np.uint8)
    q = cv2.imread(str(qr_path)) if qr_path else None
    if q is not None:
        s = 640
        q = cv2.resize(q, (s, s), interpolation=cv2.INTER_NEAREST)
        x0, y0 = (W - s) // 2, 150
        card[y0:y0 + s, x0:x0 + s] = q
    lines = [(f"관객 #{vid:04d} · 머문 시간 {stay:.0f}초", 46, 50), ("휴대폰으로 찍으면 내 동선이 나와요", 38, 820), ("Scan to see your path", 30, 880)]
    font = None
    for fp in ("/System/Library/Fonts/AppleSDGothicNeo.ttc", "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
               "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"):
        if os.path.exists(fp):
            font = fp
            break
    try:
        from PIL import Image, ImageDraw, ImageFont
        if not font:
            raise ImportError
        im = Image.fromarray(card[:, :, ::-1]); d = ImageDraw.Draw(im)
        for text, sz, y in lines:
            f = ImageFont.truetype(font, sz)
            w = d.textlength(text, font=f)
            d.text(((W - w) / 2, y), text, font=f, fill=(20, 20, 20))
        card = np.array(im)[:, :, ::-1].copy()
    except Exception:
        cv2.putText(card, f"Visitor #{vid:04d}  {stay:.0f}s", (60, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (20, 20, 20), 3)
        cv2.putText(card, "Scan to see your path", (60, 880), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (20, 20, 20), 3)
    return card


# ---------------------------------------------------------------- OSC
class Osc:
    def __init__(self, cfg, enabled=True):
        self.c = None
        if enabled:
            try:
                from pythonosc.udp_client import SimpleUDPClient
                self.c = SimpleUDPClient(cfg["osc"]["host"], int(cfg["osc"]["port"]))
            except ImportError:
                print("  (python-osc가 없어 OSC를 끄고 실행해요: pip install python-osc)")
        self.sent = []

    def send(self, addr, *args):
        self.sent.append((addr, args))
        if self.c:
            try:
                self.c.send_message(addr, list(args) if len(args) != 1 else args[0])
            except OSError:
                pass


# ---------------------------------------------------------------- 감지
class Tracker:
    def __init__(self, cfg, frame_wh, osc, results_dir, log=print):
        self.cfg, self.T = cfg, cfg["tune"]
        self.user_tune = cfg.get("_user_tune_keys", [])
        self.fw, self.fh = frame_wh
        self.Hm, self.Hinv = floor_homography(cfg, frame_wh)
        self.osc, self.log = osc, log
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.scale = self.T["proc_width"] / self.fw
        self.pw, self.ph = self.T["proc_width"], int(round(self.fh * self.scale))
        self.bg = None
        self.fg = None
        d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
        prm = cv2.aruco.DetectorParameters()
        prm.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
        prm.minMarkerPerimeterRate = 0.01            # 작게 찍힌 마커도
        self.aruco = cv2.aruco.ArucoDetector(d, prm)
        self.marker_obj = {int(k): v for k, v in cfg["markers"].items()}
        self.events_out = []                          # 테스트용 기록 (t, 이름, 값)
        self.reset_session()
        self.state = "IDLE"
        self.present_hist = []
        self.person = None                            # (cx_px, cy_px, contour_px, floor_xy)
        self.seen = {}                                # 마커 id -> (img_pt, floor_pt)
        self.last_absent_t = None
        self.last_pos = None
        self.relearn_until = 0.0
        self.need_clear = False                      # 퇴장 직후: 화면이 비기 전엔 새 입장 안 받음
        self.clear_since = None
        self.entry_since = None
        self.last_result = None                      # (방문 번호, 머문 시간, QR 경로, 주소) — QR 창용
        self.prev_foot_proc = None
        self.jump_since = None
        self.speed, self.dt = 0.0, 0.0
        self.prev_g, self.still_t = None, 0.0
        self.gate_since = None
        self.recent = []
        self.nadir = tuple(cfg["nadir_px"]) if cfg.get("nadir_px") else (self.fw / 2, self.fh / 2)
        Wc = cfg["floor_cm"][0]
        a, b = to_floor(self.Hinv, [[0, cfg["floor_cm"][1] / 2], [Wc, cfg["floor_cm"][1] / 2]])
        self.ppcm = float(np.hypot(*(b - a))) / Wc            # 화면 픽셀 / cm (대략)

    # -------------------------------------------- 세션
    def reset_session(self):
        self.t0 = None
        self.samples, self.events = [], []
        self.seated = False
        self.sit_since = self.stand_since = None
        self.mk = {}                                  # 마커 id -> 상태
        self.obj_cool = {}
        self.touch_count = {}
        self.next_pos_t = self.next_sample_t = 0.0
        self.near_exit = False
        self.in_exit = False
        self.exit_since = None
        self.room = None
        self.home_since = None
        self.door_sent = False

    def emit(self, t, name, *val):
        self.events_out.append((round(t, 2), name, val))
        self.osc.send(f"/home/{name}", *val)

    # -------------------------------------------- 사람 (배경 차이)
    def person_detect(self, frame, t):
        # 밝기만 보면 바닥과 밝기가 비슷한 옷을 놓치므로 색(B·G·R) 차이까지 본다
        g = cv2.resize(frame, (self.pw, self.ph), interpolation=cv2.INTER_AREA)
        g = cv2.GaussianBlur(g, (5, 5), 0).astype(np.float32)
        if self.bg is None:
            self.bg = g.copy()
            self.fg = np.zeros(g.shape[:2], np.uint8)
            return None, None
        # 조명 보정: 화면을 작은 칸으로 나눠 칸·색 채널마다 '배경 대비 밝기 비율'을 구해 맞춘다
        # (스탠드 하나만 켜지거나 색온도가 바뀌어도 사람으로 착각하지 않게). 사람 자리는 계산에서 뺀다.
        stat = cv2.dilate(self.fg, np.ones((21, 21), np.uint8)) == 0
        gn = g * self.gain_map(g, stat)[..., :]
        diff = np.abs(gn - self.bg).max(axis=2)
        fgb = diff > self.T["diff_thresh"]
        if self.T.get("shadow_remove", True):
            sg, sb = gn.sum(axis=2) + 1.0, self.bg.sum(axis=2) + 1.0
            ratio = sg / sb
            chroma = np.abs(gn / sg[..., None] - self.bg / sb[..., None]).max(axis=2)
            lo, hi = self.T["shadow_ratio"]
            shadow = (ratio > lo) & (ratio < hi) & (chroma < self.T["shadow_chroma"])
            fgb &= ~shadow
        fg = fgb.astype(np.uint8) * 255
        fg = cv2.morphologyEx(fg, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        fg = cv2.morphologyEx(fg, cv2.MORPH_CLOSE, np.ones((11, 11), np.uint8))
        fg = cv2.dilate(fg, np.ones((7, 7), np.uint8))
        if self.T.get("person_detector", "bg") == "yolo":
            ym = self.yolo_mask(frame)
            if ym is not None:
                fg = ym                                # 사람 형체만 (그림자·가구·TV 화면은 빠짐)
        self.fg = fg
        self.last_gn = gn
        cnts, _ = cv2.findContours(fg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = self.T["min_person_frac"] * self.pw * self.ph
        cands = [c for c in cnts if cv2.contourArea(c) >= min_area]
        best = None
        if cands:
            if self.state == "IN" and self.prev_foot_proc is not None:
                # 세션 중에는 '직전 위치에서 이어지는' 덩어리만 사람 (남은 물건 덩어리로 갈아타지 않게)
                pf = (float(self.prev_foot_proc[0]), float(self.prev_foot_proc[1]))
                d, c = max(((cv2.pointPolygonTest(c, pf, True), c) for c in cands), key=lambda z: z[0])
                if d > -self.T["max_jump_cm"] * self.ppcm * self.scale:
                    best = c
            else:
                best = max(cands, key=cv2.contourArea)
        person_mask = np.zeros_like(fg)
        if best is not None:
            cv2.drawContours(person_mask, [best], -1, 255, -1)
        # 배경 갱신: 사람 아닌 곳은 천천히(옮겨진 물건은 몇 초 뒤 배경으로), 사람 자리는 그대로
        idle = self.state == "IDLE"
        if t < self.relearn_until:
            a_bg, a_fg = 0.25, 0.25
        else:
            a_bg = 0.03 if idle else 0.01
            a_fg = 0.02 if idle else 0.012
        a_person = a_fg if idle else 0.0           # 빈 공간일 때 남은 덩어리는 배경으로 흡수
        if best is not None and self.prev_g is not None:
            motion = float(np.abs(g - self.prev_g).mean(axis=2)[person_mask > 0].mean())
            self.still_t = (self.still_t + self.dt) if motion < self.T["static_motion"] else 0.0
            if self.still_t > (self.T["static_seated_s"] if self.seated else self.T["static_s"]):
                a_person = a_fg * 3                    # 오래 안 움직이는 덩어리 = 그림자·남은 물건 → 배경으로
        self.prev_g = g
        rate = np.where(person_mask > 0, a_person, np.where(fg > 0, a_fg, a_bg)).astype(np.float32)
        self.bg += rate[..., None] * (gn - self.bg)
        if best is None:
            return None, fg
        M = cv2.moments(best)
        cx, cy = M["m10"] / M["m00"] / self.scale, M["m01"] / M["m00"] / self.scale
        cnt_full = (best.astype(np.float32) / self.scale).astype(np.int32)
        mode = self.T.get("point_mode") or ("foot" if self.T.get("foot_point") else "center")
        if "point_mode" not in self.user_tune and "foot_point" in self.user_tune:
            mode = "foot" if self.T["foot_point"] else "center"        # 예전 설정 파일 호환
        if mode == "foot":
            cx, cy = self.foot_of(cnt_full, (cx, cy))
        elif mode == "tip":
            cx, cy = self.tip_of(cnt_full, (cx, cy))
        elif mode == "finger":
            cx, cy = self.finger_of(frame, g, person_mask, cnt_full, (cx, cy))
        self.prev_foot_proc = (cx * self.scale, cy * self.scale)
        return (cx, cy, cnt_full), fg

    def clear_ghost(self, img_pt, radius_cm):
        """물건이 옮겨진 원래 자리의 배경을 지금 화면으로 바로 바꿔 '빈자리 잔상'을 없앤다 (사람 발 주변은 제외)."""
        if self.bg is None or getattr(self, "last_gn", None) is None:
            return
        m = np.zeros(self.bg.shape[:2], np.uint8)
        r = int(radius_cm * self.ppcm * self.scale)
        cv2.circle(m, (int(img_pt[0] * self.scale), int(img_pt[1] * self.scale)), r, 255, -1)
        if self.person is not None:
            cv2.circle(m, (int(self.person[0] * self.scale), int(self.person[1] * self.scale)), int(40 * self.ppcm * self.scale), 0, -1)
        self.bg[m > 0] = self.last_gn[m > 0]

    def gain_map(self, g, stat, cell=20):
        ph, pw = g.shape[:2]
        H2, W2 = ph // cell, pw // cell
        ratio = self.bg[:H2 * cell, :W2 * cell] / np.maximum(g[:H2 * cell, :W2 * cell], 4)
        ratio[~stat[:H2 * cell, :W2 * cell]] = np.nan
        r = ratio.reshape(H2, cell, W2, cell, 3).transpose(0, 2, 4, 1, 3).reshape(H2, W2, 3, -1)
        valid = np.isfinite(r).sum(axis=3) >= cell * cell * 0.3
        with np.errstate(all="ignore"):
            import warnings; warnings.simplefilter('ignore', RuntimeWarning)
            med = np.nanmedian(np.where(valid[..., None], r, np.nan), axis=3)
        glob = np.nanmedian(med.reshape(-1, 3), axis=0) if np.isfinite(med).any() else np.ones(3)
        glob = np.where(np.isfinite(glob), glob, 1.0)
        for c in range(3):                              # 사람이 덮은 칸은 주변 값으로 채움
            m = med[..., c]
            bad = ~np.isfinite(m)
            if bad.any():
                fill = cv2.blur(np.where(bad, 0, m).astype(np.float32), (5, 5))
                wts = cv2.blur((~bad).astype(np.float32), (5, 5))
                m[bad] = np.where(wts[bad] > 0.05, fill[bad] / np.maximum(wts[bad], 1e-6), glob[c])
        med = np.clip(med, 0.3, 3.0).astype(np.float32)
        med = cv2.GaussianBlur(med, (3, 3), 0)
        return cv2.resize(med, (pw, ph), interpolation=cv2.INTER_LINEAR)

    def yolo_mask(self, frame):
        """YOLO 분할 모델로 '사람' 모양만 찾아 감지용 크기(pw×ph)의 마스크로 돌려준다. 못 쓰면 None → 배경 방식."""
        if getattr(self, "yolo_off", False):
            return None
        if getattr(self, "yolo", None) is None:
            try:
                from ultralytics import YOLO
                self.yolo = YOLO(self.T.get("yolo_model", "yolov8n-seg.pt"))
                self.yolo_dev = "cpu"
                try:
                    import torch
                    if torch.backends.mps.is_available():
                        self.yolo_dev = "mps"
                except Exception:
                    pass
                print(f"  [사람 형체 인식] YOLO 사용 중 ({self.T.get('yolo_model')}, {self.yolo_dev})")
            except Exception as e:
                self.yolo_off = True
                print("  (YOLO를 못 불러와서 배경 차이 방식으로 감지해요. 설치: pip3 install ultralytics)", repr(e)[:120])
                return None
        try:
            r = self.yolo.predict(frame, imgsz=int(self.T.get("yolo_imgsz", 640)), conf=float(self.T.get("yolo_conf", 0.35)),
                                  classes=[0], device=self.yolo_dev, verbose=False)[0]
        except Exception as e:
            if self.yolo_dev != "cpu":
                print("  (mps에서 오류가 나서 cpu로 바꿔요)", repr(e)[:120])
                self.yolo_dev = "cpu"
                return None
            raise
        m = np.zeros((self.ph, self.pw), np.uint8)
        if r.masks is not None and len(r.masks):
            for poly in r.masks.xy:
                if len(poly) >= 3:
                    cv2.fillPoly(m, [np.int32(np.asarray(poly) * self.scale)], 255)
        elif r.boxes is not None:
            for x1, y1, x2, y2 in r.boxes.xyxy.cpu().numpy():
                cv2.rectangle(m, (int(x1 * self.scale), int(y1 * self.scale)), (int(x2 * self.scale), int(y2 * self.scale)), 255, -1)
        m = cv2.dilate(m, np.ones((5, 5), np.uint8))
        return m

    def finger_of(self, frame, g, person_mask, cnt_full, ctr):
        """손끝: ① MediaPipe 손 인식(설치돼 있고 손이 잡히면) → 검지 끝
        ② 아니면 피부색만 남겨(그림자·소매 제외) 그 덩어리의 끝"""
        self.finger_src = "blob"
        if self.T.get("use_mediapipe", False):
            tip = self.mp_tip(frame)
            if tip is not None:
                self.finger_src = "mediapipe"
                self.prev_tip = tip
                return tip
        ycc = cv2.cvtColor(np.clip(g, 0, 255).astype(np.uint8), cv2.COLOR_BGR2YCrCb)
        lo, hi = self.T.get("skin_lo", [40, 136, 77]), self.T.get("skin_hi", [255, 180, 130])
        skin = cv2.inRange(ycc, np.array(lo, np.uint8), np.array(hi, np.uint8))
        skin &= cv2.dilate(person_mask, np.ones((9, 9), np.uint8))
        skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        skin = cv2.morphologyEx(skin, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
        cs, _ = cv2.findContours(skin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cs = [c for c in cs if cv2.contourArea(c) > 0.25 * self.T["min_person_frac"] * self.pw * self.ph]
        if not cs:
            return self.tip_of(cnt_full, ctr)
        self.finger_src = "skin"
        c = max(cs, key=cv2.contourArea)
        return self.tip_of((c.astype(np.float32) / self.scale).astype(np.int32), ctr)

    def mp_tip(self, frame):
        if getattr(self, "_mp", None) is None:
            try:
                import mediapipe as mp
                self._mp = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=1, model_complexity=0,
                                                    min_detection_confidence=0.5, min_tracking_confidence=0.4)
                print("  손 인식(MediaPipe) 켜짐")
            except Exception:
                self._mp = False
                print("  (MediaPipe가 없어서 피부색으로 손끝을 찾아요. 더 정확하게: pip3 install mediapipe)")
        if not self._mp:
            return None
        sm = cv2.resize(frame, (640, int(frame.shape[0] * 640 / frame.shape[1])))
        r = self._mp.process(cv2.cvtColor(sm, cv2.COLOR_BGR2RGB))
        if not r.multi_hand_landmarks:
            return None
        lm = r.multi_hand_landmarks[0].landmark[8]                 # 8 = 검지 끝
        return float(lm.x * frame.shape[1]), float(lm.y * frame.shape[0])

    def tip_of(self, cnt, ctr, edge=24):
        """손끝: 덩어리가 화면 가장자리에 닿은 곳(팔 쪽)에서 가장 먼 끝.
        후보가 여럿이면(최대 거리의 85% 이상) 직전 손끝에 가장 가까운 것 — 손가락 사이를 오가지 않게."""
        pts = cnt.reshape(-1, 2).astype(np.float32)
        at_edge = (pts[:, 0] < edge) | (pts[:, 0] > self.fw - edge) | (pts[:, 1] < edge) | (pts[:, 1] > self.fh - edge)
        base = pts[at_edge].mean(axis=0) if at_edge.any() else np.float32(ctr)
        m2 = 3 * edge                                         # 손끝은 화면 가장자리에 있을 수 없음
        inner = (pts[:, 0] > m2) & (pts[:, 0] < self.fw - m2) & (pts[:, 1] > m2) & (pts[:, 1] < self.fh - m2)
        if not inner.any():
            return float(ctr[0]), float(ctr[1])
        q = pts[inner]
        dist = np.hypot(q[:, 0] - base[0], q[:, 1] - base[1])
        cand = q[dist >= dist.max() * self.T.get("tip_band", 0.85)]
        prev = getattr(self, "prev_tip", None)
        if prev is not None and len(cand) > 1:
            k = int(np.argmin(np.hypot(cand[:, 0] - prev[0], cand[:, 1] - prev[1])))
            tip = cand[k]
        else:
            tip = q[int(np.argmax(dist))]
        self.prev_tip = (float(tip[0]), float(tip[1]))
        return self.prev_tip

    def foot_of(self, cnt, ctr):
        """카메라 바로 아래(nadir)에 가장 가까운 덩어리 끝 = 발. 바로 아래에 서 있으면 가운데."""
        nx, ny = self.nadir
        if cv2.pointPolygonTest(cnt.reshape(-1, 1, 2).astype(np.float32), (float(nx), float(ny)), False) >= 0:
            return ctr
        pts = cnt.reshape(-1, 2).astype(np.float32)
        k = int(np.argmin(np.hypot(pts[:, 0] - nx, pts[:, 1] - ny)))
        near = pts[k]
        v = np.float32(ctr) - near
        L = float(np.hypot(*v))
        if L < 1:
            return ctr
        step = min(self.T["foot_radius_cm"] * self.ppcm, L * 0.5)
        f = near + v / L * step
        return float(f[0]), float(f[1])

    # -------------------------------------------- 마커
    def markers_detect(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        corners, ids, _ = self.aruco.detectMarkers(gray)
        seen = {}
        if ids is not None:
            for c, i in zip(corners, ids.flatten()):
                i = int(i)
                if i not in self.marker_obj:
                    continue
                ctr = c.reshape(4, 2).mean(axis=0)
                seen[i] = (ctr, to_floor(self.Hm, [ctr])[0], c.reshape(4, 2))
        return seen

    def under_person(self, img_pt):
        if self.person is None:
            return False
        hull = cv2.convexHull(self.person[2].reshape(-1, 1, 2).astype(np.float32))   # 덩어리 속 구멍(어두운 신발 위 리모컨 등) 무시
        return cv2.pointPolygonTest(hull, (float(img_pt[0]), float(img_pt[1])), True) > -self.T["cover_margin_cm"] * self.ppcm

    def touch(self, t, obj, why):
        if obj in ("spare", "spare_small"):
            obj = obj  # 예비 마커도 그대로 알림
        if t - self.obj_cool.get(obj, -99) < 2.5:
            return
        self.obj_cool[obj] = t
        self.touch_count[obj] = self.touch_count.get(obj, 0) + 1
        self.events.append((obj, t - self.t0))
        self.log(f"[{t - self.t0:6.1f}s] {NAMES_KO.get(obj, obj)} 만짐 ({why}) · {self.touch_count[obj]}번째")
        self.emit(t, "touch", obj, self.touch_count[obj])

    def update_markers(self, t):
        T = self.T
        for i, (img, fl, _c) in self.seen.items():
            m = self.mk.setdefault(i, {"base": None, "base_img": None, "last": t, "hide_t": None, "fired": False, "move_t": None, "cov": 0.0})
            m["last"] = t
            if m["base"] is None:
                m["base"], m["base_img"] = fl.copy(), img.copy()
                continue
            dist = float(np.linalg.norm(fl - m["base"]))
            if m["hide_t"] is not None:                       # 가려졌다가 다시 보임
                if dist > T["move_cm"] and not m["fired"]:
                    self.touch(t, self.marker_obj[i], "다른 자리에서 다시 보임")
                if dist > T["move_cm"]:
                    self.clear_ghost(m["base_img"], T["ghost_cm"].get(self.marker_obj[i], 25))
                m["hide_t"], m["fired"], m["move_t"], m["cov"] = None, False, None, 0.0
                m["base"], m["base_img"] = fl.copy(), img.copy()
                continue
            if dist > T["move_cm"]:
                m["move_t"] = m["move_t"] or t
                if t - m["move_t"] > 0.5:
                    self.touch(t, self.marker_obj[i], f"{dist:.0f}cm 옮겨짐")
                    self.clear_ghost(m["base_img"], T["ghost_cm"].get(self.marker_obj[i], 25))
                    m["base"], m["base_img"], m["move_t"] = fl.copy(), img.copy(), None
            else:
                m["move_t"] = None
        for i, m in self.mk.items():
            if i in self.seen or m["base"] is None:
                continue
            if m["hide_t"] is None:
                m["hide_t"] = t
            gone = t - m["hide_t"]
            covered = self.under_person(m["base_img"])
            if covered and self.speed < T["still_cms"]:
                m["cov"] = m.get("cov", 0.0) + self.dt          # 멈춘 사람 아래에 가려진 시간만 셈 (지나가는 건 제외)
            if not m["fired"] and ((not covered and gone > T["hide_free_s"]) or (covered and m.get("cov", 0.0) > T["hide_under_s"])):
                m["fired"] = True
                self.touch(t, self.marker_obj[i], "들고 있음" if covered else "집어 감/덮임")
                if not covered:
                    self.clear_ghost(m["base_img"], T["ghost_cm"].get(self.marker_obj[i], 25))

    # -------------------------------------------- 한 프레임
    def process(self, frame, t):
        T, Z = self.T, self.cfg["zones"]
        self.dt = t - getattr(self, "_t_prev", t)
        self._t_prev = t
        det, _fg = self.person_detect(frame, t)
        self.seen = self.markers_detect(frame)
        self.present_hist = (self.present_hist + [det is not None])[-6:]
        present = sum(self.present_hist) >= 4
        if det is not None and self.recent:
            last = self.recent[-1]
            v = float(np.hypot(det[0] - last[0], det[1] - last[1])) / max(self.dt, 1e-3)
            if v > self.T["gate_frac_s"] * self.fw and self.state == "IN":
                self.gate_since = self.gate_since or t
                if t - self.gate_since < 0.3:                 # 순간 점프는 무시 (직전 위치 유지)
                    det = (last[0], last[1], det[2])
            else:
                self.gate_since = None
        if det is not None:
            self.recent = (self.recent + [det[:2]])[-max(1, int(self.T["smooth_n"])):]
            med = np.median(np.float32(self.recent), axis=0)
            det = (float(med[0]), float(med[1]), det[2])
            fl = to_floor(self.Hm, [det[:2]])[0]
            if self.seated and self.person is not None and np.linalg.norm(fl - self.person[3]) > self.T["seat_hold_cm"]:
                self.jump_since = self.jump_since or t
                if t - self.jump_since < 1.0:              # 잠깐 튄 건 무시하고 앉은 자리 유지
                    det = (self.person[0], self.person[1], det[2])
                    fl = self.person[3]
            else:
                self.jump_since = None
            self.person = (det[0], det[1], det[2], fl)
            self.hist = [h for h in getattr(self, "hist", []) if t - h[0] <= 1.0] + [(t, float(fl[0]), float(fl[1]))]
            h0 = self.hist[0]
            self.speed = float(np.hypot(fl[0] - h0[1], fl[1] - h0[2]) / max(t - h0[0], 0.3))
        elif not present:
            self.person = None
            self.recent = []
            self.prev_tip = None

        if self.state == "IDLE":
            W, H = self.cfg["floor_cm"]
            if self.need_clear:                          # 방금 나간 사람이 아직 화면에 있으면 기다림
                if self.person is None and not present:
                    self.clear_since = self.clear_since or t
                    if t - self.clear_since >= T["clear_s"]:
                        self.need_clear = False
                else:
                    self.clear_since = None
                self.entry_since = None
                return
            ok_pos = False
            if self.person is not None:
                px, py = self.person[3]
                if T.get("entry_anywhere", True):
                    ok_pos = -10 <= px <= W + 10 and -10 <= py <= H + 10
                else:
                    e = T["entry_edge_cm"]
                    ok_pos = not (e < px < W - e and e < py < H - e)
            if present and ok_pos and t >= self.relearn_until:
                self.entry_since = self.entry_since or t
            else:
                self.entry_since = None
            if self.entry_since is not None and t - self.entry_since >= T.get("entry_s", 0.8):
                self.entry_since = None
                self.state = "IN"
                self.reset_session()
                self.t0 = t
                self.vid = self.next_visitor_id()
                self.log(f"\n▶ 관객 #{self.vid:04d} 입장")
                self.emit(t, "enter", self.vid)
                for i, (img, fl, _c) in self.seen.items():     # 지금 자리 = 물건 기준 위치
                    self.mk[i] = {"base": fl.copy(), "base_img": img.copy(), "last": t, "hide_t": None, "fired": False, "move_t": None, "cov": 0.0}
            return

        # ---- 세션 중
        if self.person is not None:
            self.last_absent_t = None
            x, y = self.person[3]
            self.last_pos = (x, y)
            self.near_exit = in_poly((x, y), Z["exit"], T["exit_margin_cm"]) if Z.get("exit") else False
            self.in_exit = in_poly((x, y), Z["exit"], 0) if Z.get("exit") else False
            if self.in_exit:
                self.exit_since = self.exit_since or t
                if t - self.exit_since >= T.get("exit_dwell_s", 3.0):
                    self.finish(t, f"출구에서 {T.get('exit_dwell_s', 3.0):.0f}초")
                    return
            else:
                self.exit_since = None
            room = "home" if Z.get("home") and in_poly((x, y), Z["home"], 0) else ("train" if Z.get("train") and in_poly((x, y), Z["train"], 0) else None)
            if room != self.room:
                self.room = room
                self.log(f"[{t - self.t0:6.1f}s] 구역: {room or '-'}")
            if room == "home" and not self.door_sent:
                self.home_since = self.home_since or t
                if t - self.home_since >= T.get("door_s", 0.4):
                    self.door_sent = True
                    self.log(f"[{t - self.t0:6.1f}s] 집에 들어옴 (문)")
                    self.emit(t, "door")
            elif room != "home":
                self.home_since = None
            if t >= self.next_pos_t:
                self.next_pos_t = t + T["pos_send_s"]
                self.osc.send("/home/pos", float(x), float(y))
            if t >= self.next_sample_t:
                self.next_sample_t = t + T["sample_s"]
                self.samples.append((t - self.t0, float(x), float(y), self.seated))
            on_sofa = (in_poly((x, y), Z["sofa"], T["sofa_margin_cm"] if self.seated else 0)) if Z.get("sofa") else False
            if on_sofa and not self.seated:
                self.stand_since = None
                self.sit_since = self.sit_since or t
                if t - self.sit_since > T["sit_s"]:
                    self.seated = True
                    if "sofa" not in [e[0] for e in self.events]:
                        self.events.append(("sofa", t - self.t0))
                    self.log(f"[{t - self.t0:6.1f}s] 소파에 앉음")
                    self.emit(t, "sit", 1)
            elif not on_sofa and self.seated:
                self.sit_since = None
                self.stand_since = self.stand_since or t
                if t - self.stand_since > T["stand_s"]:
                    self.seated = False
                    self.log(f"[{t - self.t0:6.1f}s] 일어남")
                    self.emit(t, "sit", 0)
            else:
                self.sit_since = self.sit_since if on_sofa else None
                self.stand_since = None
        self.update_markers(t)

        if self.person is None:
            self.last_absent_t = self.last_absent_t or t
            self.exit_since = None
            gone = t - self.last_absent_t
            if (self.near_exit and gone > T["absent_exit_s"]) or gone > T["lost_s"]:
                self.finish(t, "출구로 퇴장" if self.near_exit else "사라짐(출구 아님)")

    def next_visitor_id(self):
        f = self.results_dir / "counter.txt"
        n = int(f.read_text()) + 1 if f.exists() else 1
        f.write_text(str(n))
        return n

    def finish(self, t, why):
        stay = (self.last_absent_t or t) - self.t0
        if self.seated:
            self.emit(t, "sit", 0)
        url = build_result_url(self.cfg["result_base"], self.vid, stay, self.cfg["floor_cm"], self.cfg["zones"], self.samples, self.events)
        rid = f"{self.vid:04d}"
        qr = save_qr(url, str(self.results_dir / f"qr_{rid}.png"))
        if qr:
            save_qr(url, str(self.results_dir / "latest_qr.png"))       # 언리얼은 항상 이 파일을 읽으면 됨
        (self.results_dir / f"visit_{rid}.json").write_text(json.dumps(
            {"id": self.vid, "stay_s": round(stay, 1), "why": why, "events": self.events, "samples": self.samples, "url": url},
            ensure_ascii=False, indent=1), encoding="utf-8")
        touched = ", ".join(f"{NAMES_KO.get(k, k)} {v}번" for k, v in self.touch_count.items()) or "없음"
        self.log(f"■ 관객 #{rid} {why} · 머문 시간 {stay:.0f}초 · 만진 물건: {touched}\n  결과 주소({len(url)}자): {url[:90]}…")
        self.emit(t, "exit", float(round(stay, 1)))
        self.osc.send("/home/result", url, str((self.results_dir / "latest_qr.png").resolve()))
        self.events_out.append((round(t, 2), "result", (url,)))
        self.state = "IDLE"
        self.person = None
        self.prev_foot_proc = None
        self.present_hist = []
        self.relearn_until = t + 2.0                   # 사람이 나간 뒤 배경 빠르게 다시 익히기
        self.need_clear = True
        self.clear_since = None
        self.last_result = (self.vid, stay, qr, url, t)

    # -------------------------------------------- 화면 표시
    def draw(self, frame, t):
        out = frame.copy()
        Z = self.cfg["zones"]
        W, H = self.cfg["floor_cm"]
        fl = to_floor(self.Hinv, [[0, 0], [W, 0], [W, H], [0, H]]).astype(np.int32)
        cv2.polylines(out, [fl], True, (200, 200, 200), 2)
        for name, col in (("train", (200, 160, 90)), ("home", (60, 180, 255))):
            if Z.get(name):
                p = to_floor(self.Hinv, Z[name]).astype(np.int32)
                cv2.polylines(out, [p], True, col, 1)
                cv2.putText(out, name.upper(), tuple(p[0] + [6, 60]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, 2)
        for name, col in (("sofa", (60, 140, 255)), ("exit", (90, 220, 120))):
            if Z.get(name):
                p = to_floor(self.Hinv, Z[name]).astype(np.int32)
                ov = out.copy(); cv2.fillPoly(ov, [p], col); out = cv2.addWeighted(ov, 0.22, out, 0.78, 0)
                cv2.polylines(out, [p], True, col, 2)
                cv2.putText(out, name.upper(), tuple(p[0] + [6, 26]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, col, 2)
        if self.samples:
            pts = to_floor(self.Hinv, [(x, y) for (_, x, y, _s) in self.samples]).astype(np.int32)
            cv2.polylines(out, [pts], False, (40, 40, 255), 3)
        if self.person is not None:
            cv2.drawContours(out, [self.person[2]], -1, (255, 200, 60), 2)
            cv2.circle(out, (int(self.person[0]), int(self.person[1])), 10, (255, 200, 60), -1)
        for i, (img, flp, c) in self.seen.items():
            cv2.polylines(out, [c.astype(np.int32)], True, (0, 255, 255), 2)
            cv2.putText(out, f"{i}:{self.marker_obj.get(i)}", (int(img[0]) + 8, int(img[1]) - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        for i, m in self.mk.items():
            if i not in self.seen and m.get("base_img") is not None:
                cv2.circle(out, tuple(int(v) for v in m["base_img"]), 14, (0, 120, 255), 2)
        rec = self.state == "IN"
        txt = f"{'REC' if rec else 'WAIT'}  #{getattr(self, 'vid', 0):04d}  " + (f"{t - self.t0:5.1f}s" if rec else "")
        if rec and self.seated:
            txt += "  SEATED"
        if rec and self.exit_since is not None:
            left = max(0.0, self.T.get("exit_dwell_s", 3.0) - (t - self.exit_since))
            txt += f"  EXIT {left:.1f}"
            p = to_floor(self.Hinv, Z["exit"]).astype(np.int32)
            cv2.polylines(out, [p], True, (90, 220, 120), 6)
        if not rec and self.need_clear:
            txt = "DONE - clear the area"
        elif not rec and self.entry_since is not None:
            txt = "ENTERING..."
        cv2.rectangle(out, (0, 0), (out.shape[1], 46), (0, 0, 0), -1)
        cv2.putText(out, txt, (14, 32), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (60, 60, 255) if rec else (200, 200, 200), 2)
        cnt = "  ".join(f"{k}:{v}" for k, v in self.touch_count.items())
        cv2.putText(out, cnt, (520, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
        return out


# ---------------------------------------------------------------- 현장 설정
def run_setup(cfg, cfg_path, cap):
    ok, frame = read_first(cap)
    if not ok:
        sys.exit("카메라 화면을 못 받았어요. --camera 번호를 확인하세요 (--list-cameras).")
    win = "SETUP"
    locked = bool(cfg.get("lock_zones"))
    steps = [("floor", 4, "Click the 4 corners: 1 2 3 4 as on the map" if locked else "1) Click the 4 FLOOR corners"),
             ("sofa", 0, "2) Click SOFA area corners, then ENTER"),
             ("exit", 0, "3) Click EXIT area corners, then ENTER")]
    if locked:
        steps = steps[:1]
        print("\n[언리얼 도면 모드] 구역(기차·집·소파·출구)은 언리얼 도면에서 가져와요.")
        print("  카메라 화면에서 전시장 네 모서리를 찍어 주세요. 오른쪽 위 작은 지도의 1·2·3·4와 같은 자리예요.")
        print("  1 = 왼쪽 위(지하철 칸 입구 쪽), 2 = 오른쪽 위(지하철 칸 끝), 3 = 오른쪽 아래(소파 뒤 스탠드), 4 = 왼쪽 아래(출구 쪽)")
    mini = layout_minimap(cfg) if locked else None
    clicks = []
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, lambda e, x, y, f, p: clicks.append((x, y)) if e == cv2.EVENT_LBUTTONDOWN else None)
    print("\n[현장 설정] 화면을 클릭하세요. z: 마지막 점 취소 · ENTER: 다음 · ESC: 취소")
    res = {}
    for key, need, msg in steps:
        clicks.clear()
        print(" ", msg)
        while True:
            ok, f2 = cap.read()
            frame = f2 if ok else frame
            v = frame.copy()
            cv2.rectangle(v, (0, 0), (v.shape[1], 44), (0, 0, 0), -1)
            cv2.putText(v, msg + "  (any order OK)", (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2)
            for k, p in enumerate(clicks):
                cv2.circle(v, p, 7, (0, 200, 255), -1)
                cv2.putText(v, str(k + 1), (p[0] + 8, p[1] - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)
            if len(clicks) > 1:
                cv2.polylines(v, [np.int32(clicks)], key != "floor" or len(clicks) == 4, (0, 200, 255), 2)
            for kk, pts in res.items():
                cv2.polylines(v, [np.int32(pts)], True, (120, 255, 120), 2)
            if mini is not None:
                mh, mw = mini.shape[:2]
                if v.shape[1] > mw + 20 and v.shape[0] > mh + 60:
                    v[54:54 + mh, v.shape[1] - mw - 10:v.shape[1] - 10] = mini
            cv2.imshow(win, v)
            k = cv2.waitKey(30) & 0xFF
            if k == 27:
                sys.exit("설정 취소")
            if k == ord("z") and clicks:
                clicks.pop()
            if (need and len(clicks) >= need) or (k in (13, 10) and len(clicks) >= 3):
                res[key] = clicks[:need] if need else list(clicks)
                break
        if key == "floor" and locked:
            cfg["floor_px"] = [list(map(float, p)) for p in order_corners(res["floor"])]
            cfg["frame_size"] = [frame.shape[1], frame.shape[0]]
        elif key == "floor":
            try:
                w = float(input("   바닥 네 점 사이 가로 길이(cm)? ") or cfg["floor_cm"][0])
                h = float(input("   세로 길이(cm)? ") or cfg["floor_cm"][1])
            except ValueError:
                w, h = cfg["floor_cm"]
            cfg["floor_px"], cfg["floor_cm"] = [list(map(float, p)) for p in order_corners(res["floor"])], [w, h]
            cfg["frame_size"] = [frame.shape[1], frame.shape[0]]
    Hm, _ = floor_homography(cfg, (frame.shape[1], frame.shape[0]))
    if not locked:
        cfg["zones"] = {k: [list(map(lambda v: round(float(v), 1), p)) for p in to_floor(Hm, order_poly(res[k]))] for k in ("sofa", "exit")}
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
    cv2.destroyWindow(win)
    print(f"  저장했어요 → {cfg_path}\n  소파(cm): {cfg['zones']['sofa']}\n  출구(cm): {cfg['zones']['exit']}")


def layout_minimap(cfg, size=220):
    """셋업 화면 구석에 그릴 언리얼 도면 미니맵 (모서리 번호 1~4)"""
    W, H = cfg["floor_cm"]
    s = size / max(W, H)
    pad = 26
    img = np.full((int(H * s) + 2 * pad, int(W * s) + 2 * pad, 3), 30, np.uint8)
    P = lambda x, y: (int(pad + x * s), int(pad + y * s))
    cols = {"train": (200, 160, 90), "home": (60, 180, 255), "sofa": (60, 140, 255), "exit": (90, 220, 120)}
    for k in ("train", "home", "sofa", "exit"):
        poly = cfg.get("zones", {}).get(k)
        if poly:
            cv2.polylines(img, [np.int32([P(*p) for p in poly])], True, cols[k], 2)
            c = np.mean(np.float32(poly), axis=0)
            cv2.putText(img, k.upper(), (P(*c)[0] - 22, P(*c)[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, cols[k], 1)
    for i, (x, y) in enumerate([(0, 0), (W, 0), (W, H), (0, H)]):
        cv2.circle(img, P(x, y), 9, (0, 200, 255), -1)
        cv2.putText(img, str(i + 1), (P(x, y)[0] - 5, P(x, y)[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 2)
    cv2.rectangle(img, (0, 0), (img.shape[1] - 1, img.shape[0] - 1), (200, 200, 200), 1)
    return img


def apply_layout(cfg, path):
    """언리얼에서 뽑은 도면(바닥 크기 + 구역)을 설정에 넣는다"""
    lay = json.loads(Path(path).read_text(encoding="utf-8"))
    cfg["floor_cm"] = lay["floor_cm"]
    cfg["zones"] = lay["zones"]
    cfg["lock_zones"] = True
    cfg["layout_note"] = lay.get("note", "")
    return cfg


def read_first(cap, wait_s=8.0):
    """카메라가 첫 화면을 줄 때까지 기다린다 (아이폰 연속성 카메라는 1~2초 걸림)"""
    t0 = time.monotonic()
    n_ok, last_mean = 0, None
    while time.monotonic() - t0 < wait_s:
        ok, f = cap.read()
        if ok and f is not None:
            n_ok, last_mean = n_ok + 1, float(f.mean())
            if last_mean > 3:
                return True, f
        time.sleep(0.05)
    if not cap.isOpened():
        print("  [진단] 카메라를 아예 못 열었어요 → 번호가 없거나, 카메라 권한(시스템 설정 → 개인정보 보호 → 카메라 → 터미널)이 꺼져 있어요.")
    elif n_ok == 0:
        print("  [진단] 카메라는 열렸는데 화면이 한 장도 안 왔어요 → A7 IV가 USB 스트리밍 중인지(카메라 화면에 표시), 다른 앱(줌·OBS 등)이 쓰고 있지 않은지 확인하세요.")
    else:
        print(f"  [진단] 화면은 {n_ok}장 왔는데 전부 새까매요 (밝기 {last_mean:.1f}) → 렌즈 캡, 너무 어두운 노출(M 모드 셔터·ISO), 방 불을 확인하세요.")
    return False, None


def open_source(args, cfg):
    if args.video:
        cap = cv2.VideoCapture(args.video)
    else:
        idx = args.camera if args.camera is not None else cfg["camera"]
        cap = cv2.VideoCapture(idx, cv2.CAP_AVFOUNDATION) if sys.platform == "darwin" else cv2.VideoCapture(idx)
        w, h = cfg["frame_size"]
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    if not cap.isOpened():
        sys.exit("카메라/영상을 열 수 없어요. (맥: 시스템 설정 → 개인정보 보호 → 카메라에서 터미널 허용)")
    return cap


def main():
    ap = argparse.ArgumentParser(description="Home Sweet Home CCTV 감지")
    ap.add_argument("--config", default=str(HERE / "config.json"))
    ap.add_argument("--setup", action="store_true")
    ap.add_argument("--camera", type=int)
    ap.add_argument("--video")
    ap.add_argument("--no-osc", action="store_true")
    ap.add_argument("--headless", action="store_true", help="화면 없이 (테스트용)")
    ap.add_argument("--events-json", help="이벤트 기록을 파일로 (테스트용)")
    ap.add_argument("--save-video", help="인식 화면을 영상으로 저장")
    ap.add_argument("--save-raw", help="표시 없는 원본 화면을 영상으로 저장 (나중에 --video로 다시 시험할 때)")
    ap.add_argument("--list-cameras", action="store_true")
    ap.add_argument("--layout", help="언리얼 도면 파일(unreal_layout.json)로 구역 맞추기 — 다음 --setup에서는 네 모서리만 찍음")
    ap.add_argument("--floor-size", nargs=2, type=float, metavar=("가로cm", "세로cm"), help="바닥 크기만 바꿔 저장 (다시 클릭 안 해도 됨)")
    args = ap.parse_args()

    if args.list_cameras:
        out = HERE / "results"
        out.mkdir(exist_ok=True)
        print("카메라마다 몇 초씩 켜서 사진을 찍어요...")
        for i in range(4):
            c = cv2.VideoCapture(i, cv2.CAP_AVFOUNDATION) if sys.platform == "darwin" else cv2.VideoCapture(i)
            ok, f = False, None
            if c.isOpened():
                for _ in range(60):                       # 켜지는 데 시간이 걸리는 카메라(아이폰 등) 기다리기
                    ok, f = c.read()
                    if ok and f is not None and f.mean() > 3:
                        break
                    time.sleep(0.05)
            c.release()
            if ok and f is not None:
                path = out / f"camera_{i}.jpg"
                cv2.imwrite(str(path), f)
                print(f"  카메라 {i}: 있음 {f.shape[1]}x{f.shape[0]} → 사진: {path}")
            else:
                print(f"  카메라 {i}: 없음")
        print("사진 보기:  open results/camera_*.jpg")
        return

    cfg_path = Path(args.config)
    cfg = load_cfg(cfg_path)
    if args.layout:
        cfg = apply_layout(cfg, args.layout)
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"언리얼 도면을 넣었어요: 바닥 {cfg['floor_cm'][0]:.0f} × {cfg['floor_cm'][1]:.0f}cm, 구역 {', '.join(cfg['zones'])}")
        print("이제 --setup 으로 네 모서리만 찍으면 돼요.")
        return
    if args.floor_size:
        cfg = set_floor_size(cfg, *args.floor_size)
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"바닥 크기 {args.floor_size[0]:.0f} × {args.floor_size[1]:.0f}cm 로 저장했어요 → {cfg_path}")
        return
    cap = open_source(args, cfg)
    if args.setup:
        run_setup(cfg, cfg_path, cap)
        cfg = load_cfg(cfg_path)

    ok, frame = read_first(cap) if not args.video else cap.read()
    if not ok:
        sys.exit("첫 화면을 못 받았어요. 아이폰이 잠긴 채 가로로 놓여 있는지, 카메라 번호(--list-cameras)가 맞는지 확인하세요.")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    osc = Osc(cfg, enabled=not args.no_osc)
    tr = Tracker(cfg, (frame.shape[1], frame.shape[0]), osc, HERE / "results")
    writer = raw_writer = None
    if args.save_raw:
        raw_writer = cv2.VideoWriter(args.save_raw, cv2.VideoWriter_fourcc(*"mp4v"), 15, (frame.shape[1], frame.shape[0]))
    if args.save_video:
        writer = cv2.VideoWriter(args.save_video, cv2.VideoWriter_fourcc(*"mp4v"), fps, (frame.shape[1], frame.shape[0]))
    print(f"실행 중 · OSC → {cfg['osc']['host']}:{cfg['osc']['port']}{' (꺼짐)' if args.no_osc else ''} · 끄기: ESC / q / 창 닫기 / 터미널에서 Ctrl+C")
    import signal
    def _stop(signum, _frame):
        raise KeyboardInterrupt
    for _sig in (getattr(signal, "SIGHUP", None), signal.SIGTERM):
        if _sig is not None:
            signal.signal(_sig, _stop)                  # 터미널 창을 닫아도 영상·기록을 마무리하고 끝냄
    n, t_start = 0, time.monotonic()
    win = "Home Sweet Home - CCTV"
    shown = False
    qr_win, qr_until, qr_seen = "QR", 0.0, None
    try:
        while ok:
            t = n / fps if args.video else time.monotonic() - t_start
            if raw_writer:
                raw_writer.write(frame)
            tr.process(frame, t)
            if writer or not args.headless:
                view = tr.draw(frame, t)
                if writer:
                    writer.write(view)
                if not args.headless:
                    cv2.imshow(win, view)
                    lr = tr.last_result
                    if lr is not None and lr is not qr_seen and lr[2]:      # 새 결과 → QR 창 띄우기
                        qr_seen = lr
                        cv2.namedWindow(qr_win, cv2.WINDOW_NORMAL)
                        cv2.imshow(qr_win, qr_card(lr[0], lr[1], lr[2], lr[3]))
                        try:
                            cv2.setWindowProperty(qr_win, cv2.WND_PROP_TOPMOST, 1)
                        except Exception:
                            pass
                        qr_until = time.monotonic() + tr.T.get("qr_show_s", 20.0)
                    if qr_until and (time.monotonic() > qr_until or tr.state == "IN"):
                        cv2.destroyWindow(qr_win)
                        qr_until = 0.0
                    k = cv2.waitKey(1) & 0xFF
                    if shown and cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) < 1:
                        break                                   # 창 닫기 버튼
                    shown = True
                    if k in (27, ord("q"), ord("Q")):           # ESC는 한글 입력 상태에서도 됨
                        break
                    if k == ord("b"):
                        tr.bg = None
                        print("배경 다시 찍음")
                    if k == ord("r") and tr.state == "IN":
                        tr.finish(t, "강제 종료")
                    if k == ord("s"):
                        cv2.imwrite(str(HERE / "results" / f"snap_{int(time.time())}.png"), view)
            ok, frame = cap.read()
            n += 1
    except KeyboardInterrupt:
        print("\nCtrl+C — 기록을 저장하고 끝낼게요")
    if tr.state == "IN":
        tr.finish(n / fps if args.video else time.monotonic() - t_start, "프로그램 종료")
    if writer:
        writer.release()                                # 영상 먼저 마무리 (창 정리 중 오류가 나도 파일은 살림)
    if raw_writer:
        raw_writer.release()
    cap.release()
    try:
        cv2.destroyAllWindows()
    except cv2.error:
        pass
    if args.events_json:
        Path(args.events_json).write_text(json.dumps({"events": tr.events_out, "osc": [(a, list(v)) for a, v in osc.sent if a != "/home/pos"]}, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
