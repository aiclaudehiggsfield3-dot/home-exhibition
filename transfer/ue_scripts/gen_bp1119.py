# -*- coding: utf-8 -*-
# bp_v4.t3d(현재 레벨 블루프린트)에 11/19 기능을 더해 bp_v5.t3d를 만든다.
#  1) 퇴장 → 플레이 종료 대신 리셋  2) touch 이름별(담요=모닥불, 리모컨=채널+지지직)
#  3) /home/train → 지하철 소리, 문(door)에서 페이드아웃  4) /home/result → QR_Screen에 QR 이미지
# 사용: python3 gen_bp1119.py <Saved 폴더> [EX_Snd_TV 내부 이름]  → bp_v6.t3d
#  6) /home/level 소리 세 갈래 · 지하철 2초 페이드 · 빠른 반응(11/19 22:40)
#  7) 앉으면 조명 · TV는 /home/touch tv로 켬 (11/19 23:00)
#  8) 리모컨 채널 차례로 · 앉으면 눈높이 115cm (11/19 23:20)
#  9) 관리자 소리 계기판 /home/meter (11/19 23:50)
# 10) 채널이 영상 끝나면 저절로 넘어가던 문제 → TV 판에 1개짜리 PL_NOW, 채널은 Replace 후 판 Open (11/20)  → bp_v10.t3d
import re, sys, uuid

SV = sys.argv[1] if len(sys.argv) > 1 else '.'
SRC, DST = SV + '/bp_v4.t3d', SV + '/bp_v10.t3d'
TVSND = sys.argv[2] if len(sys.argv) > 2 else 'AmbientSound_2'   # EX_Snd_TV의 내부 이름 (언리얼에서 확인)
LVL = "/Game/Exhibition/Maps/L_Current.L_Current:PersistentLevel."
STD = ("PinType.PinSubCategoryMemberReference=(),PinType.PinValueType=(),PinType.ContainerType=None,PinType.bIsReference=False,"
       "PinType.bIsConst=False,PinType.bIsWeakPointer=False,PinType.bIsUObjectWrapper=False,PinType.bSerializeAsSinglePrecisionFloat=False,")
END = ("PersistentGuid=00000000000000000000000000000000,bHidden=False,bNotConnectable=False,bDefaultValueIsReadOnly=False,"
       "bDefaultValueIsIgnored=False,bAdvancedView=False,bOrphanedPin=False,")

def gid():
    return uuid.uuid4().hex.upper()

def cls(path):            # '/Script/Engine.AudioComponent' -> 핀 타입 문자열
    return "\"/Script/CoreUObject.Class'%s'\"" % path

# ------------------------------------------------------------------ 읽기
text = open(SRC, encoding='utf-8').read()
blocks = re.findall(r'(Begin Object Class=(\S+) Name="([^"]+)"\n(.*?)\nEnd Object)', text, re.S)
nodes, order = {}, []
for full, klass, name, body in blocks:
    head, pins = [], []
    for line in body.split('\n'):
        if line.strip().startswith('CustomProperties Pin ('):
            pid = re.search(r'PinId=([0-9A-F]+)', line).group(1)
            pn = re.search(r'PinName="([^"]+)"', line).group(1)
            lk = re.search(r'LinkedTo=\(([^)]*)\),', line)
            links = [tuple(x.split()) for x in lk.group(1).split(',') if x.strip()] if lk else []
            raw = re.sub(r'LinkedTo=\([^)]*\),', '', line)
            pins.append({'name': pn, 'id': pid, 'links': links, 'raw': raw})
        else:
            head.append(line)
    nodes[name] = {'klass': klass, 'head': head, 'pins': pins}
    order.append(name)

def pin(node, pname):
    for p in nodes[node]['pins']:
        if p['name'] == pname:
            return p
    raise KeyError(node + '.' + pname)

def link(a, ap, b, bp):
    pa, pb = pin(a, ap), pin(b, bp)
    if (b, pb['id']) not in pa['links']:
        pa['links'].append((b, pb['id']))
    if (a, pa['id']) not in pb['links']:
        pb['links'].append((a, pa['id']))

def unlink(a, ap, b, bp):
    pa, pb = pin(a, ap), pin(b, bp)
    pa['links'] = [l for l in pa['links'] if l != (b, pb['id'])]
    pb['links'] = [l for l in pb['links'] if l != (a, pa['id'])]

def remove(name):
    for p in nodes[name]['pins']:
        for (n, pid) in p['links']:
            if n in nodes:
                for q in nodes[n]['pins']:
                    q['links'] = [l for l in q['links'] if l[0] != name]
    del nodes[name]
    order.remove(name)

# ------------------------------------------------------------------새 노드 만들기
def P(name, cat='exec', sub='', obj=None, out=False, default=None, defobj=None, ref=False):
    s = 'CustomProperties Pin (PinId=%s,PinName="%s",' % (gid(), name)
    if out:
        s += 'Direction="EGPD_Output",'
    s += 'PinType.PinCategory="%s",PinType.PinSubCategory="%s",PinType.PinSubCategoryObject=%s,' % (cat, sub, obj or 'None')
    s += STD.replace('bIsReference=False,PinType.bIsConst=False', 'bIsReference=True,PinType.bIsConst=True') if ref else STD
    if default is not None:
        s += 'DefaultValue="%s",' % default
    if defobj is not None:
        s += 'DefaultObject="%s",' % defobj
    s += END + ')'
    return {'name': name, 'id': re.search(r'PinId=(\w+)', s).group(1), 'links': [], 'raw': '   ' + s}

def add(name, klass, head, pins, x, y, comment=None):
    h = list(head) + ['   NodePosX=%d' % x, '   NodePosY=%d' % y]
    if comment:
        h += ['   NodeComment="%s"' % comment, '   bCommentBubbleVisible=True']
    h.append('   NodeGuid=' + gid())
    nodes[name] = {'klass': '/Script/BlueprintGraph.' + klass, 'head': h, 'pins': pins}
    order.append(name)

