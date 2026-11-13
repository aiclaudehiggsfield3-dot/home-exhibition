# -*- coding: utf-8 -*-
"""
전시 공간 자동 생성 스크립트 (Unreal Engine 5, 에디터 전용)

실행: Unreal 메뉴의 Execute Python Script 에서 이 파일 선택
      또는 Output Log 입력칸을 Cmd 로 두고:  py "/파일/경로/build_exhibition.py"

좌표 규칙 (위에서 내려다본 배치도 기준, 단위 cm)
  X = 가로 (왼쪽 0 → 오른쪽 300)
  Y = 세로 (입구가 있는 위쪽 벽 0 → 아래쪽 벽 300)
  Z = 높이 (바닥 0 → 위)

  A 공간(사회): X 0 ~ 120
  B 공간(집)  : X 120 ~ 300
  가벽        : X = 120 위치, 아래쪽 끝에 A→B 문
  출구        : 위쪽 벽(Y=0), B 공간 오른쪽 끝
  B 영상 벽   : 오른쪽 벽(X=300) 안쪽 면

다시 실행하면 이전에 만든 EX_ 로 시작하는 물체를 지우고 새로 짓습니다.
"""

import unreal

# =====================================================================
# 1. 설정값  ← 레이아웃을 바꾸고 싶으면 여기 숫자만 고치면 됩니다
# =====================================================================
ROOM = 300            # 전체 한 변 (cm)
SPLIT_X = 120         # A/B 나누는 가벽 위치 (A 폭)
WALL_H = 240          # 벽 높이
WALL_T = 10           # 벽 두께
DOOR_W = 80           # 문 폭
DOOR_H = 210          # 문 높이 (그 위는 벽으로 막음)
FLOOR_TOP = 2         # 바닥 윗면 높이 (기본 레벨 바닥과 겹쳐 깜빡이는 것 방지)

ENTRANCE_X = (0, 80)                        # 입구: 위쪽 벽 왼쪽 끝 (문 없이 열림)
PARTITION_DOOR_Y = (210, 210 + DOOR_W)      # 가벽 문: 가벽 아래쪽
EXIT_X = (ROOM - 20 - DOOR_W, ROOM - 20)    # 출구: 위쪽 벽, 오른쪽 모서리에서 20cm 안쪽

DOORS_OPEN = True        # True: 문을 열어 둔 상태로 배치 (걸어서 통과 확인용)
INCLUDE_CEILING = True   # 천장 (위에서 내려다보는 사진은 Outliner에서 EX_Ceiling 눈 아이콘 끄기)

PREFIX = "EX_"
FOLDER = "Exhibition"
MAT_DIR = "/Game/Exhibition/Materials"

# 색 (R, G, B) 0~1
COLORS = {
    "A_Wall":   (0.32, 0.37, 0.42),   # 차가운 회청색
    "A_Floor":  (0.18, 0.19, 0.21),   # 어두운 콘크리트
    "B_Wall":   (0.85, 0.74, 0.60),   # 따뜻한 베이지
    "B_Floor":  (0.45, 0.30, 0.18),   # 나무색
    "Outer":    (0.80, 0.80, 0.78),   # 외벽 바깥 기본색
    "Door":     (0.55, 0.35, 0.22),
    "Sofa":     (0.65, 0.28, 0.14),
    "Rug":      (0.90, 0.82, 0.68),
    "Device":   (0.08, 0.08, 0.08),   # 프로젝터 등 장비
}
SCREEN_GLOW = 2.0   # 영상 면 밝기 (빛나는 흰 면으로 표시)
EXPOSURE_BIAS = -5.0  # 화면 밝기(노출). 숫자가 작을수록 어두움. 위에서 본 사진은 -7 정도가 적당

# =====================================================================
# 2. 기본 도구
# =====================================================================
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
asset_lib = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
CUBE = asset_lib.load_asset("/Engine/BasicShapes/Cube.Cube")   # 한 변 100cm, 중심 기준


def clear_previous():
    """이전 실행에서 만든 EX_ 물체 삭제"""
    removed = 0
    for a in actors.get_all_level_actors():
        if a.get_actor_label().startswith(PREFIX):
            actors.destroy_actor(a)
            removed += 1
    unreal.log("[전시] 이전 물체 {}개 삭제".format(removed))


