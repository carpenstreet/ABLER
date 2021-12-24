import psutil


def is_first_open():
    # 윈도우에선 blender.exe로 인식
    process_count = sum(
        i.startswith("ABLER") or i.startswith("blender")
        for i in (p.name() for p in psutil.process_iter())
    )
    return process_count <= 1
