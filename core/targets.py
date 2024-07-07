from core.db import insert_targets
from termcolor import colored  # type: ignore
from typing import List
import core.logging as logging


def integrate_targets(filename: str, db_path: str) -> None:
    """Integrate targets from a file into the database."""
    domain_list: List[str] = []
    with open(filename, 'r') as file:
        domain_list = [line.strip() for line in file]
    
    insert_targets(domain_list, db_path)

def save_targets_to_file(domains: List[str], output_file: str) -> None:
    """Save domains to a file."""
    try:
        with open(output_file, 'w') as file:
            for domain in domains:
                file.write(domain + '\n')
        logging.print_info(f"Domains successfully saved to {output_file}")
    except IOError as e:
        logging.print_error(f"File I/O error: {e}")