def get_material(name, color, emissive=0.0):
    """단색 재질을 만들거나, 이미 있으면 불러오기"""
    path = "{}/M_{}".format(MAT_DIR, name)
    if asset_lib.does_asset_exist(path):
        return asset_lib.load_asset(path)

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    mat = tools.create_asset("M_" + name, MAT_DIR, unreal.Material, unreal.MaterialFactoryNew())

    col = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 0)
    col.set_editor_property("constant", unreal.LinearColor(color[0], color[1], color[2], 1.0))
    mel.connect_material_property(col, "", unreal.MaterialProperty.MP_BASE_COLOR)

    rough = mel.create_material_expression(mat, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", 0.8)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

    if emissive > 0:
        glow = mel.create_material_expression(mat, unreal.MaterialExpressionConstant3Vector, -400, 400)
        glow.set_editor_property("constant", unreal.LinearColor(emissive, emissive, emissive, 1.0))
        mel.connect_material_property(glow, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)

    mel.recompile_material(mat)
    asset_lib.save_asset(path)
    return mat


def box(name, x0, x1, y0, y1, z0, z1, mat=None, sub="Structure"):
    """두 모서리 좌표(시작~끝)로 상자 만들기. 좌표는 위 규칙 기준"""
    sx, sy, sz = abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)
    center = unreal.Vector((x0 + x1) / 2.0, (y0 + y1) / 2.0, (z0 + z1) / 2.0)
    a = actors.spawn_actor_from_object(CUBE, center)
    a.set_actor_scale3d(unreal.Vector(sx / 100.0, sy / 100.0, sz / 100.0))
    a.set_actor_label(PREFIX + name)
    a.set_folder_path(FOLDER + "/" + sub)
    if mat:
        a.static_mesh_component.set_material(0, mat)
    return a


def wall_x(name, x, y0, y1, mat, z0=None, z1=None):
    """세로 방향(Y축을 따라) 벽: X 위치에 두께 WALL_T"""
    z0 = FLOOR_TOP if z0 is None else z0
    z1 = FLOOR_TOP + WALL_H if z1 is None else z1
    return box(name, x - WALL_T / 2.0, x + WALL_T / 2.0, y0, y1, z0, z1, mat, "Walls")


def wall_y(name, y, x0, x1, mat, z0=None, z1=None):
    """가로 방향(X축을 따라) 벽: Y 위치에 두께 WALL_T"""
    z0 = FLOOR_TOP if z0 is None else z0
    z1 = FLOOR_TOP + WALL_H if z1 is None else z1
    return box(name, x0, x1, y - WALL_T / 2.0, y + WALL_T / 2.0, z0, z1, mat, "Walls")


def light(name, x, y, z, kelvin, lumens, radius=350):
    a = actors.spawn_actor_from_class(unreal.PointLight, unreal.Vector(x, y, z))
    a.set_actor_label(PREFIX + name)
    a.set_folder_path(FOLDER + "/Lights")
    c = a.get_editor_property("light_component")
    # 무버블: '라이팅 빌드 필요' 경고 없이 바로 실시간 조명으로 보이게
    c.set_mobility(unreal.ComponentMobility.MOVABLE)
    c.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
    c.set_editor_property("intensity", lumens)
    c.set_editor_property("use_temperature", True)
    c.set_editor_property("temperature", float(kelvin))
    c.set_editor_property("attenuation_radius", float(radius))
    return a


def camera(name, x, y, z, pitch, yaw, focal=16.0):
    rot = unreal.Rotator(roll=0.0, pitch=float(pitch), yaw=float(yaw))
    a = actors.spawn_actor_from_class(unreal.CineCameraActor, unreal.Vector(x, y, z), rot)
    a.set_actor_label(PREFIX + name)
    a.set_folder_path(FOLDER + "/Cameras")
    a.get_cine_camera_component().set_editor_property("current_focal_length", float(focal))
    return a


