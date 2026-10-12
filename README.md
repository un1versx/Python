# How to Run These Scripts

All four scripts are plain Python files. General steps for any of them:

1. Install Python 3 if you don't have it: https://www.python.org/downloads/
   (while installing, tick **"Add Python to PATH"**).
2. Put the script's folder path in mind, then open **Command Prompt** (search
   "cmd" in the Start menu).
3. `cd` into the folder where the `.py` file is saved, e.g.:
   ```
   cd C:\Users\YourName\Downloads
   ```
4. Run the script with:
   ```
   python filename.py
   ```
   (if `python` doesn't work, try `py filename.py`)

Each script prints its own menu/instructions once it starts, in red text
with a black-hole banner at the top.

---

## 1. Tree.py - Text Encryption Tool

Encrypts/decrypts any text with a password (AES-GCM).

```
python Tree.py
```

- Choose `1` to encrypt text (you'll set a password).
- Choose `2` to decrypt text (paste the encrypted data + enter the same
  password).
- **Requires:** `pip install cryptography colorama`

---

## 2. shutdown_timer.py - Auto Shutdown Timer

Shuts your PC down automatically after a set amount of time.

```
python shutdown_timer.py
```

- Pick a time unit (`h` for hours, `m` for minutes, `s` for seconds), enter
  the value, and confirm.
- A countdown starts; press `Ctrl+C` any time to cancel.
- Windows only (uses the `shutdown` command).
- **Requires:** `pip install colorama`

---

## 3. ram_cleaner.py - Close Background Apps

Closes every other running app/process to free up RAM, keeping only this
script and essential Windows system processes alive.

```
python ram_cleaner.py
```

- Type `yes` when asked to confirm (save your other work first!).
- Shows a list of what got closed, what got skipped (core system
  processes), and what it couldn't close (needs admin rights for those).
- **Requires:** `pip install psutil colorama`
- Tip: run Command Prompt **as Administrator** if you want it to be able to
  close more processes.

---

## 4. battery_saver.py - Extend Battery Life

Helps a laptop's battery last longer in three optional steps.

```
python battery_saver.py
```

- Step 1 (automatic): switches the Windows power plan to **Power saver**.
- Step 2 (asks y/n): lowers screen brightness to a percentage you choose.
- Step 3 (asks y/n, then needs `yes` to confirm): closes extra background
  apps, same as `ram_cleaner.py`.
- **Requires:** `pip install psutil wmi colorama`
  (brightness and background-app steps are skipped automatically if their
  package isn't installed - the rest still works)

---

## Quick install (all scripts at once)

```
pip install cryptography colorama psutil wmi
```

## Notes

- All four are Windows-focused; `Tree.py` works on any OS.
- None of them ever close silently - every script pauses with
  "Press Enter to exit..." before closing, even if something goes wrong.
- `ram_cleaner.py` and the background-apps step in `battery_saver.py` never
  touch core Windows processes (explorer.exe, svchost.exe, lsass.exe, etc.)
  or the script itself.
