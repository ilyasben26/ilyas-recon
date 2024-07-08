from core.db import insert_targets
from termcolor import colored  # type: ignore
from typing import List
import core.logging as logging
import re


def integrate_targets(filename: str, db_path: str) -> None:
    """Integrate targets from a file into the database."""
    domain_list: List[str] = extract_subdomains(filename)
    insert_targets(domain_list, db_path)

def extract_subdomains(filename: str) -> List[str]:
    """Extract subdomains from URLs in a file using regex."""
    subdomain_list: List[str] = []
    domain_regex = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            # Find all matches of domain_regex in the line
            matches = re.findall(domain_regex, line)
            for match in matches:
                subdomain_list.append(match)

    return subdomain_list


def save_targets_to_file(domains: List[str], output_file: str) -> None:
    """Save domains to a file."""
    try:
        with open(output_file, 'w') as file:
            for domain in domains:
                file.write(domain + '\n')
        logging.print_info(f"Domains successfully saved to {output_file}")
    except IOError as e:
        logging.print_error(f"File I/O error: {e}")
