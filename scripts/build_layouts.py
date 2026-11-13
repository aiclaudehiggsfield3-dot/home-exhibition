# -*- coding: utf-8 -*-
"""
전시 공간 4가지 배치를 Unreal 레벨로 한 번에 만드는 스크립트 (UE 5.4)

실행: Output Log 입력칸(Cmd)에
  py "/Users/jiwon/Documents/Unreal Projects/AICLASS_prototype1/Scripts/build_layouts.py"

만들어지는 레벨 (콘텐츠 브라우저 > Exhibition > Maps)
  L_Current : 기존 계획 (A 120 / B 180, B 화면 220)
  L_Opt1    : 안 1. 화면 축소 (B 화면 150)
  L_Opt2    : 안 2. 가벽 이동 (A 90 / B 210)
  L_Opt3    : 안 3. 가로로 나누기 (A 300x100 / B 300x200)
  L_Opt4    : 안 4. 안 3 수정 (B 영상 왼쪽 벽, 소파 오른쪽, 출구 아래쪽 벽 왼쪽)

영상
  Content/Movies/A_society.mp4 → 모든 레벨의 A(사회) 화면
  Content/Movies/B_home.mp4    → 모든 레벨의 B(집) 화면
  같은 이름으로 파일만 바꿔 넣으면 네 레벨 모두 새 영상으로 재생됩니다.
  Play(재생)를 누르면 자동 재생 + 반복됩니다.

좌표 (위에서 본 배치도 기준, 단위 cm)
  X = 가로 (왼쪽 0 → 오른쪽 300), Y = 세로 (위쪽 0 → 아래쪽 300), Z = 높이
"""
import unreal

# =====================================================================
# 1. 공통 설정
# =====================================================================
BUILD = ["Current", "Opt1", "Opt2", "Opt3", "Opt4"]   # 만들 레벨. 하나만 다시 지으려면 ["Opt3"]처럼
OPEN_AFTER = "Current"                          # 다 지은 뒤 열어 둘 레벨

ROOM, T, H, F = 300, 10, 240, 2     # 공간 한 변, 벽 두께, 벽 높이, 바닥 윗면 높이
DW, DH = 80, 210                    # 문 폭, 문 높이
TOP = F + H

EXPOSURE = 0.0         # 노출(밝기) 보정. +1 = 두 배 밝게, -1 = 절반. 영상이 너무 밝거나 어두우면 조절
VIDEO_A = "Movies/A_society.mp4"
VIDEO_B = "Movies/B_home.mp4"

ROOT = "/Game/Exhibition"
PREFIX = "EX_"
OVERHEAD_EYE = unreal.Vector(150, 270, 540)   # 부감샷 시점 위치 (방 위에서 살짝 비스듬히 내려다봄)

COLORS = {
    "A_Wall": (0.32, 0.37, 0.42), "A_Floor": (0.18, 0.19, 0.21),
    "B_Wall": (0.85, 0.74, 0.60), "B_Floor": (0.45, 0.30, 0.18),
    "Ground": (0.05, 0.05, 0.05), "Ceiling": (0.80, 0.80, 0.78),
    "Door": (0.55, 0.35, 0.22), "Sofa": (0.65, 0.28, 0.14),
    "Rug": (0.90, 0.82, 0.68), "Device": (0.08, 0.08, 0.08),
}

# =====================================================================
# 2. 배치 정의
#    box: (이름, x0, x1, y0, y1, z0, z1, 색 키)
#    screen: (이름, 영상, 중심 x, 중심 y, 중심 z, 폭, 높이, 바라보는 방향 yaw)
#            yaw 0 = 화면 앞면이 왼쪽(-X)을 봄, yaw 90 = 위쪽(-Y)을 봄
# =====================================================================
def wall_x(name, x, y0, y1, col, z0=F, z1=TOP):
    return (name, x - T / 2, x + T / 2, y0, y1, z0, z1, col)

def wall_y(name, y, x0, x1, col, z0=F, z1=TOP):
    return (name, x0, x1, y - T / 2, y + T / 2, z0, z1, col)

