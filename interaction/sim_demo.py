#!/usr/bin/env python3
"""가상 시연 영상 만들기 — 카메라 없이 home_tracker.py 인식을 시험하기 위한 합성 영상.

  python3 sim_demo.py                → sim_demo.mp4 + sim_truth.json + sim_config.json
  python3 home_tracker.py --video sim_demo.mp4 --config sim_config.json

위에서 내려다본 바닥(340×190cm)에 소파·담요(마커 1·3)·리모컨(마커 2)·출구를 두고,
사람이 들어와 앉고, 담요를 옮기고, 리모컨을 들었다 놓고, 출구로 나간다.
까다로운 조건: 살짝 기운 카메라 · 원근으로 늘어지는 몸 · 조명 켜짐 · 노이즈/압축 · 작은 리모컨 마커.
"""
import json, math
from pathlib import Path
import cv2
import numpy as np

HERE = Path(__file__).resolve().parent
FPS, PX = 15, 4                       # 바닥 그림: 1cm = 4px
FW, FH = 340, 190                     # 바닥 크기(cm)
MARGIN = 70                           # 바닥 바깥까지 그려 둘 여백(cm)
OUT_W, OUT_H = 1920, 1080
CAM_H, BODY_H = 2.6, 1.65             # 카메라 높이, 사람 키(m) — 원근 늘어짐 계산용
NADIR = np.array([170.0, 95.0])       # 카메라 바로 아래 바닥 지점(cm)
# 바닥 네 모서리가 화면에 찍히는 위치 (약간 기운 카메라)
FLOOR_IMG = np.float32([[205, 92], [1735, 120], [1790, 1000], [150, 978]])

rng = np.random.default_rng(7)
d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)


def world_px(x, y):
    return int(round((x + MARGIN) * PX)), int(round((y + MARGIN) * PX))


def base_floor():
    w, h = (FW + 2 * MARGIN) * PX, (FH + 2 * MARGIN) * PX
    img = np.full((h, w, 3), (92, 98, 104), np.uint8)               # 바깥 (콘크리트)
    x0, y0 = world_px(0, 0); x1, y1 = world_px(FW, FH)
    wood = np.full((y1 - y0, x1 - x0, 3), (70, 108, 150), np.uint8)
    for k in range(0, wood.shape[0], 9 * PX):                        # 마루 줄
        wood[k:k + 2] = (60, 92, 128)
    wood = cv2.add(wood, rng.integers(0, 14, wood.shape, dtype=np.uint8))
    img[y0:y1, x0:x1] = wood
    cv2.rectangle(img, world_px(95, 45), world_px(205, 150), (196, 210, 222), -1)    # 러그
    cv2.rectangle(img, world_px(250, 35), world_px(335, 135), (60, 95, 190), -1)     # 소파(위에서)
    cv2.rectangle(img, world_px(318, 35), world_px(335, 135), (45, 75, 160), -1)     # 등받이
    cv2.rectangle(img, world_px(0, 150), world_px(60, 190), (80, 170, 110), 6)        # 출구 테이프
    cv2.rectangle(img, world_px(2, 60), world_px(40, 110), (150, 150, 150), -1)      # TV장
    return img


def paste_marker(img, mid, cx, cy, size_cm, angle=0.0, pad_cm=None):
    pad_cm = pad_cm if pad_cm is not None else size_cm * 0.12
    s = int(size_cm * PX)
    m = cv2.aruco.generateImageMarker(d, mid, s)
    p = int(pad_cm * PX)
    tile = cv2.copyMakeBorder(m, p, p, p, p, cv2.BORDER_CONSTANT, value=255)
    tile = cv2.cvtColor(tile, cv2.COLOR_GRAY2BGR)
    tile = (tile.astype(np.float32) * np.array([0.92, 0.95, 0.97])).astype(np.uint8)    # 종이 약간 누렇게
    R = cv2.getRotationMatrix2D((tile.shape[1] / 2, tile.shape[0] / 2), angle, 1.0)
    T = tile.shape[0]
    diag = int(T * 1.5)
    R[:, 2] += (diag - T) / 2
    rot = cv2.warpAffine(tile, R, (diag, diag), borderValue=(0, 0, 0))
    mask = cv2.warpAffine(np.full((T, T), 255, np.uint8), R, (diag, diag))
    X, Y = world_px(cx, cy)
    x0, y0 = X - diag // 2, Y - diag // 2
    roi = img[y0:y0 + diag, x0:x0 + diag]
    roi[mask > 0] = rot[mask > 0]


