import os
import core.logging as logging

def get_directory_size(directory: str) -> int:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size

def convert_bytes(size: int, unit: str) -> float:
    if unit == 'KB':
        return size / 1024
    elif unit == 'MB':
        return size / (1024 * 1024)
    elif unit == 'GB':
        return size / (1024 * 1024 * 1024)
    else:
        return size

import os

def get_total_size(directory: str) -> None:
    # Get the directory of the current Python script
    script_directory = os.path.dirname(directory)
    total_size = get_directory_size(script_directory)

    if total_size > (1024 * 1024 * 1024):
        size = convert_bytes(total_size, 'GB')
        unit = 'GB'
    elif total_size > (1024 * 1024):
        size = convert_bytes(total_size, 'MB')
        unit = 'MB'
    elif total_size > 1024:
        size = convert_bytes(total_size, 'KB')
        unit = 'KB'
    else:
        size = total_size
        unit = 'bytes'

    logging.print_info(f'{size:.2f} {unit} project size')
