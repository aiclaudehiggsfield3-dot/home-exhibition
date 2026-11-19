# -*- coding: utf-8 -*-
"""시연 기록: 프로그램을 켤 때마다 results/.../sessions/<날짜_시각>/ 폴더를 만들어 자동으로 남긴다.

  시연기록.html   한눈에 보는 기록 (관객별 머문 시간·만진 물건·소리 세 갈래·동선 그림·QR·결과 페이지 링크, 영상)
  시연화면.mp4    시연 프로그램 화면 녹화 (게임식: 도면+판 / 카메라: CCTV 인식 화면)
  로그.txt        프로그램이 출력한 모든 줄 (시각 포함)
  신호.csv        언리얼로 보낸 OSC 신호 (위치·방향은 0.25초마다만)
  동선_0001.png · qr_0001.png · visit_0001.json   관객별
  언리얼로그.txt  언리얼을 함께 켰을 때 그 로그
"""
import csv
import html
import json
import shutil
import time
from pathlib import Path

import cv2
import numpy as np

FONTS = ("/System/Library/Fonts/AppleSDGothicNeo.ttc", "/System/Library/Fonts/Supplemental/AppleGothic.ttf",
         "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc")
FONT = next((f for f in FONTS if Path(f).exists()), None)
NAMES_KO = {"blanket": "담요", "remote": "리모컨", "tv": "TV", "sofa": "소파"}
ZONE_COL = {"train": (200, 160, 90), "home": (60, 160, 230), "sofa": (60, 90, 200), "exit": (80, 200, 120)}


def _text(img, items):
    try:
        from PIL import Image, ImageDraw, ImageFont
        if not FONT:
            raise ImportError
        im = Image.fromarray(img[:, :, ::-1]); d = ImageDraw.Draw(im)
        for s, xy, size, col in items:
            d.text(xy, s, font=ImageFont.truetype(FONT, size), fill=(col[2], col[1], col[0]))
        return np.array(im)[:, :, ::-1].copy()
    except Exception:
        for s, xy, size, col in items:
            cv2.putText(img, s.encode("ascii", "replace").decode(), (xy[0], xy[1] + size), cv2.FONT_HERSHEY_SIMPLEX, size / 30, col, 1)
        return img