EXEC = lambda: [P('execute'), P('then', out=True)]
C_AC, C_AMB = cls('/Script/Engine.AudioComponent'), cls('/Script/Engine.AmbientSound')
C_SMA, C_SMC = cls('/Script/Engine.StaticMeshActor'), cls('/Script/Engine.StaticMeshComponent')
C_PRIM, C_MID = cls('/Script/Engine.PrimitiveComponent'), cls('/Script/Engine.MaterialInstanceDynamic')
C_MPC, C_MP = cls('/Script/MediaPlate.MediaPlateComponent'), cls('/Script/MediaAssets.MediaPlayer')
C_MPLATE, C_ACTOR = cls('/Script/MediaPlate.MediaPlate'), cls('/Script/Engine.Actor')
OSCMSG = "\"/Script/CoreUObject.ScriptStruct'/Script/OSC.OSCMessage'\""

def fn(name, parent, member, pins, x, y, comment=None):
    add(name, 'K2Node_CallFunction',
        ['   FunctionReference=(MemberParent="/Script/CoreUObject.Class\'%s\'",MemberName="%s")' % (parent, member)],
        pins, x, y, comment)

def literal(name, objclass, objname, x, y):
    add(name, 'K2Node_Literal', ['   ObjectRef="%s\'%s%s\'"' % (objclass, LVL, objname)],
        [P('ReturnValue', 'object', obj=cls(objclass), out=True)], x, y)

def comp_get(name, owner_cls, owner_obj, member, comp_obj, x, y):
    add(name, 'K2Node_VariableGet',
        ['   VariableReference=(MemberParent="/Script/CoreUObject.Class\'%s\'",MemberName="%s")' % (owner_cls, member)],
        [P(member, 'object', obj=comp_obj, out=True), P('self', 'object', obj=owner_obj)], x, y)

def self_get(name, var, cat, obj, x, y):
    add(name, 'K2Node_VariableGet', ['   VariableReference=(MemberName="%s",bSelfContext=True)' % var],
        [P(var, cat, obj=obj, out=True)], x, y)

def self_set(name, var, cat, sub, value, x, y):
    add(name, 'K2Node_VariableSet', ['   VariableReference=(MemberName="%s",bSelfContext=True)' % var],
        EXEC() + [P(var, cat, sub, default=value), P('Output_Get', cat, sub, out=True)], x, y)

def get_string(name, index, x, y, comment):
    fn(name, '/Script/OSC.OSCManager', 'GetString',
       EXEC() + [P('Message', 'struct', obj=OSCMSG, ref=True), P('Index', 'int', default=str(index)),
                 P('Value', 'string', out=True), P('ReturnValue', 'bool', out=True)], x, y, comment)

def switch_string(name, cases, x, y, comment):
    head = ['   PinNames(%d)="%s"' % (i, c) for i, c in enumerate(cases)]
    pins = [P('execute'), P('Selection', 'string'), P('Default', out=True)] + [P(c, out=True) for c in cases]
    add(name, 'K2Node_SwitchString', head, pins, x, y, comment)

def fade_in(name, x, y, dur, level, comment):
    fn(name, '/Script/Engine.AudioComponent', 'FadeIn',
       EXEC() + [P('self', 'object', obj=C_AC), P('FadeInDuration', 'real', 'double', default=dur),
                 P('FadeVolumeLevel', 'real', 'double', default=level)], x, y, comment)

def ac_call(name, member, x, y, comment=None):
    fn(name, '/Script/Engine.AudioComponent', member, EXEC() + [P('self', 'object', obj=C_AC)], x, y, comment)

# ------------------------------------------------------------------ 레벨 액터 리터럴
literal('LIT_FIRE', '/Script/Engine.AmbientSound', 'AmbientSound_0', 900, -140)
literal('LIT_SUB', '/Script/Engine.AmbientSound', 'AmbientSound_1', 900, -80)
literal('LIT_QR', '/Script/Engine.StaticMeshActor', 'StaticMeshActor_116', 900, -20)

# ================================================================== 2) touch 이름별
X0, Y0 = 2300, 2600     # 새 노드는 아래쪽에 모아 둔다 (기존 그래프와 겹치지 않게)
unlink('SET_TV2', 'then', 'F_PRINT', 'execute')
get_string('T_GS', 0, X0, Y0, 'touch: 물건 이름')
link('SET_TV2', 'then', 'T_GS', 'execute')
link('ONOSC', 'Message', 'T_GS', 'Message')
switch_string('T_SW', ['blanket', 'remote'], X0 + 300, Y0, '담요 / 리모컨')
link('T_GS', 'then', 'T_SW', 'execute'); link('T_GS', 'Value', 'T_SW', 'Selection')
# 담요 → 모닥불 (이미 나고 있으면 그대로)
comp_get('T_FIREAC', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0 + 300, Y0 + 260)
link('LIT_FIRE', 'ReturnValue', 'T_FIREAC', 'self')
fn('T_ISPLAY', '/Script/Engine.AudioComponent', 'IsPlaying', [P('self', 'object', obj=C_AC), P('ReturnValue', 'bool', out=True)], X0 + 550, Y0 + 260)
link('T_FIREAC', 'AudioComponent', 'T_ISPLAY', 'self')
add('T_BR', 'K2Node_IfThenElse', [], [P('execute'), P('Condition', 'bool', default='true'), P('then', out=True), P('else', out=True)], X0 + 650, Y0 - 40)
link('T_SW', 'blanket', 'T_BR', 'execute'); link('T_ISPLAY', 'ReturnValue', 'T_BR', 'Condition')
fade_in('T_FIREIN', X0 + 900, Y0 - 40, '1.0', '1.0', '담요 → 모닥불 소리')
link('T_BR', 'else', 'T_FIREIN', 'execute'); link('T_FIREAC', 'AudioComponent', 'T_FIREIN', 'self')
# 리모컨 → 다음 채널 + 지지직
comp_get('TVC3', '/Script/MediaPlate.MediaPlate', C_MPLATE, 'MediaPlateComponent', C_MPC, X0 + 650, Y0 + 380)
link('LIT_TV', 'ReturnValue', 'TVC3', 'self')
fn('T_GETMP', '/Script/MediaPlate.MediaPlateComponent', 'GetMediaPlayer',
   EXEC() + [P('self', 'object', obj=C_MPC), P('ReturnValue', 'object', obj=C_MP, out=True)], X0 + 900, Y0 + 250)
