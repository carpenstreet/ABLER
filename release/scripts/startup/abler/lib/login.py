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

        process_count = sum(
            bool(i.startswith("blender") or i.startswith("ABLER") for i in p)
        )
        return process_count <= 1

    elif platform.system() == "Darwin":
        process_count = os.popen("ps -Af").read().count("ABLER")
        return process_count <= 2

    elif platform.system() == "Linux":
        print("Linux")
        return None