class SessionRecorder:
    def __init__(self, results_dir, kind, cfg, title):
        self.dir = Path(results_dir) / "sessions" / time.strftime("%Y-%m-%d_%H%M%S")
        self.dir.mkdir(parents=True, exist_ok=True)
        self.kind, self.cfg, self.title = kind, cfg, title
        self.t_wall = time.time()
        self.logf = open(self.dir / "로그.txt", "a", encoding="utf-8")
        self.evf = open(self.dir / "신호.csv", "w", newline="", encoding="utf-8-sig")
        self.ev = csv.writer(self.evf)
        self.ev.writerow(["시각", "경과(초)", "주소", "값"])
        self.visits, self.notes = [], []
        self.vw, self.video_name, self.video_note, self.nframe = None, None, "", 0
        self._last = {}
        self.unreal_log = self.dir / "언리얼로그.txt"
        self.unreal_status = "-"
        self.log(f"=== {title} 시작 · 기록 폴더 {self.dir}")

    # ---------------- 글·신호
    def log(self, msg):
        stamp = time.strftime("%H:%M:%S")
        for line in str(msg).rstrip("\n").split("\n"):
            self.logf.write(f"{stamp}  {line}\n")
        self.logf.flush()

    def wrap_log(self, fn):
        def both(msg):
            fn(msg)
            self.log(msg)
        return both

    def attach_osc(self, osc):
        orig = osc.send
        every = {"/home/pos": 0.25, "/home/look": 0.25, "/home/level": 1.0}
        def send(addr, *args):
            now = time.time()
            gap = every.get(addr)
            if gap is None or now - self._last.get(addr, 0) >= gap:
                self._last[addr] = now
                self.ev.writerow([time.strftime("%H:%M:%S", time.localtime(now)), f"{now - self.t_wall:.2f}", addr,
                                  " ".join(f"{a:.2f}" if isinstance(a, float) else str(a) for a in args)])
            return orig(addr, *args)
        osc.send = send

    def attach_tracker(self, tr):
        orig = tr.finish
        def finish(t, why):
            orig(t, why)
            try:
                self.on_visit(tr, why)
            except Exception as e:                       # 기록이 시연을 멈추게 하지 않게
                self.log(f"(시연 기록 오류: {e})")
        tr.finish = finish

    # ---------------- 영상
    def frame(self, bgr, every=2, fps=15):
        self.nframe += 1
        if self.nframe % every:
            return
        if self.vw is None:
            h, w = bgr.shape[:2]
            # 맥 OpenCV에서 avc1(H.264)은 프로그램을 통째로 죽이는 경우가 있어서 mp4v만 씀 (QuickTime·Safari에서 재생)
            for fourcc, name, note in (("mp4v", "시연화면.mp4", "Chrome에서 안 나오면 QuickTime·Safari로 열어 주세요"),
                                       ("MJPG", "시연화면.avi", "VLC 등으로 열어 주세요")):
                vw = cv2.VideoWriter(str(self.dir / name), cv2.VideoWriter_fourcc(*fourcc), fps, (w, h))
                if vw.isOpened():
                    self.vw, self.video_name, self.video_note = vw, name, note
                    break
            if self.vw is None:
                self.video_name = False
        if self.vw:
            self.vw.write(bgr)

    # ---------------- 관객
    def on_visit(self, tr, why):
        rid = f"{tr.vid:04d}"
        src = tr.results_dir / f"visit_{rid}.json"
        data = json.loads(src.read_text(encoding="utf-8")) if src.exists() else {}
        shutil.copy(src, self.dir / src.name) if src.exists() else None
        qr = tr.results_dir / f"qr_{rid}.png"
        if qr.exists():
            shutil.copy(qr, self.dir / qr.name)
        img = self.draw_path(data, tr)
        cv2.imwrite(str(self.dir / f"동선_{rid}.png"), img)
        stay = float(data.get("stay_s", 0))
        self.visits.append({
            "id": rid, "in": time.strftime("%H:%M:%S", time.localtime(time.time() - stay)), "stay": stay, "why": why,
            "touch": dict(tr.touch_count), "layers": data.get("layers_s", {}), "url": data.get("url", ""),
            "qr": qr.name if qr.exists() else "", "path": f"동선_{rid}.png",
            "seated": any(s[3] for s in data.get("samples", []) if len(s) > 3)})
        self.write_report()

    def draw_path(self, data, tr):
        W, H = self.cfg["floor_cm"]
        S, P = 2, 40
        img = np.full((int(H * S + P * 2), int(W * S + P * 2), 3), 250, np.uint8)
        c = lambda x, y: (int(P + x * S), int(P + y * S))
        cv2.rectangle(img, c(0, 0), c(W, H), (215, 215, 215), -1)
        labels = []
        for k, col in ZONE_COL.items():
            poly = self.cfg["zones"].get(k)
            if poly:
                pts = np.int32([c(x, y) for x, y in poly])
                over = img.copy(); cv2.fillPoly(over, [pts], col)
                img = cv2.addWeighted(over, 0.25, img, 0.75, 0)
                cv2.polylines(img, [pts], True, col, 2)
                labels.append(({"train": "지하철 칸", "home": "집", "sofa": "소파", "exit": "출구"}[k], (int(pts[:, 0].min()) + 4, int(pts[:, 1].min()) + 2), 14, (70, 70, 70)))
        tx, ty = getattr(tr, "tv_pos", (71, 186))
        cv2.rectangle(img, c(tx - 15, ty - 22), c(tx + 15, ty + 22), (60, 90, 130), -1)
        labels.append(("TV", (c(tx, ty)[0] - 9, c(tx, ty)[1] - 9), 13, (255, 255, 255)))
        sm = [s for s in data.get("samples", []) if len(s) >= 3]
        if len(sm) > 1:
            T = max(sm[-1][0], 1e-6)
            for a, b in zip(sm, sm[1:]):
                col = cv2.applyColorMap(np.uint8([[int(255 * b[0] / T)]]), cv2.COLORMAP_PLASMA)[0, 0].tolist()
                cv2.line(img, c(a[1], a[2]), c(b[1], b[2]), col, 3, cv2.LINE_AA)
            cv2.circle(img, c(sm[0][1], sm[0][2]), 7, (40, 160, 40), -1)
            cv2.circle(img, c(sm[-1][1], sm[-1][2]), 7, (40, 40, 200), -1)
            used = {}
            for name, te in data.get("events", []):
                s = min(sm, key=lambda q: abs(q[0] - te))
                p = c(s[1], s[2])
                k = (p[0] // 20, p[1] // 20)                  # 같은 자리면 글자를 한 줄씩 내려 씀
                row = used.get(k, 0); used[k] = row + 1
                cv2.circle(img, p, 9, (0, 170, 255), 2)
                labels.append((f"{NAMES_KO.get(name, name)} {te:.0f}초", (p[0] + 12, p[1] - 10 + row * 17), 14, (0, 110, 200)))
        labels.append((f"관객 #{data.get('id', '?')} · {float(data.get('stay_s', 0)):.0f}초 · 초록=입장 빨강=퇴장 · 선 색: 처음(보라)→끝(노랑)",
                       (8, img.shape[0] - P + 10), 13, (60, 60, 60)))
        return _text(img, labels)

    # ---------------- 기록 페이지
    def write_report(self, final=False):
        e = html.escape
        n = len(self.visits)
        avg = sum(v["stay"] for v in self.visits) / n if n else 0
        when = time.strftime("%Y-%m-%d %H:%M", time.localtime(self.t_wall))
        dur = time.time() - self.t_wall
        rows = []
        for v in self.visits:
            touch = ", ".join(f"{NAMES_KO.get(k, k)} {c}번" for k, c in v["touch"].items()) or "없음"
            L = v["layers"]
            rows.append(f"""<section class="v"><div class="vh"><b>관객 #{v['id']}</b><span>{v['in']} 입장 · <b>{v['stay']:.0f}초</b> 머묾 · {e(v['why'])}</span></div>
<div class="vb"><img class="path" src="{e(v['path'])}" alt="동선"><div class="info">
<table><tr><th>만진 물건</th><td>{e(touch)}</td></tr><tr><th>소파에 앉음</th><td>{'예' if v['seated'] else '아니요'}</td></tr>
<tr><th>소리 세 갈래</th><td>소파 {L.get('sofa', 0):.0f}초 · TV {L.get('tv', 0):.0f}초 · 담요 {L.get('blanket', 0):.0f}초</td></tr></table>
{f'<img class="qr" src="{e(v["qr"])}" alt="QR">' if v['qr'] else ''}
{f'<p><a href="{e(v["url"])}" target="_blank">관객 결과 페이지 (동선 애니메이션) 열기 →</a></p>' if v['url'] else ''}</div></div></section>""")
        video = ""
        if self.video_name:
            note = f" <small>({e(self.video_note)})</small>" if self.video_note else ""
            video = f'<h2>시연 화면</h2><video src="{e(self.video_name)}" controls preload="metadata"></video><p><a href="{e(self.video_name)}">{e(self.video_name)}</a>{note}</p>'
        files = " · ".join(f'<a href="{f}">{f}</a>' for f in ("로그.txt", "신호.csv") + (("언리얼로그.txt",) if self.unreal_log.exists() else ()))
        notes = "".join(f"<li>{e(x)}</li>" for x in self.notes)
        doc = f"""<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>시연 기록 {when}</title><style>
body{{font-family:-apple-system,"Apple SD Gothic Neo",sans-serif;margin:0;background:#f6f2ec;color:#2a2622}}
.w{{max-width:980px;margin:0 auto;padding:28px 20px 60px}} h1{{font-size:26px;margin:0 0 4px}} h2{{font-size:19px;margin:28px 0 10px}}
.sum{{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}} .sum div{{background:#fff;border-radius:12px;padding:12px 16px;min-width:120px}}
.sum b{{display:block;font-size:24px}} .v{{background:#fff;border-radius:14px;padding:14px 16px;margin:12px 0}}
.vh{{display:flex;justify-content:space-between;gap:10px;flex-wrap:wrap;margin-bottom:10px}} .vb{{display:flex;gap:16px;flex-wrap:wrap}}
.path{{width:340px;max-width:100%;border-radius:8px}} .qr{{width:120px;border-radius:6px}} table{{border-collapse:collapse;margin-bottom:8px}}
th{{text-align:left;color:#7a6f63;font-weight:500;padding:4px 12px 4px 0}} td{{padding:4px 0}} video{{width:100%;border-radius:10px;background:#000}}
.mute{{color:#7a6f63;font-size:13px}} a{{color:#b5532a}}</style></head><body><div class="w">
<h1>Home Sweet Home · 시연 기록</h1><p class="mute">{when} · {e(self.title)} · {'끝남' if final else '진행 중 (관객이 나갈 때마다 갱신)'} · 언리얼 {e(self.unreal_status)}</p>
<div class="sum"><div>관객<b>{n}명</b></div><div>평균 머문 시간<b>{avg:.0f}초</b></div><div>시연 시간<b>{dur / 60:.1f}분</b></div>
<div>앉은 관객<b>{sum(v['seated'] for v in self.visits)}명</b></div></div>
{video}<h2>관객별 기록</h2>{''.join(rows) or '<p class="mute">아직 나간 관객이 없어요.</p>'}
{f'<h2>메모</h2><ul>{notes}</ul>' if notes else ''}<h2>파일</h2><p>{files}</p></div></body></html>"""
        (self.dir / "시연기록.html").write_text(doc, encoding="utf-8")

    def close(self):
        if self.vw:
            self.vw.release()
            self.vw = None
        if self.video_name is False:
            self.notes.append("영상 저장기를 열지 못해 시연 화면 영상은 없어요.")
        self.log("=== 끝")
        self.write_report(final=True)
        self.logf.close()
        self.evf.close()
        return self.dir / "시연기록.html"
