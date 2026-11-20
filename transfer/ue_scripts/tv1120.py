import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
import unreal, time, traceback
exec(open(SV_+'p5.py').read(), globals())
OUTT=SV_+'tv1120.txt'
open(OUTT,'w').write('--- tv1120 start\n')
PLAN=[(3,'enter'),(4,'tv'),(22,'remote1'),(40,'remote2'),(58,'end')]
S={'t0':None,'done':set(),'last':0,'h':None}
def log(s): open(OUTT,'a').write(s+'\n')
def snap(tag):
    w=unreal.EditorLevelLibrary.get_game_world()
    if not w: log(tag+' no world'); return
    A={a.get_actor_label():a for a in unreal.GameplayStatics.get_all_actors_of_class(w,unreal.Actor)}
    mp=A['EX_Screen_B_Home'].get_editor_property('media_plate_component').get_media_player()
    log('%s url=%s playing=%s t=%.1f/%.1f idx=%s loop=%s' % (tag,(mp.get_url() or '').split('/')[-1],mp.is_playing(),
        mp.get_time().get_total_seconds() if hasattr(mp.get_time(),'get_total_seconds') else -1,
        mp.get_duration().get_total_seconds() if hasattr(mp.get_duration(),'get_total_seconds') else -1,
        mp.get_playlist_index(), mp.is_looping()))
def tick(dt):
    try:
        if S['t0'] is None: S['t0']=time.time()
        e=time.time()-S['t0']
        for at,what in PLAN:
            if e>=at and what not in S['done']:
                S['done'].add(what); log('>> %.1f %s'%(e,what))
                if what=='enter': osc('/home/enter',1); osc('/home/pos',150.0,200.0)
                elif what=='tv': osc('/home/touch','tv',1)
                elif what=='remote1': osc('/home/touch','remote',1)
                elif what=='remote2': osc('/home/touch','remote',2)
                elif what=='end':
                    snap('final'); unreal.unregister_slate_post_tick_callback(S['h'])
                    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_request_end_play(); log('ended'); return
        if e-S['last']>=2 and e>5:
            S['last']=e; snap('%5.1f'%e)
    except Exception:
        log('ERR '+traceback.format_exc()[-500:])
        try: unreal.unregister_slate_post_tick_callback(S['h'])
        except Exception: pass
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).editor_play_simulate()
S['h']=unreal.register_slate_post_tick_callback(tick)