def sofa_facing_right(x0, y0, length=160):
    """등받이가 왼쪽, 앉으면 오른쪽(+X)을 바라보는 소파"""
    x1, y1 = x0 + 75, y0 + length
    return [("Sofa_Seat", x0, x1, y0, y1, F + 1, F + 45, "Sofa"),
            ("Sofa_Back", x0, x0 + 18, y0, y1, F + 45, F + 85, "Sofa"),
            ("Sofa_Arm_1", x0, x1, y0, y0 + 15, F + 45, F + 65, "Sofa"),
            ("Sofa_Arm_2", x0, x1, y1 - 15, y1, F + 45, F + 65, "Sofa")]


def vertical_split(split, b_screen_w):
    """기존 계획 / 안 1 / 안 2: 가벽이 세로로 서는 배치"""
    S = split
    sofa_x = S + 15
    boxes = [
        ("Floor_A", 0, S, 0, ROOM, F - 5, F, "A_Floor"),
        ("Floor_B", S, ROOM, 0, ROOM, F - 5, F, "B_Floor"),
        wall_x("Wall_Left", 0, 0, ROOM, "A_Wall"),
        wall_x("Wall_Right_Screen", ROOM, 0, ROOM, "B_Wall"),
        wall_y("Wall_Bottom_A", ROOM, 0, S, "A_Wall"),
        wall_y("Wall_Bottom_B", ROOM, S, ROOM, "B_Wall"),
        wall_y("Wall_Top_A", 0, 80, S, "A_Wall"),                 # 입구: 위쪽 벽 0~80
        wall_y("Wall_Top_B_1", 0, S, 200, "B_Wall"),              # 출구: 위쪽 벽 200~280
        wall_y("Wall_Top_B_2", 0, 280, ROOM, "B_Wall"),
        wall_y("Wall_Top_ExitHeader", 0, 200, 280, "B_Wall", z0=F + DH),
        wall_x("Partition_1", S, 0, 210, "A_Wall"),               # 가벽 문: 210~290
        wall_x("Partition_2", S, 290, ROOM, "A_Wall"),
        wall_x("Partition_DoorHeader", S, 210, 290, "A_Wall", z0=F + DH),
        ("Door_Partition", S + 5, S + 5 + DW, 284, 288, F, F + DH, "Door"),   # 열린 상태
        ("Door_Exit", 274, 278, -T / 2 - DW, -T / 2, F, F + DH, "Door"),
        ("Rug", S + 10, 280, 30, 270, F, F + 1, "Rug"),
        ("Projector_A", 10, 40, 92, 118, TOP - 31, TOP - 19, "Device"),
        ("Projector_B", sofa_x + 15, sofa_x + 45, 137, 163, TOP - 25, TOP - 13, "Device"),
        ("Speaker_A", 15, 30, 270, 285, F, F + 30, "Device"),
        ("Speaker_B_1", 275, 290, 15, 30, F, F + 30, "Device"),
        ("Speaker_B_2", 275, 290, 270, 285, F, F + 30, "Device"),
    ] + sofa_facing_right(sofa_x, 70)
    a_w = 190
    screens = [
        ("Screen_A_Society", VIDEO_A, S - T / 2 - 1, 105, F + 125, a_w, a_w * 9 / 16, 0),
        ("Screen_B_Home", VIDEO_B, ROOM - T / 2 - 1, 150, F + 125, b_screen_w, b_screen_w * 9 / 16, 0),
    ]
    lights = [("Light_A_Cold", S / 2, 150, TOP - 20, 6500, 2),
              ("Light_B_Warm_1", 250, 280, F + 110, 2700, 4),
              ("Light_B_Warm_2", S + 40, 30, F + 170, 2700, 2.5)]
    cams = [("Cam_TopView", 150, 150, 900, -90, -90, 24),
            ("Cam_A_Entrance", 40, 15, F + 160, -5, 90, 14),
            ("Cam_B_OverSofa", sofa_x - 8, 150, 215, -35, 0, 12),
            ("Cam_B_Corner", 280, 20, F + 200, -25, 135, 14)]
    start = (40, 30, 90)
    return dict(boxes=boxes, screens=screens, lights=lights, cams=cams, start=start)


