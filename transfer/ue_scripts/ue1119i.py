import unreal as _u; SV_=_u.Paths.convert_relative_path_to_full(_u.Paths.project_saved_dir())  # 이 프로젝트의 Saved/ (어느 컴퓨터든)
import unreal, traceback
L=[]
try:
    bp=unreal.find_object(None,'/Game/Exhibition/Maps/L_Current.L_Current:PersistentLevel.L_Current')
    L.append('bp='+str(bp))
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
    L.append('compiled')
    try:
        L.append('status='+str(bp.get_editor_property('status')))
    except Exception as e:
        L.append('status? '+str(e)[:120])
    unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True)
    L.append('saved')
except Exception:
    L.append(traceback.format_exc())
open(SV_+'ue1119i.txt','w').write('\n'.join(L))
