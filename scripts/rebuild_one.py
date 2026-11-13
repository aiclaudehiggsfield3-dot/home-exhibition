# rebuild_one.py — Saved/one.txt 에 적힌 레벨 하나만 다시 짓기
import unreal, re
key=open(unreal.Paths.project_saved_dir()+'one.txt').read().strip()
src=open(unreal.Paths.project_dir()+'Scripts/build_layouts.py',encoding='utf-8').read()
src=re.sub(r'^BUILD = \[.*?\]', 'BUILD = ["%s"]'%key, src, count=1, flags=re.M)
src=re.sub(r'^OPEN_AFTER = ".*?"', 'OPEN_AFTER = "%s"'%key, src, count=1, flags=re.M)
exec(compile(src,'build_layouts','exec'),{'__name__':'__main__'})
