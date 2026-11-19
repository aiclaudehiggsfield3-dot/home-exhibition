# -*- coding: utf-8 -*-
# bp_v4.t3d(현재 레벨 블루프린트)에 11/19 기능을 더해 bp_v5.t3d를 만든다.
#  1) 퇴장 → 플레이 종료 대신 리셋  2) touch 이름별(담요=모닥불, 리모컨=채널+지지직)
#  3) /home/train → 지하철 소리, 문(door)에서 페이드아웃  4) /home/result → QR_Screen에 QR 이미지
# 사용: python3 gen_bp1119.py <Saved 폴더>
import re, sys, uuid

SV = sys.argv[1] if len(sys.argv) > 1 else '.'
SRC, DST = SV + '/bp_v4.t3d', SV + '/bp_v5.t3d'
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
   EXEC() + [P('self', 'object', obj=C_AC), P('FadeOutDuration', 'real', 'double', default='1.5'),
             P('FadeVolumeLevel', 'real', 'double', default='0.0')], X0 + 600, Y1, 'door: 지하철 소리 끊김')
link('F_TVOPEN', 'then', 'D_SUBOUT', 'execute'); link('SUBAC1', 'AudioComponent', 'D_SUBOUT', 'self')
link('D_SUBOUT', 'then', 'F_PRINT', 'execute')

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
