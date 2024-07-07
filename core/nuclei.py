from core.db import update_tags
import re
from typing import List, Tuple

def integrate_nuclei_results(nuclei_results_file: str, db_path: str) -> None:
    """Integrate nuclei scan results into the database."""
    parsed_results = parse_nuclei_results(nuclei_results_file)
    update_tags(parsed_results, db_path)

def parse_nuclei_results(filename: str) -> List[Tuple[str, str]]:
    """Parse nuclei scan results from a file and extract domains with tags."""
    result: List[Tuple[str, str]] = []
    domain_regex = r'\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b'
    tag_regex = r'\[.*?\]'
    
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            tags = ''.join(re.findall(tag_regex, line))
            match = re.search(domain_regex, line)
            if match:
                domain = match.group(0)
                result.append((domain, tags))
    
    return result