def horizontal_split():
    """안 3: A는 위쪽 3m 복도, B는 아래쪽 300 x 200"""
    S = 100
    boxes = [
        ("Floor_A", 0, ROOM, 0, S, F - 5, F, "A_Floor"),
        ("Floor_B", 0, ROOM, S, ROOM, F - 5, F, "B_Floor"),
        wall_y("Wall_Top", 0, 0, ROOM, "A_Wall"),
        wall_x("Wall_Left_A_1", 0, 0, 10, "A_Wall"),              # 입구: 왼쪽 벽 10~90
        wall_x("Wall_Left_A_2", 0, 90, S, "A_Wall"),
        wall_x("Wall_Left_B", 0, S, ROOM, "B_Wall"),
        wall_x("Wall_Right_A", ROOM, 0, S, "A_Wall"),
        wall_x("Wall_Right_Screen", ROOM, S, ROOM, "B_Wall"),     # B 영상: 오른쪽 배정 벽
        wall_y("Wall_Bottom_1", ROOM, 0, 200, "B_Wall"),          # 출구: 아래쪽 벽 200~280
        wall_y("Wall_Bottom_2", ROOM, 280, ROOM, "B_Wall"),
        wall_y("Wall_Bottom_ExitHeader", ROOM, 200, 280, "B_Wall", z0=F + DH),
        wall_y("Partition_1", S, 0, 210, "A_Wall"),               # 가벽 문: 210~290
        wall_y("Partition_2", S, 290, ROOM, "A_Wall"),
        wall_y("Partition_DoorHeader", S, 210, 290, "A_Wall", z0=F + DH),
        ("Door_Partition", 284, 288, S - 5 - DW, S - 5, F, F + DH, "Door"),   # A 쪽으로 열림 (B 화면을 가리지 않게)
        ("Door_Exit", 274, 278, ROOM + T / 2, ROOM + T / 2 + DW, F, F + DH, "Door"),
        ("Rug", 30, 250, 115, 285, F, F + 1, "Rug"),
        ("Projector_A", 90, 120, 10, 40, TOP - 31, TOP - 19, "Device"),
        ("Projector_B", 60, 90, 187, 213, TOP - 25, TOP - 13, "Device"),
        ("Speaker_A", 270, 285, 10, 25, F, F + 30, "Device"),
        ("Speaker_B_1", 10, 25, 280, 295, F, F + 30, "Device"),
        ("Speaker_B_2", 275, 290, 105, 120, F, F + 30, "Device"),
    ] + sofa_facing_right(40, 120)
    screens = [
        ("Screen_B_Home", VIDEO_B, ROOM - T / 2 - 1, 200, F + 125, 160, 160 * 9 / 16, 0),
        ("Screen_A_Society", VIDEO_A, 105, S - T / 2 - 1, F + 125, 180, 180 * 9 / 16, 90),
    ]
    lights = [("Light_A_Cold", 150, 50, TOP - 20, 6500, 2),
              ("Light_B_Warm_1", 25, 285, F + 110, 2700, 4),
              ("Light_B_Warm_2", 200, 115, F + 170, 2700, 2.5)]
    cams = [("Cam_TopView", 150, 150, 900, -90, -90, 24),
            ("Cam_A_Entrance", 15, 50, F + 160, -5, 0, 14),
            ("Cam_B_OverSofa", 25, 200, 215, -30, 0, 12),
            ("Cam_B_Corner", 285, 290, F + 200, -25, -150, 14)]
    start = (20, 50, 90)
    return dict(boxes=boxes, screens=screens, lights=lights, cams=cams, start=start)