def draw_blanket(img, x, y, spread):
    w, h = (36, 30) if not spread else (70, 50)
    cv2.rectangle(img, world_px(x - w / 2, y - h / 2), world_px(x + w / 2, y + h / 2), (124, 143, 47), -1)
    paste_marker(img, 1, x - w / 2 + 8, y - h / 2 + 8, 10, angle=8 if spread else 0)
    if spread:
        paste_marker(img, 3, x + w / 2 - 8, y + h / 2 - 8, 10, angle=-6)


def draw_remote(img, x, y, ang):
    R = cv2.boxPoints(((float((x + MARGIN) * PX), float((y + MARGIN) * PX)), (6 * PX, 18 * PX), ang))
    cv2.fillPoly(img, [R.astype(np.int32)], (30, 30, 30))
    paste_marker(img, 2, x, y, 5, angle=ang, pad_cm=0.5)


def draw_person(img, feet, seated):
    """위에서 본 사람: 발 자리에서 카메라 반대쪽으로 원근 늘어짐."""
    feet = np.array(feet, float)
    h = 1.25 if seated else BODY_H
    k = h / (CAM_H - h)
    head = feet + (feet - NADIR) * k
    v = head - feet
    L = np.linalg.norm(v)
    n = np.array([-v[1], v[0]]) / L if L > 1e-3 else np.array([1.0, 0.0])
    sh = 24 if not seated else 28
    poly = [feet + n * 14, feet + v * 0.55 + n * sh, head + n * 10, head - n * 10, feet + v * 0.55 - n * sh, feet - n * 14]
    pts = np.int32([world_px(*p) for p in poly])
    shadow = pts + np.int32([10 * PX // 2, 6 * PX // 2])
    ov = img.copy(); cv2.fillPoly(ov, [shadow], (40, 45, 50)); img[:] = cv2.addWeighted(ov, 0.35, img, 0.65, 0)
    cv2.fillPoly(img, [pts], (52, 56, 140))                                     # 상의
    cv2.circle(img, world_px(*feet), 13 * PX, (40, 40, 48), -1)                 # 발/하체
    cv2.circle(img, world_px(*head), 11 * PX, (40, 50, 70), -1)                 # 머리


def lerp_path(pts, t):
    """[(t, x, y), ...] 구간 선형 보간"""
    for (t0, x0, y0), (t1, x1, y1) in zip(pts, pts[1:]):
        if t0 <= t <= t1:
            a = (t - t0) / max(t1 - t0, 1e-6)
            return x0 + (x1 - x0) * a, y0 + (y1 - y0) * a
    return None


def main():
    # 관객 1: 위 가운데(문)로 들어와 → 리모컨 위를 지나감 → 소파 → 출구(왼쪽 아래)
    P1 = [(3.0, 260, -40), (5.0, 250, 20), (8.0, 200, 70), (11.0, 222, 30), (13.0, 262, 70), (14.0, 285, 82),
          (31.0, 285, 82), (33.0, 230, 120), (36.0, 40, 172), (38.0, -60, 205)]
    P2 = [(45.0, 260, -40), (48.0, 180, 80), (52.0, 35, 172), (54.0, -60, 205)]
    seated = (14.0, 31.0)
    END = 60.0
    W, H = (FW + 2 * MARGIN) * PX, (FH + 2 * MARGIN) * PX
    src = np.float32([world_px(0, 0), world_px(FW, 0), world_px(FW, FH), world_px(0, FH)])
    Hw = cv2.getPerspectiveTransform(src, FLOOR_IMG)
    base = base_floor()
    vw = cv2.VideoWriter(str(HERE / "sim_demo.mp4"), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (OUT_W, OUT_H))
    yy, xx = np.mgrid[0:OUT_H, 0:OUT_W].astype(np.float32)
    vign = 1 - 0.22 * (((xx - OUT_W / 2) / (OUT_W / 2)) ** 2 + ((yy - OUT_H / 2) / (OUT_H / 2)) ** 2)
    glow = np.exp(-(((xx - 1650) / 700) ** 2 + ((yy - 150) / 600) ** 2)).astype(np.float32)   # 스탠드 빛
    truth = []
    n = int(END * FPS)
    for f in range(n):
        t = f / FPS
        img = base.copy()
        # 담요: 소파 옆 바닥 → 18초에 무릎으로 펼침
        if t < 18.0:
            draw_blanket(img, 228, 125, False)
        else:
            draw_blanket(img, 262, 86, True)
        # 리모컨: 소파 팔걸이 옆 → 22~28초 손에 듦(안 보임) → 28초 다른 자리 → 31초 20cm 밀림
        if t < 22.0:
            draw_remote(img, 222, 30, 15)
        elif 28.0 <= t < 31.0:
            draw_remote(img, 240, 140, -20)
        elif t >= 31.0:
            draw_remote(img, 222, 154, -10)
        person = lerp_path(P1, t) or lerp_path(P2, t)
        if person:
            is_seat = seated[0] <= t <= seated[1]
            draw_person(img, person, is_seat)
            if 22.0 <= t < 28.0:     # 손에 든 리모컨(마커는 손바닥 쪽이라 안 보임)
                cv2.circle(img, world_px(person[0] - 22, person[1] + 6), 4 * PX, (30, 30, 30), -1)
        frame = cv2.warpPerspective(img, Hw, (OUT_W, OUT_H), flags=cv2.INTER_AREA, borderValue=(40, 40, 40))
        # 조명: 처음엔 어둡고(0.72) 첫 입장 직후 0.6초 동안 켜짐 + 스탠드 쪽 따뜻한 빛
        k = float(np.clip((t - 3.4) / 0.6, 0, 1)) if t < 40 else float(np.clip(1 - (t - 40) / 1.0, 0, 1)) if t < 44 else float(np.clip((t - 45.2) / 0.6, 0, 1))
        gain = (0.72 + 0.28 * k) * vign * (1 + 0.18 * k * glow)
        fr = frame.astype(np.float32) * gain[..., None]
        fr[..., 2] *= 1 + 0.06 * k                                   # 조명 켜지면 살짝 따뜻하게
        fr += rng.normal(0, 4.0, fr.shape).astype(np.float32)        # 센서 노이즈
        frame = np.clip(fr, 0, 255).astype(np.uint8)
        frame = cv2.GaussianBlur(frame, (3, 3), 0.7)
        ok, enc = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 78])      # 압축
        frame = cv2.imdecode(enc, cv2.IMREAD_COLOR)
        vw.write(frame)
        truth.append({"t": round(t, 3), "feet": person, "seated": bool(person and seated[0] <= t <= seated[1])})
        if f in (int(2 * FPS), int(20 * FPS), int(24 * FPS), int(35 * FPS)):
            cv2.imwrite(str(HERE / f"sim_frame_{int(t):02d}s.jpg"), frame)
    vw.release()
    (HERE / "sim_truth.json").write_text(json.dumps({
        "fps": FPS, "nadir_cm": NADIR.tolist(),
        "expected": [
            "관객1 입장(~3.1s)", "8~11s 리모컨 위 지나감 → 만짐 아님", "소파 앉음(~15s)", "담요 만짐(~18.5s)",
            "리모컨 만짐 1(들고 있음 ~26s)", "리모컨 28s 내려놓음 → 중복 없음", "리모컨 만짐 2(31s 밀림)",
            "일어남(~33s)", "출구 퇴장(~38s)", "관객2 입장(~45s)", "관객2 퇴장(~54s), 만짐 없음"],
        "frames": truth}, ensure_ascii=False), encoding="utf-8")
    # 이 영상에 맞는 현장 설정(설정 화면에서 찍은 것과 같은 값)
    nadir_img = cv2.perspectiveTransform(np.float32([[world_px(*NADIR)]]), Hw)[0][0]
    cfg = {"floor_px": FLOOR_IMG.tolist(), "floor_cm": [FW, FH], "frame_size": [OUT_W, OUT_H],
           "nadir_px": [float(nadir_img[0]), float(nadir_img[1])],
           "zones": {"sofa": [[250, 35], [335, 35], [335, 135], [250, 135]], "exit": [[0, 150], [60, 150], [60, 190], [0, 190]]}}
    (HERE / "sim_config.json").write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    print("만듦: sim_demo.mp4, sim_truth.json, sim_config.json", n, "프레임")


if __name__ == "__main__":
    main()
