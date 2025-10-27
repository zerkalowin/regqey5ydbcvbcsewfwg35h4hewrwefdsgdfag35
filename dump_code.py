import importlib.util, importlib.machinery, sys, marshal, types, os

ENTRY = "/workspace/Linux/smm.py"
sys.path.insert(0, "/workspace/Linux")

os.makedirs("/workspace/_dump", exist_ok=True)

spec = importlib.util.spec_from_loader("smm_entry", importlib.machinery.SourceFileLoader("smm_entry", ENTRY))
mod = importlib.util.module_from_spec(spec)
sys.modules["smm_entry"] = mod
spec.loader.exec_module(mod)

import smm

visited = set()
out_idx = 0

def dump_codeobj(co: types.CodeType, tag: str="root"):
    global out_idx
    if not isinstance(co, types.CodeType):
        return
    if id(co) in visited:
        return
    visited.add(id(co))
    path = f"/workspace/_dump/{out_idx:04d}_{tag}.pyc"
    with open(path, "wb") as f:
        f.write(b"\x42\x0d\x0d\x0a")
        f.write(b"\x00\x00\x00\x00")
        f.write(b"\x00\x00\x00\x00")
        marshal.dump(co, f)
    out_idx += 1
    for const in co.co_consts or ():
        if isinstance(const, types.CodeType):
            dump_codeobj(const, tag)

for name in dir(smm):
    obj = getattr(smm, name)
    if isinstance(obj, types.FunctionType):
        dump_codeobj(obj.__code__, f"smm.{name}")
    if isinstance(obj, type):
        for k, v in obj.__dict__.items():
            if isinstance(v, types.FunctionType):
                dump_codeobj(v.__code__, f"smm.{obj.__name__}.{k}")

print(f"dumped {out_idx} code objects to /workspace/_dump")