def horizontal_split_v2():
    """안 4 (안 3 수정, 2026-11-13 스케치): A는 위쪽 3m 복도, B 영상은 왼쪽 벽, 소파는 오른쪽에서 왼쪽을 봄, 출구는 아래쪽 벽 왼쪽"""
    S = 100
    PD = (190, 270)          # A→B 문 (가벽 오른쪽 끝)
    EX = (10, 90)            # 출구 (아래쪽 벽 왼쪽 끝)
    sofa_x1 = 290            # 소파 등받이 (오른쪽 벽 쪽)
    sofa_x0 = sofa_x1 - 75
    sy0, sy1 = 130, 290
    boxes = [
        ("Floor_A", 0, ROOM, 0, S, F - 5, F, "A_Floor"),
        ("Floor_B", 0, ROOM, S, ROOM, F - 5, F, "B_Floor"),
        wall_y("Wall_Top", 0, 0, ROOM, "A_Wall"),
        wall_x("Wall_Left_A_1", 0, 0, 10, "A_Wall"),              # 입구: 왼쪽 벽 10~90
        wall_x("Wall_Left_A_2", 0, 90, S, "A_Wall"),
        wall_x("Wall_Left_B_Screen", 0, S, ROOM, "B_Wall"),       # B 영상: 왼쪽 벽
        wall_x("Wall_Right_A", ROOM, 0, S, "A_Wall"),
        wall_x("Wall_Right_B", ROOM, S, ROOM, "B_Wall"),
        wall_y("Wall_Bottom_1", ROOM, EX[1], ROOM, "B_Wall"),     # 출구: 아래쪽 벽 10~90
        wall_y("Wall_Bottom_ExitHeader", ROOM, EX[0], EX[1], "B_Wall", z0=F + DH),
        wall_y("Partition_1", S, 0, PD[0], "A_Wall"),
        wall_y("Partition_2", S, PD[1], ROOM, "A_Wall"),
        wall_y("Partition_DoorHeader", S, PD[0], PD[1], "A_Wall", z0=F + DH),
        ("Door_Partition", PD[1] - 6, PD[1] - 2, S - 5 - DW, S - 5, F, F + DH, "Door"),   # A 쪽으로 열림
        ("Door_Exit", EX[1] - 6, EX[1] - 2, ROOM + T / 2, ROOM + T / 2 + DW, F, F + DH, "Door"),
        ("Rug", 40, 270, 115, 285, F, F + 1, "Rug"),
        ("Projector_A", 90, 120, 10, 40, TOP - 31, TOP - 19, "Device"),
        ("Projector_B", sofa_x0 + 10, sofa_x0 + 40, 197, 223, TOP - 25, TOP - 13, "Device"),
        ("Speaker_A", 270, 285, 10, 25, F, F + 30, "Device"),
        ("Speaker_B_1", 10, 25, 105, 120, F, F + 30, "Device"),
        ("Speaker_B_2", 275, 290, 105, 120, F, F + 30, "Device"),
        # 소파: 등받이가 오른쪽, 앉으면 왼쪽(-X) 화면을 봄
        ("Sofa_Seat", sofa_x0, sofa_x1, sy0, sy1, F + 1, F + 45, "Sofa"),
        ("Sofa_Back", sofa_x1 - 18, sofa_x1, sy0, sy1, F + 45, F + 85, "Sofa"),
        ("Sofa_Arm_1", sofa_x0, sofa_x1, sy0, sy0 + 15, F + 45, F + 65, "Sofa"),
        ("Sofa_Arm_2", sofa_x0, sofa_x1, sy1 - 15, sy1, F + 45, F + 65, "Sofa"),
    ]
    screens = [
        ("Screen_B_Home", VIDEO_B, T / 2 + 1, 210, F + 125, 160, 160 * 9 / 16, 180),
        ("Screen_A_Society", VIDEO_A, 95, S - T / 2 - 1, F + 125, 170, 170 * 9 / 16, 90),
    ]
    lights = [("Light_A_Cold", 150, 50, TOP - 20, 6500, 2),
              ("Light_B_Warm_1", 285, 285, F + 110, 2700, 4),
              ("Light_B_Warm_2", 150, 115, F + 170, 2700, 2.5)]
    cams = [("Cam_TopView", 150, 150, 900, -90, -90, 24),
            ("Cam_A_Entrance", 15, 50, F + 160, -5, 0, 14),
            ("Cam_B_OverSofa", 292, 210, 215, -30, 180, 12),
            ("Cam_B_Corner", 20, 285, F + 200, -25, -40, 14)]
    start = (20, 50, 90)
    return dict(boxes=boxes, screens=screens, lights=lights, cams=cams, start=start)


