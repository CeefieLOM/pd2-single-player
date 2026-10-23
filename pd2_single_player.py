#!/usr/bin/env python3
"""Unlock (or re-lock) Single Player in a Project Diablo 2 install.

ProjectDiablo.dll carries a list of byte patches it writes into the game's
DLLs at startup. Its first entry rewrites D2Launch.dll+0x17ec4 from the
original `jl; push 0x624` into a jump that skips creating the Single Player
and Other Multiplayer main-menu buttons. This tool changes only that entry's
seven data bytes back to the original code, so PD2 still applies (and
verifies) the rest of its list but leaves the menu intact.

usage: pd2_single_player.py [PROJECTD2_FOLDER] [--revert | --check]

The folder defaults to the current directory. Launch Game.exe directly
afterwards: PD2Launcher.exe restores its own ProjectDiablo.dll on start.
"""
import argparse
import hashlib
import os
from pathlib import Path
import struct
import sys
import tempfile

D2LAUNCH_SHA256 = '99cabc4751c95d035b5e77151b3605b809884fec2c10edf37d4c4e4e231e8479'
LAUNCH_DLL_INDEX = 18          # ProjectDiablo.dll's module table: D2Launch.dll
MENU_OFFSET = 0x17ec4
PD2_BYTES = bytes.fromhex('e9060100009090')       # jmp past both buttons; nop; nop
ORIGINAL_BYTES = bytes.fromhex('7c0a6824060000')  # jl 0x6fa57ed0; push 0x624
COUNT_FIELD = 0x408            # record: dll, offset, 256 dword-wide bytes, count


def record_pattern(data):
    return struct.pack('<2I', LAUNCH_DLL_INDEX, MENU_OFFSET) + struct.pack(f'<{len(data)}I', *data)


def find_record(image, data):
    pattern = record_pattern(data)
    hits = []
    start = image.find(pattern)
    while start != -1:
        if struct.unpack_from('<I', image, start + COUNT_FIELD)[0] == len(data):
            hits.append(start)
        start = image.find(pattern, start + 1)
    return hits


def write_atomically(path, data):
    # Replace rather than rewrite in place, so a running game keeps its mapped copy.
    handle, temporary = tempfile.mkstemp(prefix='.ProjectDiablo-', dir=path.parent)
    try:
        with os.fdopen(handle, 'wb') as stream:
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('folder', nargs='?', type=Path, default=Path.cwd(), help='the ProjectD2 folder')
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--revert', action='store_true', help='restore PD2\'s original menu patch')
    action.add_argument('--check', action='store_true', help='report the current state without changing anything')
    options = parser.parse_args()
    dll = options.folder / 'ProjectDiablo.dll'
    launch = options.folder / 'D2Launch.dll'
    if not dll.is_file() or not launch.is_file():
        raise SystemExit(f'No ProjectDiablo.dll and D2Launch.dll in {options.folder}')
    if hashlib.sha256(launch.read_bytes()).hexdigest() != D2LAUNCH_SHA256:
        raise SystemExit('Unrecognised D2Launch.dll; this tool only knows the PD2 1.13c build. Nothing changed.')
    image = bytearray(dll.read_bytes())
    locked, unlocked = find_record(image, PD2_BYTES), find_record(image, ORIGINAL_BYTES)
    if len(locked) + len(unlocked) != 1:
        raise SystemExit('PD2\'s menu patch entry was not found exactly once; this ProjectDiablo.dll '
                         'is not supported. Nothing changed.')
    state = 'unlocked' if unlocked else 'locked'
    if options.check:
        print(f'Single Player is {state} in {dll}'); return
    want = 'locked' if options.revert else 'unlocked'
    if state == want:
        print(f'Single Player is already {want}; nothing changed.'); return
    record = (locked or unlocked)[0]
    data = PD2_BYTES if options.revert else ORIGINAL_BYTES
    struct.pack_into(f'<{len(data)}I', image, record + 8, *data)
    backup = dll.with_name(dll.name + '.singleplayer-backup')
    if not options.revert and not backup.exists():
        backup.write_bytes(dll.read_bytes())
        print(f'Backup: {backup}')
    write_atomically(dll, bytes(image))
    print(f'Single Player {want} in {dll}.')
    if not options.revert:
        print('Start Game.exe directly (for example "Game.exe -3dfx"); PD2Launcher.exe would replace this file.')


if __name__ == '__main__':
    try:
        main()
    except OSError as error:
        print(f'Failed: {error}', file=sys.stderr); sys.exit(1)
