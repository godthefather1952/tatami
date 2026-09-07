#!/usr/bin/env python3
from motionforge.system.diagnostics import run_diagnostics
print("MOTIONFORGE DIAGNOSTICS\n")
failed=False
for name,status,detail in run_diagnostics():
    print(f"{name:.<22} {status:4}  {detail}")
    failed |= status=="FAIL"
raise SystemExit(1 if failed else 0)