LAYOUTS = {
    "Current": lambda: vertical_split(120, 220),
    "Opt1":    lambda: vertical_split(120, 150),
    "Opt2":    lambda: vertical_split(90, 180),
    "Opt3":    horizontal_split,
    "Opt4":    horizontal_split_v2,
}

# =====================================================================
# 3. 도구
# =====================================================================
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
lib = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
els = unreal.EditorLoadingAndSavingUtils
CUBE = lib.load_asset("/Engine/BasicShapes/Cube.Cube")
PLANE = lib.load_asset("/Engine/BasicShapes/Plane.Plane")   # 100x100, 한쪽 면만 보임


def get_material(name, color):
    path = "{}/Materials/M_{}".format(ROOT, name)
    if lib.does_asset_exist(path):
        return lib.load_asset(path)
    mat = tools.create_asset("M_" + name, ROOT + "/Materials", unreal.Material, unreal.MaterialFactoryNew())
    c = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    c.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
    r = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
    r.set_editor_property("r", 0.8)
    mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    lib.save_asset(path)
    return mat


def get_playlist(key, video):
    """영상 파일 → 미디어 소스 → 플레이리스트 (레벨들이 함께 씀)"""
    d = ROOT + "/Media"
    src_path, pl_path = "{}/MS_{}".format(d, key), "{}/PL_{}".format(d, key)
    src = lib.load_asset(src_path) if lib.does_asset_exist(src_path) else \
        tools.create_asset("MS_" + key, d, unreal.FileMediaSource, unreal.FileMediaSourceFactoryNew())
    src.set_file_path(unreal.Paths.project_content_dir() + video)
    lib.save_asset(src_path)
    pl = lib.load_asset(pl_path) if lib.does_asset_exist(pl_path) else \
        tools.create_asset("PL_" + key, d, unreal.MediaPlaylist, unreal.MediaPlaylistFactoryNew())
    if pl.num() == 0:
        pl.add(src)
        lib.save_asset(pl_path)
    return pl


def label(a, name, folder):
    a.set_actor_label(PREFIX + name)
    a.set_folder_path("Exhibition/" + folder)


def box(spec, mats):
    name, x0, x1, y0, y1, z0, z1, col = spec
    center = unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    a = actors.spawn_actor_from_object(CUBE, center)
    a.set_actor_scale3d(unreal.Vector(abs(x1 - x0) / 100.0, abs(y1 - y0) / 100.0, abs(z1 - z0) / 100.0))
    a.static_mesh_component.set_material(0, mats[col])
    label(a, name, "Structure")


def ceiling(mats):
    """천장: 아래를 향한 한 면짜리 판.
    안에서 올려다보면 천장이 보이고, 위에서 내려다보면 투명해서 방 안이 보임 (부감샷용)"""
    a = actors.spawn_actor_from_object(PLANE, unreal.Vector(ROOM / 2.0, ROOM / 2.0, TOP),
                                       unreal.Rotator(roll=180.0, pitch=0.0, yaw=0.0))
    a.set_actor_scale3d(unreal.Vector(ROOM / 100.0, ROOM / 100.0, 1.0))
    a.static_mesh_component.set_material(0, mats["Ceiling"])
    label(a, "Ceiling", "Structure")


def overhead_view():
    """레벨을 열면 바로 보이는 에디터 화면 시점: 비스듬히 내려다보는 부감샷"""
    eye, target = OVERHEAD_EYE, unreal.Vector(ROOM / 2.0, ROOM / 2.0, 60)
    rot = unreal.MathLibrary.find_look_at_rotation(eye, target)
    unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).set_level_viewport_camera_info(eye, rot)


def screen(spec, playlists):
    """미디어 플레이트: 영상을 띄우는 화면. Play 시 자동 재생 + 반복"""
    name, video, x, y, z, w, h, yaw = spec
    a = actors.spawn_actor_from_class(unreal.MediaPlate, unreal.Vector(x, y, z),
                                      unreal.Rotator(roll=0.0, pitch=0.0, yaw=float(yaw)))
    a.set_actor_scale3d(unreal.Vector(1.0, w / 100.0, h / 100.0))
    c = a.get_editor_property("media_plate_component")
    c.set_editor_property("media_playlist", playlists[video])
    c.set_editor_property("auto_play", True)
    c.set_editor_property("loop", True)
    c.set_editor_property("play_on_open", True)
    c.set_editor_property("enable_audio", True)
    c.set_editor_property("play_only_when_visible", False)   # 안 보이는 위치에서 시작해도 재생
    label(a, name, "Screens")
    return a


