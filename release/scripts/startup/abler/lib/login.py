import re, os
import subprocess
import platform
import psutil


def is_first_open():
    process_count = sum(
        i.startswith("ABLER") or i.startswith("blender")
        for i in (p.name() for p in psutil.process_iter())
    )
    return process_count <= 1
