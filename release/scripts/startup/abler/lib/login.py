import re, os
import subprocess
import platform


def is_first_open():
    if platform.system() == "Windows":
        tasks = (
            subprocess.check_output(["tasklist"])
            .decode("cp949", "ignore")
            .split("\r\n")
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

    elif platform.system() == "Darwin":
        tmp = os.popen("ps -Af").read()
        proccount = tmp.count("ABLER")

        if proccount > 2:
            return False
        else:
            return True

    elif platform.system() == "Linux":
        print("Linux")
        return None