link('T_SW', 'remote', 'T_GETMP', 'execute'); link('TVC3', 'MediaPlateComponent', 'T_GETMP', 'self')
# MediaPlate의 Open()은 늘 0번부터, 플레이어 Next()는 같은 영상만 다시 틀어서 →
# 플레이어가 PL_TV의 다른 번호를 직접 열게 한다 (지금 A_society면 0번, 아니면 1번). PlayOnOpen을 켜야 바로 재생됨.
add('T_PON', 'K2Node_VariableSet',
    ['   VariableReference=(MemberParent="/Script/CoreUObject.Class\'/Script/MediaAssets.MediaPlayer\'",MemberName="PlayOnOpen")'],
    EXEC() + [P('PlayOnOpen', 'bool', default='true'), P('Output_Get', 'bool', out=True), P('self', 'object', obj=C_MP)],
    X0 + 1200, Y0 + 250)
link('T_GETMP', 'then', 'T_PON', 'execute'); link('T_GETMP', 'ReturnValue', 'T_PON', 'self')
fn('T_URL', '/Script/MediaAssets.MediaPlayer', 'GetUrl',
   [P('self', 'object', obj=C_MP), P('ReturnValue', 'string', out=True)], X0 + 1200, Y0 + 450)
link('T_GETMP', 'ReturnValue', 'T_URL', 'self')
fn('T_HAS', '/Script/Engine.KismetStringLibrary', 'Contains',
   [P('SearchIn', 'string'), P('Substring', 'string', default='A_society'), P('ReturnValue', 'bool', out=True)], X0 + 1450, Y0 + 450)
link('T_URL', 'ReturnValue', 'T_HAS', 'SearchIn')
fn('T_SELI', '/Script/Engine.KismetMathLibrary', 'SelectInt',
   [P('A', 'int', default='0'), P('B', 'int', default='1'), P('bPickA', 'bool'), P('ReturnValue', 'int', out=True)], X0 + 1700, Y0 + 450)
link('T_HAS', 'ReturnValue', 'T_SELI', 'bPickA')
fn('T_OPEN', '/Script/MediaAssets.MediaPlayer', 'OpenPlaylistIndex',
   EXEC() + [P('self', 'object', obj=C_MP),
             P('InPlaylist', 'object', obj=cls('/Script/MediaAssets.MediaPlaylist'), defobj='/Game/Exhibition/Media/PL_TV.PL_TV'),
             P('Index', 'int'), P('ReturnValue', 'bool', out=True)], X0 + 1500, Y0 + 250, '리모컨 → 다른 채널')
link('T_PON', 'then', 'T_OPEN', 'execute'); link('T_GETMP', 'ReturnValue', 'T_OPEN', 'self')
link('T_SELI', 'ReturnValue', 'T_OPEN', 'Index')
fn('T_STATIC', '/Script/Engine.GameplayStatics', 'PlaySound2D',
   EXEC() + [P('Sound', 'object', obj=cls('/Script/Engine.SoundBase'), defobj='/Game/Exhibition/Audio/S_TempStatic.S_TempStatic'),
             P('VolumeMultiplier', 'real', 'double', default='0.5')], X0 + 1800, Y0 + 250, '채널 바뀌는 지지직')
link('T_OPEN', 'then', 'T_STATIC', 'execute')

# ================================================================== 3) 지하철 소리
sw = nodes['SW']
sw['head'].insert(7, '   PinNames(7)="/home/train"')
sw['pins'].append(P('/home/train', out=True))
Y1 = Y0 + 700
comp_get('SUBAC1', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0, Y1 + 150)
link('LIT_SUB', 'ReturnValue', 'SUBAC1', 'self')
fade_in('N_SUBIN', X0 + 300, Y1, '1.0', '1.0', 'train: 지하철 소리 켬')
link('SW', '/home/train', 'N_SUBIN', 'execute'); link('SUBAC1', 'AudioComponent', 'N_SUBIN', 'self')
link('N_SUBIN', 'then', 'F_PRINT', 'execute')
# 문 열고 집에 들어오면 지하철 소리 끊김
unlink('F_TVOPEN', 'then', 'F_PRINT', 'execute')
fn('D_SUBOUT', '/Script/Engine.AudioComponent', 'FadeOut',
   EXEC() + [P('self', 'object', obj=C_AC), P('FadeOutDuration', 'real', 'double', default='2.0'),
             P('FadeVolumeLevel', 'real', 'double', default='0.0')], X0 + 600, Y1, 'door: 지하철 소리 2초에 걸쳐 잦아듦')
link('F_TVOPEN', 'then', 'D_SUBOUT', 'execute'); link('SUBAC1', 'AudioComponent', 'D_SUBOUT', 'self')
link('D_SUBOUT', 'then', 'F_PRINT', 'execute')

# ================================================================== 5) 바라보는 방향(/home/look) + 시야 부채꼴 (11/19 21:55)
# 각도는 보이지 않는 기준점 EX_LookRef(TargetPoint_0)의 회전에 저장 → Tick에서 형체가 그 방향으로 부드럽게 돈다 (새 변수 없이)
literal('LIT_LOOK', '/Script/Engine.TargetPoint', 'TargetPoint_0', 900, 40)
literal('LIT_FAN', '/Script/Engine.StaticMeshActor', 'StaticMeshActor_0', 900, 100)
ROT = "\"/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Rotator'\""
sw['head'].insert(8, '   PinNames(8)="/home/look"')
sw['pins'].append(P('/home/look', out=True))
Y4 = Y1 + 2400
fn('L_GF', '/Script/OSC.OSCManager', 'GetFloat',
   EXEC() + [P('Message', 'struct', obj=OSCMSG, ref=True), P('Index', 'int', default='0'),
             P('Value', 'real', 'double', out=True), P('ReturnValue', 'bool', out=True)], X0 + 300, Y4, 'look: 바라보는 방향(도)')
