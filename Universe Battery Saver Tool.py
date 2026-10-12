#!/usr/bin/env python3
"""
Battery Saver - helps your laptop's battery last longer.

What it does (Windows):
  1) Switches the active power plan to "Power saver".
  2) Lowers screen brightness (optional, needs the 'wmi' package;
     pip install wmi).
  3) Optionally closes extra background apps that drain battery
     (keeps core Windows processes running).

Safe to run without admin rights for steps 1 and 2; closing other
apps in step 3 is always confirmed before anything happens.
"""

import os
import subprocess
import sys

RED = "\033[91m"
RESET = "\033[0m"


def cprint(*args, **kwargs):
    """print() wrapper that renders everything in red."""
    text = " ".join(str(a) for a in args)
    print(f"{RED}{text}{RESET}", **kwargs)


def pause_before_exit():
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
        .   Battery Saver. Make the charge last.   .
"""

# Windows built-in GUID for the "Power saver" plan.
POWER_SAVER_GUID = "a1841308-3541-4fab-bc81-f71556f20b4a"

# Same safety list used elsewhere: never touch these.
SYSTEM_WHITELIST = {
    "system idle process", "system", "registry",
    "smss.exe", "csrss.exe", "wininit.exe", "winlogon.exe",
    "services.exe", "lsass.exe", "lsaiso.exe", "svchost.exe",
    "explorer.exe", "dwm.exe", "fontdrvhost.exe", "sihost.exe",
    "taskhostw.exe", "ctfmon.exe", "userinit.exe", "spoolsv.exe",
    "wudfhost.exe", "runtimebroker.exe", "shellexperiencehost.exe",
    "searchindexer.exe", "searchapp.exe", "startmenuexperiencehost.exe",
    "audiodg.exe", "conhost.exe", "dllhost.exe",
    "systemd", "init", "launchd", "kernel_task", "windowserver",
    "loginwindow", "finder",
}
SELF_WHITELIST = {"python.exe", "python3", "python", "pythonw.exe", "cmd.exe", "powershell.exe"}


def switch_to_power_saver():
    if os.name != "nt":
        cprint("Power-plan switching only works on Windows (skipped).")
        return
    try:
        subprocess.run(
            ["powercfg", "/s", POWER_SAVER_GUID],
            check=True, capture_output=True, text=True,
        )
        cprint("Power plan switched to: Power saver.")
    except FileNotFoundError:
        cprint("Could not find 'powercfg' (are you on Windows?).")
    except subprocess.CalledProcessError as exc:
        cprint(f"Could not switch power plan: {exc.stderr.strip() or exc}")


def lower_brightness():
    if os.name != "nt":
        cprint("Brightness control only works on Windows (skipped).")
        return
    try:
        import wmi
    except ImportError:
        cprint("Skipping brightness step - needs the 'wmi' package.")
        cprint("Install it with:  pip install wmi")
        return

    try:
        level_str = input("Set screen brightness to what percent (e.g. 40)? ").strip()
        level = max(0, min(100, int(level_str)))
    except ValueError:
        cprint("Not a valid number, skipping brightness change.")
        return

    try:
        c = wmi.WMI(namespace="wmi")
        methods = c.WmiMonitorBrightnessMethods()[0]
        methods.WmiSetBrightness(level, 0)
        cprint(f"Screen brightness set to {level}%.")
    except Exception as exc:
        cprint(f"Could not change brightness (some laptops/monitors don't support this): {exc}")


def is_protected(proc_name: str, pid: int) -> bool:
    name = proc_name.lower()
    if pid in (0, 4):
        return True
    if name in SYSTEM_WHITELIST or name in SELF_WHITELIST:
        return True
    return False


def trim_background_apps():
    try:
        import psutil
    except ImportError:
        cprint("Skipping this step - needs the 'psutil' package.")
        cprint("Install it with:  pip install psutil")
        return

    cprint("\nThis will close other running apps to save battery/CPU power.")
    cprint("Core Windows system processes are left alone.")
    confirm = input("Type 'yes' to close other background apps: ").strip().lower()
    if confirm != "yes":
        cprint("Skipped. Nothing was closed.")
        return

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
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            pid = proc.info["pid"]
            name = proc.info["name"] or ""
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if pid == my_pid or pid in my_ancestors or is_protected(name, pid):
            continue
        try:
            proc.terminate()
            closed.append(f"{name} (PID {pid})")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    cprint(f"Closed {len(closed)} background app(s).")
    for item in closed:
        cprint(f"  - {item}")


def main():
    try:
        import colorama
        colorama.init()
    except ImportError:
        pass

    cprint(BANNER)
    cprint("Battery Saver - a few steps to stretch your laptop's charge.\n")

    switch_to_power_saver()
    print()

    if input("Lower screen brightness too? (y/n): ").strip().lower() == "y":
        lower_brightness()
    print()

    if input("Close extra background apps to save power? (y/n): ").strip().lower() == "y":
        trim_background_apps()

    cprint("\nDone. Your laptop is now set up to save battery.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\nCancelled.")
    except Exception as exc:
        cprint(f"\n\nUnexpected error: {type(exc).__name__}: {exc}")
    finally:
        pause_before_exit()
