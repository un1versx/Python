#!/usr/bin/env python3
"""Tree - private text encryption tool."""

import base64
import getpass
import os
import sys

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

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


MAGIC = b"TREE-SECURE-v1"
SALT_LEN = 16
NONCE_LEN = 12
ITERATIONS = 600_000

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


def derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_text(text: str) -> str:
    password = getpass.getpass("Create password: ")
    confirm = getpass.getpass("Confirm password: ")

    if not password:
        raise ValueError("Password cannot be empty.")
    if password != confirm:
        raise ValueError("Passwords do not match.")

    salt = os.urandom(SALT_LEN)
    nonce = os.urandom(NONCE_LEN)
    key = derive_key(password, salt)

    encrypted = AESGCM(key).encrypt(nonce, text.encode("utf-8"), None)
    package = MAGIC + salt + nonce + encrypted

    return base64.b64encode(package).decode("ascii")


def decrypt_text(encoded: str) -> str:
    password = getpass.getpass("Enter password (input is hidden): ")

    if not password:
        raise ValueError("Password cannot be empty.")

    try:
        package = base64.b64decode(encoded.strip(), validate=True)

        minimum_length = len(MAGIC) + SALT_LEN + NONCE_LEN + 16
        if len(package) < minimum_length:
            raise ValueError

        if not package.startswith(MAGIC):
            raise ValueError

        pos = len(MAGIC)
        salt = package[pos:pos + SALT_LEN]
        pos += SALT_LEN
        nonce = package[pos:pos + NONCE_LEN]
        pos += NONCE_LEN
        encrypted = package[pos:]

        key = derive_key(password, salt)
        plaintext = AESGCM(key).decrypt(nonce, encrypted, None)

        return plaintext.decode("utf-8")

    except Exception:
        raise ValueError(
            "Decryption failed: wrong password or damaged data."
        ) from None


def main() -> None:
    cprint(BANNER)
    cprint("1) Encrypt")
    cprint("2) Decrypt")

    choice = input("Choose 1 or 2: ").strip()

    if choice == "1":
        text = input("Text to encrypt: ")
        cprint("\nEncrypted data:")
        cprint(encrypt_text(text))

    elif choice == "2":
        encoded = input("Paste encrypted data: ").strip()

        # Get and verify the password before displaying the output heading.
        result = decrypt_text(encoded)

        cprint("\nDecrypted text:")
        cprint(result)

    else:
        raise ValueError("Invalid choice. Please choose 1 or 2.")


def run() -> None:
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\nCancelled.")
    except (EOFError, ValueError) as exc:
        cprint(f"\n\nError: {exc}")
    except Exception as exc:
        cprint(f"\n\nUnexpected error: {type(exc).__name__}: {exc}")
    finally:
        # Keeps the window open after an error or after successful execution.
        try:
            input("\nPress Enter to exit...")
        except (EOFError, KeyboardInterrupt):
            pass


if __name__ == "__main__":
    run()
