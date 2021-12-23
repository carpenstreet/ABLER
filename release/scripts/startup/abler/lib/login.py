import re
import subprocess


def is_first_open():
    # 영어일때는 `ignore` 인자 없어도 됨
    tasks = (
        subprocess.check_output(["tasklist"]).decode("cp949", "ignore").split("\r\n")
    )
    p = []
    for task in tasks:
        m = re.match("(.+?) +(\d+) (.+?) +(\d+) +(\d+.* K).*", task)
        if m is not None:
            p.append(m.group(1))
    cnt = 0

    for i in p:
        if i.startswith("blender") or i.startswith("ABLER"):
            cnt += 1

    if cnt > 1:
        return False
    else:
        return True
