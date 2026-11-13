# walk_one.py — Saved/one.txt 에 적힌 레벨 하나만 워크스루 렌더
import unreal, re
key=open(unreal.Paths.project_saved_dir()+'one.txt').read().strip()
src=open(unreal.Paths.project_dir()+'Scripts/make_walkthrough.py',encoding='utf-8').read()
src=re.sub(r'^LAYOUTS = \[.*?\]', 'LAYOUTS = ["%s"]'%key, src, count=1, flags=re.M)
exec(compile(src,'make_walkthrough','exec'),{'__name__':'__main__'})