link('SW', '/home/look', 'L_GF', 'execute'); link('ONOSC', 'Message', 'L_GF', 'Message')
fn('L_ROT', '/Script/Engine.KismetMathLibrary', 'MakeRotator',
   [P('Roll', 'real', 'double', default='0.0'), P('Pitch', 'real', 'double', default='0.0'), P('Yaw', 'real', 'double'),
    P('ReturnValue', 'struct', obj=ROT, out=True)], X0 + 600, Y4 + 200)
link('L_GF', 'Value', 'L_ROT', 'Yaw')
fn('L_SET', '/Script/Engine.Actor', 'K2_SetActorRotation',
   EXEC() + [P('self', 'object', obj=C_ACTOR), P('NewRotation', 'struct', obj=ROT), P('bTeleportPhysics', 'bool', default='false'),
             P('ReturnValue', 'bool', out=True)], X0 + 900, Y4, '기준점에 방향 저장')
link('L_GF', 'then', 'L_SET', 'execute'); link('LIT_LOOK', 'ReturnValue', 'L_SET', 'self'); link('L_ROT', 'ReturnValue', 'L_SET', 'NewRotation')
# Tick: 형체가 도는 목표 = (예전) 움직이는 쪽 → (지금) 기준점 방향
unlink('F_SELROT', 'ReturnValue', 'F_RINTERP', 'Target')
fn('L_GETROT', '/Script/Engine.Actor', 'K2_GetActorRotation',
   [P('self', 'object', obj=C_ACTOR), P('ReturnValue', 'struct', obj=ROT, out=True)], 1250, 2350)
link('LIT_LOOK', 'ReturnValue', 'L_GETROT', 'self'); link('L_GETROT', 'ReturnValue', 'F_RINTERP', 'Target')
# 부채꼴은 형체와 같이 숨기고 보이기
for n in ('F_HIDEVIS', 'F_SHOWVIS'):
    link('LIT_FAN', 'ReturnValue', n, 'self')          # 퇴장 리셋(X_HIDEV)은 아래에서

# ================================================================== 4) QR
Y2 = Y1 + 400
comp_get('QRC1', '/Script/Engine.StaticMeshActor', C_SMA, 'StaticMeshComponent', C_SMC, X0, Y2 + 200)
link('LIT_QR', 'ReturnValue', 'QRC1', 'self')
unlink('SW', '/home/result', 'F_PRINT', 'execute')
get_string('Q_GS', 1, X0 + 300, Y2, 'result: QR 파일 경로')
link('SW', '/home/result', 'Q_GS', 'execute'); link('ONOSC', 'Message', 'Q_GS', 'Message')
fn('Q_IMP', '/Script/Engine.KismetRenderingLibrary', 'ImportFileAsTexture2D',
   EXEC() + [P('Filename', 'string'), P('ReturnValue', 'object', obj=cls('/Script/Engine.Texture2D'), out=True)], X0 + 600, Y2, 'PNG 읽기')
link('Q_GS', 'then', 'Q_IMP', 'execute'); link('Q_GS', 'Value', 'Q_IMP', 'Filename')
fn('Q_MID', '/Script/Engine.PrimitiveComponent', 'CreateDynamicMaterialInstance',
   EXEC() + [P('self', 'object', obj=C_PRIM), P('ElementIndex', 'int', default='0'),
             P('SourceMaterial', 'object', obj=cls('/Script/Engine.MaterialInterface'), defobj='/Game/Exhibition/Materials/M_QR.M_QR'),
             P('ReturnValue', 'object', obj=C_MID, out=True)], X0 + 900, Y2)
link('Q_IMP', 'then', 'Q_MID', 'execute'); link('QRC1', 'StaticMeshComponent', 'Q_MID', 'self')
fn('Q_TEX', '/Script/Engine.MaterialInstanceDynamic', 'SetTextureParameterValue',
   EXEC() + [P('self', 'object', obj=C_MID), P('ParameterName', 'name', default='Tex'),
             P('Value', 'object', obj=cls('/Script/Engine.Texture'))], X0 + 1200, Y2)
link('Q_MID', 'then', 'Q_TEX', 'execute'); link('Q_MID', 'ReturnValue', 'Q_TEX', 'self')
link('Q_IMP', 'ReturnValue', 'Q_TEX', 'Value')
fn('Q_SHOW', '/Script/Engine.MaterialInstanceDynamic', 'SetScalarParameterValue',
   EXEC() + [P('self', 'object', obj=C_MID), P('ParameterName', 'name', default='Show'),
             P('Value', 'real', 'double', default='1.0')], X0 + 1500, Y2, 'QR 화면 켬')
link('Q_TEX', 'then', 'Q_SHOW', 'execute'); link('Q_MID', 'ReturnValue', 'Q_SHOW', 'self')
link('Q_SHOW', 'then', 'F_PRINT', 'execute')
# 다음 관객 입장 → QR 화면 끔 (원래 머티리얼로)
unlink('SET_SNAPT', 'then', 'F_PRINT', 'execute')
fn('E_QROFF', '/Script/Engine.PrimitiveComponent', 'SetMaterial',
   EXEC() + [P('self', 'object', obj=C_PRIM), P('ElementIndex', 'int', default='0'),
             P('Material', 'object', obj=cls('/Script/Engine.MaterialInterface'), defobj='/Game/Exhibition/Materials/M_QR.M_QR')],
   X0 + 300, Y2 + 300, 'enter: QR 화면 끔')
link('SET_SNAPT', 'then', 'E_QROFF', 'execute'); link('QRC1', 'StaticMeshComponent', 'E_QROFF', 'self')
link('E_QROFF', 'then', 'F_PRINT', 'execute')