def light(spec):
    name, x, y, z, kelvin, lumens = spec
    a = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, z))
    c = a.get_editor_property("light_component")
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_intensity(float(lumens))
    c.set_editor_property("use_temperature", True)
    c.set_editor_property("temperature", float(kelvin))
    c.set_editor_property("attenuation_radius", 350.0)
    label(a, name, "Lights")


def camera(spec):
    name, x, y, z, pitch, yaw, focal = spec
    a = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(x, y, z),
                                      unreal.Rotator(roll=0.0, pitch=float(pitch), yaw=float(yaw)))
    cc = a.get_cine_camera_component()
    cc.set_editor_property("current_focal_length", float(focal))
    cc.set_editor_property("post_process_settings", manual_exposure(cc.get_editor_property("post_process_settings")))
    label(a, name, "Cameras")


def manual_exposure(ps):
    """노출 고정: 방 밝기가 변해도 화면 밝기가 흔들리지 않게"""
    for k, v in [("auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL),
                 ("auto_exposure_apply_physical_camera_exposure", False),
                 ("auto_exposure_bias", EXPOSURE)]:
        ps.set_editor_property("override_" + k, True)
        ps.set_editor_property(k, v)
    return ps


def exposure():
    a = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(150, 150, 120))
    a.set_editor_property("unbound", True)
    a.set_editor_property("settings", manual_exposure(a.get_editor_property("settings")))
    label(a, "PostProcess", "Lights")


def preview_play():
    """에디터 화면에서도 영상이 보이도록 현재 레벨의 화면을 재생"""
    for a in actors.get_all_level_actors():
        if isinstance(a, unreal.MediaPlate):
            c = a.get_editor_property("media_plate_component")
            p = c.get_media_player()
            if p:
                p.set_editor_property("play_on_open", True)
                p.set_looping(True)
                p.open_source(c.get_editor_property("media_playlist").get(0))

# =====================================================================
# 4. 레벨 만들기
# =====================================================================
def build_level(key, mats, playlists):
    spec = LAYOUTS[key]()
    path = "{}/Maps/L_{}".format(ROOT, key)
    if lib.does_asset_exist(path):
        els.load_map(path)
        for a in actors.get_all_level_actors():
            if a.get_actor_label().startswith(PREFIX):
                actors.destroy_actor(a)
    else:
        els.new_blank_map(False)

    box(("Ground", -500, 800, -500, 800, F - 10, F - 5, "Ground"), mats)   # 바깥 바닥
    for b in spec["boxes"]:
        box(b, mats)
    ceiling(mats)
    for s in spec["screens"]:
        screen(s, playlists)
    for l in spec["lights"]:
        light(l)
    for c in spec["cams"]:
        camera(c)
    exposure()
    x, y, z = spec["start"]
    yaw = 0.0 if key in ("Opt3", "Opt4") else 90.0
    ps = actors.spawn_actor_from_class(unreal.PlayerStart, unreal.Vector(x, y, z),
                                       unreal.Rotator(roll=0.0, pitch=0.0, yaw=yaw))
    label(ps, "PlayerStart", "Start")

    overhead_view()
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    els.save_map(world, path)
    unreal.log("[전시] {} 완료".format(path))


def main():
    mats = {k: get_material(k, v) for k, v in COLORS.items()}
    playlists = {VIDEO_A: get_playlist("A_society", VIDEO_A),
                 VIDEO_B: get_playlist("B_home", VIDEO_B)}
    for key in BUILD:
        build_level(key, mats, playlists)
    if OPEN_AFTER:
        els.load_map("{}/Maps/L_{}".format(ROOT, OPEN_AFTER))
        overhead_view()
        preview_play()
    unreal.log("[전시] 전체 완료: " + ", ".join(BUILD))


main()