# =====================================================================
# 3. 짓기
# =====================================================================
def build():
    clear_previous()

    m = {k: get_material(k, v) for k, v in COLORS.items()}
    m["Screen"] = get_material("Screen", (1.0, 1.0, 1.0), emissive=SCREEN_GLOW)

    top = FLOOR_TOP + WALL_H
    door_top = FLOOR_TOP + DOOR_H

    # ---------- 바닥 / 천장 ----------
    box("Floor_A", 0, SPLIT_X, 0, ROOM, FLOOR_TOP - 5, FLOOR_TOP, m["A_Floor"], "Structure")
    box("Floor_B", SPLIT_X, ROOM, 0, ROOM, FLOOR_TOP - 5, FLOOR_TOP, m["B_Floor"], "Structure")
    if INCLUDE_CEILING:
        box("Ceiling", 0, ROOM, 0, ROOM, top, top + 5, m["Outer"], "Structure")

    # ---------- 외벽 ----------
    wall_x("Wall_Left_A", 0, 0, ROOM, m["A_Wall"])                      # A 왼쪽 벽
    wall_x("Wall_Right_B_Screen", ROOM, 0, ROOM, m["B_Wall"])           # B 영상 벽 (배정 벽)
    wall_y("Wall_Bottom_A", ROOM, 0, SPLIT_X, m["A_Wall"])              # 아래쪽 벽
    wall_y("Wall_Bottom_B", ROOM, SPLIT_X, ROOM, m["B_Wall"])

    # 위쪽 벽: [입구 빈칸] A벽 | B벽 [출구] B벽
    wall_y("Wall_Top_A", 0, ENTRANCE_X[1], SPLIT_X, m["A_Wall"])
    wall_y("Wall_Top_B_1", 0, SPLIT_X, EXIT_X[0], m["B_Wall"])
    wall_y("Wall_Top_B_2", 0, EXIT_X[1], ROOM, m["B_Wall"])
    wall_y("Wall_Top_ExitHeader", 0, EXIT_X[0], EXIT_X[1], m["B_Wall"], z0=door_top)

    # ---------- 가벽 (A/B 사이) ----------
    wall_x("Partition_1", SPLIT_X, 0, PARTITION_DOOR_Y[0], m["A_Wall"])
    wall_x("Partition_2", SPLIT_X, PARTITION_DOOR_Y[1], ROOM, m["A_Wall"])
    wall_x("Partition_DoorHeader", SPLIT_X, PARTITION_DOOR_Y[0], PARTITION_DOOR_Y[1],
           m["A_Wall"], z0=door_top)

    # ---------- 문 ----------
    t = 4  # 문짝 두께
    if DOORS_OPEN:
        # 가벽 문: 아래쪽 끝이 경첩, B 공간 쪽으로 90도 열림
        hy = PARTITION_DOOR_Y[1]
        box("Door_Partition", SPLIT_X + WALL_T / 2.0, SPLIT_X + WALL_T / 2.0 + DOOR_W,
            hy - t - 2, hy - 2, FLOOR_TOP, door_top, m["Door"], "Doors")
        # 출구 문: 오른쪽 끝이 경첩, 바깥쪽으로 90도 열림
        hx = EXIT_X[1]
        box("Door_Exit", hx - t - 2, hx - 2, -WALL_T / 2.0 - DOOR_W, -WALL_T / 2.0,
            FLOOR_TOP, door_top, m["Door"], "Doors")
    else:
        box("Door_Partition", SPLIT_X - t / 2.0, SPLIT_X + t / 2.0,
            PARTITION_DOOR_Y[0], PARTITION_DOOR_Y[1], FLOOR_TOP, door_top, m["Door"], "Doors")
        box("Door_Exit", EXIT_X[0], EXIT_X[1], -t / 2.0, t / 2.0,
            FLOOR_TOP, door_top, m["Door"], "Doors")

    # ---------- 영상 투사면 (빛나는 흰 면) ----------
    a_face = SPLIT_X - WALL_T / 2.0 - 0.5      # 가벽의 A쪽 면
    box("Screen_A_Society", a_face - 1, a_face, 10, PARTITION_DOOR_Y[0] - 10,
        FLOOR_TOP + 40, FLOOR_TOP + 200, m["Screen"], "Screens")
    b_face = ROOM - WALL_T / 2.0 - 0.5         # 오른쪽 벽 안쪽 면
    box("Screen_B_Home", b_face - 1, b_face, 40, 260,
        FLOOR_TOP + 50, FLOOR_TOP + 200, m["Screen"], "Screens")

    # ---------- B 공간 가구 (영상 벽을 바라봄) ----------
    box("Rug", 135, 280, 30, 270, FLOOR_TOP, FLOOR_TOP + 1, m["Rug"], "Furniture")
    sofa_x0, sofa_x1 = 135, 210          # 깊이 75cm (뒤쪽 135 → 앞쪽 210)
    sofa_y0, sofa_y1 = 70, 230           # 길이 160cm
    box("Sofa_Seat", sofa_x0, sofa_x1, sofa_y0, sofa_y1, FLOOR_TOP + 1, FLOOR_TOP + 45,
        m["Sofa"], "Furniture")
    box("Sofa_Back", sofa_x0, sofa_x0 + 18, sofa_y0, sofa_y1, FLOOR_TOP + 45, FLOOR_TOP + 85,
        m["Sofa"], "Furniture")
    box("Sofa_Arm_1", sofa_x0, sofa_x1, sofa_y0, sofa_y0 + 15, FLOOR_TOP + 45, FLOOR_TOP + 65,
        m["Sofa"], "Furniture")
    box("Sofa_Arm_2", sofa_x0, sofa_x1, sofa_y1 - 15, sofa_y1, FLOOR_TOP + 45, FLOOR_TOP + 65,
        m["Sofa"], "Furniture")

    # ---------- 장비 자리 표시 ----------
    box("Projector_A", 10, 40, 92, 118, top - 31, top - 19, m["Device"], "Devices")
    box("Projector_B", 150, 180, 137, 163, top - 25, top - 13, m["Device"], "Devices")
    box("Speaker_A", 15, 30, 270, 285, FLOOR_TOP, FLOOR_TOP + 30, m["Device"], "Devices")
    box("Speaker_B_1", 275, 290, 15, 30, FLOOR_TOP, FLOOR_TOP + 30, m["Device"], "Devices")
    box("Speaker_B_2", 275, 290, 270, 285, FLOOR_TOP, FLOOR_TOP + 30, m["Device"], "Devices")

    # ---------- 조명 ----------
    light("Light_A_Cold", 60, 150, top - 20, kelvin=6500, lumens=250)
    light("Light_B_Warm_1", 250, 280, FLOOR_TOP + 110, kelvin=2700, lumens=500)
    light("Light_B_Warm_2", 160, 30, FLOOR_TOP + 170, kelvin=2700, lumens=350)

    # ---------- 예시 사진용 카메라 ----------
    camera("Cam_TopView", ROOM / 2.0, ROOM / 2.0, 900, pitch=-90, yaw=-90, focal=24)
    camera("Cam_A_Entrance", 40, 15, FLOOR_TOP + 160, pitch=-5, yaw=90, focal=14)
    camera("Cam_B_OverSofa", 127, 150, 215, pitch=-40, yaw=0, focal=12)
    camera("Cam_B_Corner", ROOM - 20, 20, FLOOR_TOP + 200, pitch=-25, yaw=135, focal=14)

    # ---------- 노출 고정 (실내가 하얗게 날아가지 않도록) ----------
    pp = actors.spawn_actor_from_class(unreal.PostProcessVolume, unreal.Vector(150, 150, 120))
    pp.set_actor_label(PREFIX + "PostProcess")
    pp.set_folder_path(FOLDER + "/Lights")
    pp.set_editor_property("unbound", True)
    ps = pp.get_editor_property("settings")
    ps.set_editor_property("override_auto_exposure_bias", True)
    ps.set_editor_property("auto_exposure_bias", EXPOSURE_BIAS)
    ps.set_editor_property("override_auto_exposure_min_brightness", True)
    ps.set_editor_property("auto_exposure_min_brightness", 4.5)
    ps.set_editor_property("override_auto_exposure_max_brightness", True)
    ps.set_editor_property("auto_exposure_max_brightness", 4.5)
    pp.set_editor_property("settings", ps)

    # ---------- 관객 시작 위치 (입구 안쪽, A 공간을 바라봄) ----------
    starts = [a for a in actors.get_all_level_actors() if isinstance(a, unreal.PlayerStart)]
    start_loc = unreal.Vector(40, 30, FLOOR_TOP + 100)
    start_rot = unreal.Rotator(roll=0.0, pitch=0.0, yaw=90.0)
    if starts:
        starts[0].set_actor_location_and_rotation(start_loc, start_rot, False, False)
    else:
        ps = actors.spawn_actor_from_class(unreal.PlayerStart, start_loc, start_rot)
        ps.set_actor_label(PREFIX + "PlayerStart")

    unreal.log("[전시] 완료: 3m x 3m 전시 공간 생성")


build()


# 예시 사진 뽑기 (Output Log를 Python 모드로 두고 한 줄씩 실행, 결과는 프로젝트/Saved/Screenshots 폴더)
# L = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
# unreal.AutomationLibrary.take_high_res_screenshot(1920, 1080, "EX_A_Entrance.png", camera=L["EX_Cam_A_Entrance"], delay=2.0)