# ================================================================== 1) 퇴장 → 리셋
Y3 = Y2 + 700
remove('F_QUIT')
chain = []
fn('X_HIDEL', '/Script/Engine.Actor', 'SetActorHiddenInGame',
   EXEC() + [P('self', 'object', obj=C_ACTOR), P('bNewHidden', 'bool', default='true')], X0, Y3, 'exit 2초 뒤: 리셋 (조명 끔)')
link('LIT_W1', 'ReturnValue', 'X_HIDEL', 'self'); link('LIT_W2', 'ReturnValue', 'X_HIDEL', 'self')
fn('X_HIDEV', '/Script/Engine.Actor', 'SetActorHiddenInGame',
   EXEC() + [P('self', 'object', obj=C_ACTOR), P('bNewHidden', 'bool', default='true')], X0 + 300, Y3, '형체 숨김')
link('LIT_V', 'ReturnValue', 'X_HIDEV', 'self')
comp_get('TVC4', '/Script/MediaPlate.MediaPlate', C_MPLATE, 'MediaPlateComponent', C_MPC, X0 + 450, Y3 + 200)
link('LIT_TV', 'ReturnValue', 'TVC4', 'self')
fn('X_TVCLOSE', '/Script/MediaPlate.MediaPlateComponent', 'Close', EXEC() + [P('self', 'object', obj=C_MPC)], X0 + 600, Y3, 'TV 끔')
link('TVC4', 'MediaPlateComponent', 'X_TVCLOSE', 'self')
self_set('X_TV0', 'TargetVol', 'real', 'double', '0.0', X0 + 900, Y3)
self_set('X_VOL0', 'Vol', 'real', 'double', '0.0', X0 + 1150, Y3)
self_set('X_SEAT', 'Seated', 'bool', '', 'false', X0 + 1400, Y3)
self_set('X_SNAP', 'Snap', 'bool', '', 'true', X0 + 1650, Y3)
self_get('GET_MUSIC2', 'MusicComp', 'object', C_AC, X0 + 1750, Y3 + 200)
fn('X_MUS', '/Script/Engine.AudioComponent', 'SetVolumeMultiplier',
   EXEC() + [P('self', 'object', obj=C_AC), P('NewVolumeMultiplier', 'real', 'double', default='0.001')], X0 + 1900, Y3, '음악 아주 작게')
link('GET_MUSIC2', 'MusicComp', 'X_MUS', 'self')
comp_get('FIREAC2', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0 + 2050, Y3 + 200)
link('LIT_FIRE', 'ReturnValue', 'FIREAC2', 'self')
ac_call('X_FIRE', 'Stop', X0 + 2200, Y3, '모닥불 끔')
link('FIREAC2', 'AudioComponent', 'X_FIRE', 'self')
comp_get('SUBAC2', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0 + 2350, Y3 + 200)
link('LIT_SUB', 'ReturnValue', 'SUBAC2', 'self')
ac_call('X_SUB', 'Stop', X0 + 2500, Y3, '지하철 소리 끔')
link('SUBAC2', 'AudioComponent', 'X_SUB', 'self')
fn('X_PRINT', '/Script/Engine.KismetSystemLibrary', 'PrintString',
   EXEC() + [P('InString', 'string', default='RESET: next visitor ready'), P('Duration', 'real', 'double', default='3.0')], X0 + 2800, Y3)
seq = ['F_DELAY', 'X_HIDEL', 'X_HIDEV', 'X_TVCLOSE', 'X_TV0', 'X_VOL0', 'X_SEAT', 'X_SNAP', 'X_MUS', 'X_FIRE', 'X_SUB', 'X_PRINT']
for a, b in zip(seq, seq[1:]):
    link(a, 'then', b, 'execute')
link('LIT_FAN', 'ReturnValue', 'X_HIDEV', 'self')        # 퇴장하면 부채꼴도 숨김

# ================================================================== 6) 소리 세 갈래 (/home/level) + 빠른 반응 (11/19 22:40)
# Python이 '소파에 앉은 시간 → 음악, TV 본 시간 → TV 소리, 담요 덮은 시간 → 모닥불' 볼륨을 계산해 보낸다.
# 언리얼은 받은 값을 그대로 적용만 한다 (조정은 Python config에서). 옛 규칙(앉으면 0.35, 만지면 +0.2, 초당 +0.01)은 지운다.
def setdef(node, pname, val):
    p = pin(node, pname)
    p['raw'] = re.sub(r'DefaultValue="[^"]*"', 'DefaultValue="%s"' % val, p['raw'])
setdef('F_VINTERP', 'InterpSpeed', '12.0')     # 위치 따라가기 (예전 4)
setdef('F_RINTERP', 'InterpSpeed', '20.0')     # 방향 따라가기 (예전 5) — 1인칭 고개가 바로 따라오게
setdef('F_FINTERP', 'InterpSpeed', '1.5')      # 음악 볼륨 따라가기 (예전 0.8)
# 옛 볼륨 규칙 지우기
unlink('SET_SEAT', 'then', 'SET_TV1', 'execute'); unlink('SET_TV1', 'then', 'F_PRINT', 'execute')
for n in ('SET_TV1', 'F_SEL', 'F_MAX', 'GET_TV1'):
    remove(n)
link('SET_SEAT', 'then', 'F_PRINT', 'execute')
unlink('SW', '/home/touch', 'SET_TV2', 'execute'); unlink('SET_TV2', 'then', 'T_GS', 'execute')
for n in ('SET_TV2', 'F_MIN', 'F_ADD', 'GET_TV2'):
    remove(n)
link('SW', '/home/touch', 'T_GS', 'execute')
unlink('F_TURN', 'then', 'SET_TV3', 'execute'); unlink('SET_TV3', 'then', 'SET_VOL', 'execute')
for n in ('SET_TV3', 'F_MIN2', 'F_ADD2', 'F_MUL', 'F_MUL2', 'F_B2D', 'GET_SEAT', 'GET_TV3'):
    remove(n)
