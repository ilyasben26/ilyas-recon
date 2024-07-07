from core.db import get_all_targets, update_dns_records, get_unverified_targets, get_unverified_date_targets
from core.enumerate import run_command
import core.config as config
import ipaddress
import os
import random
from typing import List, Dict, Any


def validate(subdomain_list: List[str]) -> None:
    """Validate subdomains using massdns and update the database with DNS records."""
    random.shuffle(subdomain_list)

    with open(config.MASSDNS_INPUT_TEMP, 'w') as file:
        for domain in subdomain_list:
            file.write(f"{domain}\n")

    print("Running massdns on targets ...")
    run_command(f"massdns -r {config.RESOLVERS} -o S -w {config.MASSDNS_OUTPUT_TEMP} {config.MASSDNS_INPUT_TEMP}")

    domain_records = read_domain_records(config.MASSDNS_OUTPUT_TEMP)
    with open(config.MASSDNS_OUTPUT_TEMP, 'w') as file:
        pass
    with open(config.MASSDNS_INPUT_TEMP, 'w') as file:
        pass

    if domain_records:
        domain_dict = parse_domain_records(domain_records)
        print("Updating resolved domains ...")
        update_dns_records(domain_dict, config.DB_PATH)


def validate_all(db_path: str) -> None:
    """Validate all subdomains in the database."""
    subdomain_list = get_all_targets(db_path)
    print(f"Total targets to process: {len(subdomain_list)}")
    if subdomain_list:
        validate(subdomain_list)


def validate_unverified(db_path: str) -> None:
    """Validate all unverified subdomains in the database."""
    subdomain_list = get_unverified_targets(db_path)
    print(f"Total targets to process: {len(subdomain_list)}")
    if subdomain_list:
        validate(subdomain_list)


def validate_unverified_date(db_path: str, date: str) -> None:
    """Validate all unverified subdomains in the database created on a specific date."""
    subdomain_list = get_unverified_date_targets(db_path, date)
    print(f"Total targets to process: {len(subdomain_list)}")
    if subdomain_list:
        validate(subdomain_list)


def read_domain_records(file_path: str) -> List[str]:
    """Read domain records from a file."""
    if os.stat(file_path).st_size == 0:
        print("The massdns results file is empty. No records to process.")
        return []

    with open(file_path, 'r') as file:
        domain_records = file.readlines()
    return [record.strip() for record in domain_records]


def is_internal_ip(ip: str) -> bool:
    """Check if an IP address is internal (private)."""
    try:
        ip_obj = ipaddress.ip_address(ip)
        return ip_obj.is_private
    except ValueError:
        return False


def parse_domain_records(domain_records: List[str]) -> Dict[str, List[str]]:
    """Parse domain records into a dictionary."""
    domain_dict: Dict[str, List[str]] = {}
    for record in domain_records:
        parts = record.split()
        domain = parts[0].rstrip('.')
        record_type = parts[1]
        record_value = parts[2]

        if record_type in ('A', 'AAAA') and is_internal_ip(record_value):
            continue

        if domain not in domain_dict:
            domain_dict[domain] = []

        domain_dict[domain].append(f"{record_type} {record_value}")
    return domain_dict
