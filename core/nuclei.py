from core.db import update_tags
import core.config as config
import re
from typing import List, Tuple
import os

def integrate_nuclei_results(nuclei_results_file: str, db_path: str) -> None:
    """Integrate nuclei scan results into the database."""
    ##TODO: save it into the log file
    append_to_nuclei_logs(nuclei_results_file, config.NUCLEI_LOGS)
    # Saving it into the database
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

def append_to_nuclei_logs(nuclei_results_file: str, log_file: str) -> None:
    """Append raw nuclei scan results to the nuclei logs, avoiding duplicates."""
    existing_lines = set()
    
    # Read existing entries to avoid duplicates
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            for line in f:
                existing_lines.add(line.strip())
    
    # Append new entries that are not duplicates
    with open(log_file, 'a') as f:
        with open(nuclei_results_file, 'r') as results:
            for line in results:
                if line.strip() not in existing_lines:
                    f.write(f"{line}")
                    existing_lines.add(line.strip())  # Update set to avoid duplicates in memory