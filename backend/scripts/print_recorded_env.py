import os
keys = sorted([k for k in os.environ.keys() if ("SID" in k.upper() or "SESSION" in k.upper())])
for k in keys:
    print(k, "=", os.environ.get(k))
