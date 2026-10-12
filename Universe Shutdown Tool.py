import time
import os
import sys

try:
    import colorama
    colorama.init()
except ImportError:
    pass

RED = "\033[91m"
RESET = "\033[0m"


def cprint(*args, **kwargs):
    """print() wrapper that renders everything in red."""
    text = " ".join(str(a) for a in args)
    print(f"{RED}{text}{RESET}", **kwargs)


BANNER = r"""
                 .                  .                  .
          .            _________            .
                    ,o88888888888o,
      .          ,88888888888888888o          .
               ,8888888'       `8888888,
             ,8888888'   EVENT    `8888888,
            d8888888'   HORIZON     8888888b      .
           d8888888                  8888888b
    .      88888888    .-------.     88888888      .
           88888888  _/ ' . . ' \_   88888888
           d8888888  \\.         ./  8888888b
            Y8888888  `.       .'  8888888P
             `8888888o   `---'   o8888888'
      .        `8888888o,,,,,o8888888'        .
                   `Y8888888888888P'
          .            `"""""""`            .
                 .                  .
        .   Singularity encryption. Nothing escapes it.   .
"""


def shutdown_after_timer():
    cprint(BANNER)
    cprint("_" * 40)
    cprint("   Auto Shutdown Timer")
    cprint("_" * 40)

    while True:
        try:
            unit = input("\nTime unit (h=hours, m=minutes, s=seconds): ").strip().lower()

            if unit == 'h':
                val = float(input("How many hours? "))
                seconds = int(val * 3600)
            elif unit == 'm':
                val = float(input("How many minutes? "))
                seconds = int(val * 60)
            elif unit == 's':
                seconds = int(input("How many seconds? "))
            else:
                cprint("Invalid input! Type h, m or s.")
                continue

            if seconds <= 0:
                cprint("Time must be greater than 0!")
                continue

            # Confirm
            mins, secs = divmod(seconds, 60)
            hrs, mins = divmod(mins, 60)
            cprint(f"\nShutdown will happen after {hrs}h {mins}m {secs}s.")
            confirm = input("Confirm? (y/n): ").strip().lower()
            if confirm != 'y':
                continue

            break
        except ValueError:
            cprint("Numbers only, please!")

    cprint(f"\n{'=' * 40}")
    cprint("  Countdown starting...")
    cprint("  (Press Ctrl+C to cancel)")
    cprint(f"{'=' * 40}\n")

    try:
        for i in range(seconds, 0, -1):
            mins, secs = divmod(i, 60)
            hrs, mins = divmod(mins, 60)
            sys.stdout.write(f"\r{RED}Time left: {hrs:02d}:{mins:02d}:{secs:02d}{RESET}  ")
            sys.stdout.flush()
            time.sleep(1)

        cprint("\n\nTime's up! Shutting down...")
        time.sleep(2)
        os.system("shutdown /s /t 0")

    except KeyboardInterrupt:
        cprint("\n\nCancelled. Your PC is safe.")

if __name__ == "__main__":
    shutdown_after_timer()
