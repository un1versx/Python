#!/usr/bin/env python3
"""
RAM Cleaner - closes other background apps so only this script keeps running.

Requires: pip install psutil
Windows-focused (uses a Windows critical-process whitelist), but the
process-closing logic itself works cross-platform.
"""

import os
import sys

RED = "\033[91m"
RESET = "\033[0m"


def cprint(*args, **kwargs):
    """print() wrapper that renders everything in red."""
    text = " ".join(str(a) for a in args)
    print(f"{RED}{text}{RESET}", **kwargs)


def pause_before_exit():
    """Always keep the window open so it never just flashes and closes."""
    try:
        input("\nPress Enter to exit...")
    except (EOFError, KeyboardInterrupt):
        pass


BANNER = r"""
                 .                  .                  .
          .            _________            .
                    ,o88888888888o,
      .          ,88888888888888888o          .
               ,8888888'       `8888888,
             ,8888888'   EVENT    `8888888,
            d8888888'   HORIZON     8888888b      .
           d8888888                  8888888b
    .      88888888   .--.___         88888888      .
           88888888  ( o  )__/\/\/\   88888888
           d8888888   \  ----  /      8888888b
            Y8888888   '.______.'   8888888P
             `8888888o            o8888888'
      .        `8888888o,,,,,o8888888'        .
                   `Y8888888888888P'
          .            `"""""""`            .
                 .                  .
        .   RAM Cleaner. Everything else goes quiet.   .
"""

# Processes that must never be killed - touching these can crash
# or lock up the operating system.
SYSTEM_WHITELIST = {
    "system idle process", "system", "registry",
    "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
    "services.exe", "lsass.exe", "lsaiso.exe", "svchost.exe",
    "explorer.exe", "dwm.exe", "fontdrvhost.exe", "sihost.exe",
    "taskhostw.exe", "ctfmon.exe", "userinit.exe", "spoolsv.exe",
    "wudfhost.exe", "runtimebroker.exe", "shellexperiencehost.exe",
    "searchindexer.exe", "searchapp.exe", "startmenuexperiencehost.exe",
    "audiodg.exe", "conhost.exe", "dllhost.exe",
    # Unix/macOS basics, in case this runs there
    "systemd", "init", "launchd", "kernel_task", "windowserver",
    "loginwindow", "finder",
}

# Never kill this script's own process tree or its shell.
SELF_WHITELIST = {"python.exe", "python3", "python", "pythonw.exe", "cmd.exe", "powershell.exe"}


def is_protected(proc_name: str, pid: int) -> bool:
    name = proc_name.lower()
    if pid in (0, 4):  # System Idle / System on Windows
        return True
    if name in SYSTEM_WHITELIST:
        return True
    if name in SELF_WHITELIST:
        return True
    return False


def close_background_processes(psutil):
    my_pid = os.getpid()
    my_ancestors = set()
    try:
        p = psutil.Process(my_pid)
        while p is not None:
            my_ancestors.add(p.pid)
            p = p.parent()
    except psutil.Error:
        pass

    closed = []
    skipped = []
    failed = []

    for proc in psutil.process_iter(["pid", "name", "username"]):
        try:
            pid = proc.info["pid"]
            name = proc.info["name"] or ""
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        if pid == my_pid or pid in my_ancestors:
            continue
        if is_protected(name, pid):
            skipped.append(name)
            continue

        try:
            proc.terminate()
            closed.append(f"{name} (PID {pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            failed.append(f"{name} (PID {pid})")

    return closed, skipped, failed


def main():
    try:
        import colorama
        colorama.init()
    except ImportError:
        pass

    try:
        import psutil
    except ImportError:
        cprint("This script needs the 'psutil' package, which isn't installed.")
        cprint("Install it first by running:")
        cprint("    pip install psutil")
        return

    cprint(BANNER)
    cprint("This will close every other running app/background process")
    cprint("on this machine, keeping only this script (and core Windows")
    cprint("system processes) running.")
    cprint("Save your work in other programs before continuing.\n")

    confirm = input("Type 'yes' to continue: ").strip().lower()
    if confirm != "yes":
        cprint("\nCancelled. Nothing was closed.")
        return

    cprint("\nClosing background processes...\n")
    closed, skipped, failed = close_background_processes(psutil)

    cprint(f"Closed: {len(closed)} process(es).")
    for item in closed:
        cprint(f"  - {item}")

    if failed:
        cprint(f"\nCould not close {len(failed)} process(es) (needs admin rights):")
        for item in failed:
            cprint(f"  - {item}")

    cprint(f"\n{len(skipped)} core system process(es) were left untouched for stability.")
    cprint("\nDone. Only this script and essential system processes are running.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\nCancelled.")
    except Exception as exc:
        cprint(f"\n\nUnexpected error: {type(exc).__name__}: {exc}")
    finally:
        pause_before_exit()
