import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
import socket, struct, unreal
def _pad(b): b+=b'\0'; return b+b'\0'*((4-len(b)%4)%4)
def osc(addr,*args):
    tt=','+''.join('f' if isinstance(a,float) else 'i' if isinstance(a,int) else 's' for a in args)
    b=_pad(addr.encode())+_pad(tt.encode())
    for a in args:
        b+=struct.pack('>f',a) if isinstance(a,float) else struct.pack('>i',a) if isinstance(a,int) else _pad(a.encode())
    socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(b,('127.0.0.1',8000))
def st(tag):
    import traceback
    try: _st(tag)
    except Exception: open(SV_+'p4.txt','a').write(tag+' ERR '+traceback.format_exc()+'\n')
def _st(tag):
    w=unreal.EditorLevelLibrary.get_game_world()
    if not w:
        open(SV_+'p4.txt','a').write(tag+': (no game world)\n'); return
    acts={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)}
    v=acts.get('EX_Visitor'); l=v.get_actor_location(); r=v.get_actor_rotation()
    tv=acts['EX_Screen_B_Home'].get_editor_property('media_plate_component')
    pcs=unreal.GameplayStatics.get_num_player_controllers(w) if hasattr(unreal.GameplayStatics,'get_num_player_controllers') else '?'
    s=f"{tag}: visitor hidden={v.is_hidden_ed() if False else v.get_editor_property('hidden')} loc=({l.x:.0f},{l.y:.0f},{l.z:.0f}) yaw={r.yaw:.0f} warm1={'OFF' if acts['EX_Light_B_Warm_1'].get_editor_property('hidden') else 'ON'} tvplaying={tv.get_editor_property('is_media_plate_playing') if False else getattr(tv,'is_media_plate_playing','?')} pcs={pcs}"
    try:
        lb=unreal.load_object(None,w.get_path_name().split(':')[0]+':PersistentLevel.L_Current') 
    except Exception: pass
    open(SV_+'p4.txt','a').write(s+'\n')
open(SV_+'p4.txt','a').write('loaded\n')