link('F_TURN', 'then', 'SET_VOL', 'execute')
self_get('GET_TVX', 'TargetVol', 'real', None, 1700, 2650)
nodes['GET_TVX']['pins'][0]['raw'] = nodes['GET_TVX']['pins'][0]['raw'].replace('PinType.PinSubCategory=""', 'PinType.PinSubCategory="double"')
link('GET_TVX', 'TargetVol', 'F_FINTERP', 'Target')
# TV 소리 (EX_Snd_TV, TV 자리의 앰비언트 사운드)
literal('LIT_TVSND', '/Script/Engine.AmbientSound', TVSND, 900, 160)
Y5 = Y4 + 600
comp_get('TVSAC1', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0 + 600, Y1 + 300)
link('LIT_TVSND', 'ReturnValue', 'TVSAC1', 'self')
fade_in('D_TVSIN', X0 + 900, Y1, '1.0', '1.0', 'door: TV 소리 켬')
unlink('D_SUBOUT', 'then', 'F_PRINT', 'execute')
link('D_SUBOUT', 'then', 'D_TVSIN', 'execute'); link('TVSAC1', 'AudioComponent', 'D_TVSIN', 'self')
link('D_TVSIN', 'then', 'F_PRINT', 'execute')
# /home/level 음악 TV 모닥불
sw['head'].insert(9, '   PinNames(9)="/home/level"')
sw['pins'].append(P('/home/level', out=True))
def getf(name, idx, x, y, comment=None):
    fn(name, '/Script/OSC.OSCManager', 'GetFloat',
       EXEC() + [P('Message', 'struct', obj=OSCMSG, ref=True), P('Index', 'int', default=str(idx)),
                 P('Value', 'real', 'double', out=True), P('ReturnValue', 'bool', out=True)], x, y, comment)
    link('ONOSC', 'Message', name, 'Message')
def setvol(name, x, y, comment):
    fn(name, '/Script/Engine.AudioComponent', 'SetVolumeMultiplier',
       EXEC() + [P('self', 'object', obj=C_AC), P('NewVolumeMultiplier', 'real', 'double', default='0.0')], x, y, comment)
getf('V_G0', 0, X0 + 300, Y5, 'level: 소파 → 음악 볼륨')
self_set('V_SETT', 'TargetVol', 'real', 'double', '0.0', X0 + 600, Y5)
link('SW', '/home/level', 'V_G0', 'execute'); link('V_G0', 'then', 'V_SETT', 'execute'); link('V_G0', 'Value', 'V_SETT', 'TargetVol')
getf('V_G1', 1, X0 + 900, Y5, 'TV 본 시간 → TV 소리')
comp_get('TVSAC2', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0 + 1050, Y5 + 250)
link('LIT_TVSND', 'ReturnValue', 'TVSAC2', 'self')
setvol('V_TV', X0 + 1200, Y5, 'TV 소리 볼륨')
link('V_SETT', 'then', 'V_G1', 'execute'); link('V_G1', 'then', 'V_TV', 'execute')
link('V_G1', 'Value', 'V_TV', 'NewVolumeMultiplier'); link('TVSAC2', 'AudioComponent', 'V_TV', 'self')
getf('V_G2', 2, X0 + 1500, Y5, '담요 덮은 시간 → 모닥불')
comp_get('FIREAC3', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0 + 1650, Y5 + 250)
link('LIT_FIRE', 'ReturnValue', 'FIREAC3', 'self')
setvol('V_FIRE', X0 + 1800, Y5, '모닥불 볼륨')
link('V_TV', 'then', 'V_G2', 'execute'); link('V_G2', 'then', 'V_FIRE', 'execute')
link('V_G2', 'Value', 'V_FIRE', 'NewVolumeMultiplier'); link('FIREAC3', 'AudioComponent', 'V_FIRE', 'self')
# 리셋: TV 소리도 끔
comp_get('TVSAC3', '/Script/Engine.AmbientSound', C_AMB, 'AudioComponent', C_AC, X0 + 2550, Y3 + 350)
link('LIT_TVSND', 'ReturnValue', 'TVSAC3', 'self')
ac_call('X_TVS', 'Stop', X0 + 2650, Y3 + 150, 'TV 소리 끔')
link('TVSAC3', 'AudioComponent', 'X_TVS', 'self')
unlink('X_SUB', 'then', 'X_PRINT', 'execute')
link('X_SUB', 'then', 'X_TVS', 'execute'); link('X_TVS', 'then', 'X_PRINT', 'execute')

# ================================================================== 7) 앉으면 조명 · TV는 만지면 켜짐 (11/19 23:00)
# 문(door): 지하철 소리 2초 페이드아웃만. 조명은 /home/sit 1, TV 영상·TV 소리는 /home/touch tv.
for a, ap, b, bp in [('SW', '/home/door', 'F_SHOWLIGHTS', 'execute'), ('F_SHOWLIGHTS', 'then', 'F_TVOPEN', 'execute'),
                     ('F_TVOPEN', 'then', 'D_SUBOUT', 'execute'), ('D_SUBOUT', 'then', 'D_TVSIN', 'execute'),
                     ('D_TVSIN', 'then', 'F_PRINT', 'execute'), ('SET_SEAT', 'then', 'F_PRINT', 'execute')]:
    unlink(a, ap, b, bp)
link('SW', '/home/door', 'D_SUBOUT', 'execute'); link('D_SUBOUT', 'then', 'F_PRINT', 'execute')
nodes['D_SUBOUT']['head'] = [h.replace('door: 지하철 소리 2초에 걸쳐 잦아듦', 'door: 지하철 소리 2초에 걸쳐 잦아듦 (조명은 앉을 때, TV는 만질 때)') for h in nodes['D_SUBOUT']['head']]
# 앉음(값 1)일 때만 조명 켬
add('S_BR', 'K2Node_IfThenElse', [], [P('execute'), P('Condition', 'bool', default='true'), P('then', out=True), P('else', out=True)],
    1500, 1500, 'sit: 앉으면 집 조명 켬')
link('SET_SEAT', 'then', 'S_BR', 'execute'); link('F_I2B', 'ReturnValue', 'S_BR', 'Condition')
link('S_BR', 'then', 'F_SHOWLIGHTS', 'execute'); link('F_SHOWLIGHTS', 'then', 'F_PRINT', 'execute')
link('S_BR', 'else', 'F_PRINT', 'execute')
nodes['F_SHOWLIGHTS']['head'] = [h.replace('집에 들어옴: 조명 켬', '앉음: 집 조명 켬') for h in nodes['F_SHOWLIGHTS']['head']]
# touch tv → TV 영상 재생 + TV 소리
tsw = nodes['T_SW']
i = max(k for k, h in enumerate(tsw['head']) if 'PinNames(' in h)
tsw['head'].insert(i + 1, '   PinNames(2)="tv"')
tsw['pins'].append(P('tv', out=True))
link('T_SW', 'tv', 'F_TVOPEN', 'execute'); link('F_TVOPEN', 'then', 'D_TVSIN', 'execute')
nodes['F_TVOPEN']['head'] = [h.replace('TV 영상 재생', 'touch tv: TV 영상 재생') for h in nodes['F_TVOPEN']['head']]
nodes['D_TVSIN']['head'] = [h.replace('door: TV 소리 켬', 'touch tv: TV 소리 켬') for h in nodes['D_TVSIN']['head']]

# ================================================================== 8) 채널 차례로 돌리기 · 앉으면 눈높이 낮춤 (11/19 23:20)
# 리모컨: 채널 번호 = 누른 횟수 % 채널 수  (PL_TV: TEST_CH1·2·3, B_home, A_society)
C_PL = cls('/Script/MediaAssets.MediaPlaylist')
for n_ in ('T_URL', 'T_HAS', 'T_SELI'):
    remove(n_)
unlink('T_PON', 'then', 'T_OPEN', 'execute')
# 리모컨 누른 횟수(/home/touch remote 횟수의 둘째 값)로 채널을 정함 → TV 켜짐 CH1(0), 1번 CH2, 2번 CH3, 3번 B_home, 4번 A_society, 5번 다시 CH1
# (플레이어의 GetPlaylistIndex는 채널을 건너뛰는 일이 있어서 쓰지 않음)
fn('C_GI', '/Script/OSC.OSCManager', 'GetInt32',
   EXEC() + [P('Message', 'struct', obj=OSCMSG, ref=True), P('Index', 'int', default='1'),
             P('Value', 'int', out=True), P('ReturnValue', 'bool', out=True)], X0 + 1300, Y0 + 380, 'remote: 누른 횟수')
link('ONOSC', 'Message', 'C_GI', 'Message')
fn('C_NUM', '/Script/MediaAssets.MediaPlaylist', 'Num',
   EXEC() + [P('self', 'object', obj=C_PL, defobj='/Game/Exhibition/Media/PL_TV.PL_TV'), P('ReturnValue', 'int', out=True)],
   X0 + 1400, Y0 + 380, 'remote: 채널 수')
fn('C_MOD', '/Script/Engine.KismetMathLibrary', 'Percent_IntInt',
   [P('A', 'int', default='0'), P('B', 'int', default='1'), P('ReturnValue', 'int', out=True)], X0 + 1750, Y0 + 520)
link('C_GI', 'Value', 'C_MOD', 'A'); link('C_NUM', 'ReturnValue', 'C_MOD', 'B'); link('C_MOD', 'ReturnValue', 'T_OPEN', 'Index')
link('T_PON', 'then', 'C_GI', 'execute'); link('C_GI', 'then', 'C_NUM', 'execute'); link('C_NUM', 'then', 'T_OPEN', 'execute')
nodes['T_OPEN']['head'] = [h.replace('리모컨 → 다른 채널', '리모컨 → 다음 채널 (차례로)') for h in nodes['T_OPEN']['head']]
# 앉음/일어남 → 관객 눈 카메라(형체에 붙음) 높이·기울기. 형체 중심 85cm, 세로 배율 1.7 → 160cm = 44.12, 115cm = 17.65
VEC = "\"/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.Vector'\""
def eye_set(name, z, pitch, x, y, comment):
    fn(name + 'L', '/Script/Engine.Actor', 'K2_SetActorRelativeLocation',
       EXEC() + [P('self', 'object', obj=C_ACTOR), P('NewRelativeLocation', 'struct', obj=VEC, default='66.666667,0.000000,%s' % z),
                 P('bSweep', 'bool', default='false'), P('bTeleport', 'bool', default='true')], x, y, comment)
    fn(name + 'R', '/Script/Engine.Actor', 'K2_SetActorRelativeRotation',
       EXEC() + [P('self', 'object', obj=C_ACTOR), P('NewRelativeRotation', 'struct', obj=ROT, default='%s,0.000000,0.000000' % pitch),
                 P('bSweep', 'bool', default='false'), P('bTeleport', 'bool', default='true')], x + 250, y)
    link('LIT_EYE', 'ReturnValue', name + 'L', 'self'); link('LIT_EYE', 'ReturnValue', name + 'R', 'self')
    link(name + 'L', 'then', name + 'R', 'execute')
eye_set('E_SIT', '17.647059', '-14.000000', 1800, 1450, 'sit 1: 눈높이 115cm (소파에 앉아 TV를 봄)')
eye_set('E_STD', '44.117647', '-6.000000', 1800, 1650, 'sit 0: 눈높이 160cm (서 있음)')
unlink('F_SHOWLIGHTS', 'then', 'F_PRINT', 'execute'); unlink('S_BR', 'else', 'F_PRINT', 'execute')
link('F_SHOWLIGHTS', 'then', 'E_SITL', 'execute'); link('E_SITR', 'then', 'F_PRINT', 'execute')
link('S_BR', 'else', 'E_STDL', 'execute'); link('E_STDR', 'then', 'F_PRINT', 'execute')

# ================================================================== 9) 관리자 소리 계기판 (/home/meter 글자 → 화면 왼쪽 위) (11/19 23:50)
# Python이 각 소리 단계(0~5)와 겹침 단계를 글자로 만들어 0.5초마다 보냄 → 같은 Key로 덮어써서 계기판처럼 보임 (1.5초 안 오면 사라짐)
sw['head'].insert(10, '   PinNames(10)="/home/meter"')
sw['pins'].append(P('/home/meter', out=True))
get_string('M_GS', 0, X0 + 300, Y5 + 500, 'meter: 관리자 계기판 글자')
link('SW', '/home/meter', 'M_GS', 'execute'); link('ONOSC', 'Message', 'M_GS', 'Message')
fn('M_PRINT', '/Script/Engine.KismetSystemLibrary', 'PrintString',
   EXEC() + [P('InString', 'string', default=''), P('bPrintToScreen', 'bool', default='true'), P('bPrintToLog', 'bool', default='false'),
             P('TextColor', 'struct', obj="\"/Script/CoreUObject.ScriptStruct'/Script/CoreUObject.LinearColor'\"",
               default='(R=1.000000,G=0.850000,B=0.350000,A=1.000000)'),
             P('Duration', 'real', 'double', default='1.5'), P('Key', 'name', default='HOME_METER')], X0 + 600, Y5 + 500, '계기판 표시 (같은 Key로 덮어씀)')
link('M_GS', 'then', 'M_PRINT', 'execute'); link('M_GS', 'Value', 'M_PRINT', 'InString')
# 신호 이름 디버그 글자는 화면에 안 찍고 로그로만 (계기판을 가리지 않게)
for n_ in ('F_PRINT', 'X_PRINT'):
    nodes[n_]['pins'].append(P('bPrintToScreen', 'bool', default='false'))

# ================================================================== 10) 채널 하나만 반복 (11/20)
# 영상이 끝나면 다음 채널로 넘기는 건 TV 판(MediaPlate 컴포넌트)이 자기 재생목록으로 직접 함 →
# 판에는 영상 1개짜리 PL_NOW를 물려 두고(언리얼에서 설정·저장, Saved/pl1120.py), 채널을 바꿀 땐
# PL_NOW의 그 한 칸을 PL_TV.Get(번호)로 바꿔 끼운 뒤 판 Open() → 목록에 하나뿐이라 그 채널만 반복
C_MSRC = cls('/Script/MediaAssets.MediaSource')
PLNOW = '/Game/Exhibition/Media/PL_NOW.PL_NOW'
def pl_get(name, x, y, comment, index='0'):
    fn(name, '/Script/MediaAssets.MediaPlaylist', 'Get',
       EXEC() + [P('self', 'object', obj=C_PL, defobj='/Game/Exhibition/Media/PL_TV.PL_TV'),
                 P('Index', 'int', default=index), P('ReturnValue', 'object', obj=C_MSRC, out=True)], x, y, comment)
def pl_replace(name, x, y, comment):
    fn(name, '/Script/MediaAssets.MediaPlaylist', 'Replace',
       EXEC() + [P('self', 'object', obj=C_PL, defobj=PLNOW), P('Index', 'int', default='0'),
                 P('Replacement', 'object', obj=C_MSRC), P('ReturnValue', 'bool', out=True)], x, y, comment)
def plate_open(name, tvc, x, y, comment):
    fn(name, '/Script/MediaPlate.MediaPlateComponent', 'Open', EXEC() + [P('self', 'object', obj=C_MPC)], x, y, comment)
    link(tvc, 'MediaPlateComponent', name, 'self')
# 리모컨: C_NUM → Get(횟수%5) → PL_NOW 바꿔 끼움 → 판 Open → 지지직
remove('T_OPEN')
pl_get('C_GET', 4000, 2980, 'remote: 이 채널 영상')
pl_replace('C_REP', 4300, 2980, 'remote: PL_NOW 한 칸을 이 채널로')
plate_open('C_POPEN', 'TVC3', 4600, 2850, '리모컨 → 그 채널만 반복 (판 Open)')
link('C_NUM', 'then', 'C_GET', 'execute'); link('C_MOD', 'ReturnValue', 'C_GET', 'Index')
link('C_GET', 'then', 'C_REP', 'execute'); link('C_GET', 'ReturnValue', 'C_REP', 'Replacement')
link('C_REP', 'then', 'C_POPEN', 'execute'); link('C_POPEN', 'then', 'T_STATIC', 'execute')
# TV 켜기(touch tv): PL_NOW를 CH1로 되돌린 뒤 판 Open (F_TVOPEN)
unlink('T_SW', 'tv', 'F_TVOPEN', 'execute')
pl_get('V_GET0', 1100, 850, 'touch tv: CH1 영상')
pl_replace('V_REP', 1400, 850, 'touch tv: PL_NOW를 CH1로')
link('T_SW', 'tv', 'V_GET0', 'execute'); link('V_GET0', 'then', 'V_REP', 'execute')
link('V_GET0', 'ReturnValue', 'V_REP', 'Replacement'); link('V_REP', 'then', 'F_TVOPEN', 'execute')

# ------------------------------------------------------------------ 쓰기
out = []
for name in order:
    n = nodes[name]
    out.append('Begin Object Class=%s Name="%s"' % (n['klass'], name))
    out += n['head']
    for p in n['pins']:
        raw = p['raw']
        lk = ''.join('%s %s,' % l for l in p['links'])
        if p['links']:
            raw = raw.replace('PersistentGuid=', 'LinkedTo=(%s),PersistentGuid=' % lk, 1)
        out.append(raw)
    out.append('End Object')
open(DST, 'w', encoding='utf-8').write('\n'.join(out) + '\n')

# 검사: 모든 링크가 양쪽에 있는지
ids = {(nm, p['id']): p for nm in nodes for p in nodes[nm]['pins']}
bad = 0
for nm in nodes:
    for p in nodes[nm]['pins']:
        for l in p['links']:
            q = ids.get(l)
            if not q or (nm, p['id']) not in q['links']:
                bad += 1; print('BAD LINK', nm, p['name'], l)
print('nodes', len(order), 'bad links', bad, '->', DST)
