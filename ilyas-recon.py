import argparse
import os
import re
import sys
from typing import List
from termcolor import colored  # type: ignore

import core.config as config
import core.db as db
import core.enumerate as enum
import core.dns as dns
import core.nuclei as nuclei
import core.targets as targets
import core.stats as stats
import core.logging as logging

def is_valid_date(date_str: str) -> bool:
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    return re.match(pattern, date_str) is not None

def handle_enumerate(args: argparse.Namespace) -> None:
    count_targets_before = db.get_count_targets(config.DB_PATH)
    if not os.path.isfile(args.input_domains):
        logging.print_error(f"The file '{args.input_domains}' does not exist.")
        return

    domain_list: List[str] = []
    try:
        with open(args.input_domains, 'r') as file:
            domain_list = [line.strip() for line in file]
    except Exception as e:
        logging.print_error(f"An error occurred while reading the file: {e}")
        return

    db.insert_domains(domain_list, config.DB_PATH)

    for domain in domain_list:
        enum.enumerate_domain_sublist3r(domain)
        enum.enumerate_domain_subfinder(domain)
        enum.enumerate_domain_amass(domain)

    count_targets_after = db.get_count_targets(config.DB_PATH)
    new_targets_count = count_targets_after - count_targets_before
    logging.print_info(f"Added {new_targets_count} subdomains")
    logging.print_info(f"Current Total: {count_targets_after} subdomains")

def handle_backup() -> None:
    db.backup(config.DB_PATH, config.BACKUP_DIR_PATH)

def handle_verify(args: argparse.Namespace) -> None:
    total_targets = db.get_count_targets(config.DB_PATH)
    count_verified_before = db.get_count_verified(config.DB_PATH)
    if args.all:
        logging.print_info("Verifying all subdomains ...")
        dns.validate_all(config.DB_PATH)
    elif args.unverified:
        logging.print_info("Verifying only unverified domains ...")
        if args.input_date:
            if is_valid_date(args.input_date):
                logging.print_info(f"Verifying records created on: {args.input_date}")
                dns.validate_unverified_date(config.DB_PATH, args.input_date)
            else:
                logging.print_error(f"{args.input_date} is not a valid date, use YYYY-MM-DD format.")
                sys.exit(1)
        else:
            dns.validate_unverified(config.DB_PATH)

    count_verified_after = db.get_count_verified(config.DB_PATH)
    count_new_verified = count_verified_after - count_verified_before
    logging.print_info(f"Verified {count_new_verified} new subdomains")
    logging.print_info(f"Total Verified/Total: {count_verified_after}/{total_targets}")

def handle_import(args: argparse.Namespace) -> None:
    if args.nuclei_results:
        if not os.path.isfile(args.nuclei_results):
            logging.print_error(f"The file '{args.nuclei_results}' does not exist.")
            return
        nuclei.integrate_nuclei_results(args.nuclei_results, config.DB_PATH)
    elif args.input_target_domains:
        if not os.path.isfile(args.input_target_domains):
            logging.print_error(f"The file '{args.input_target_domains}' does not exist.")
            return
        count_targets_before = db.get_count_targets(config.DB_PATH)
        targets.integrate_targets(args.input_target_domains, config.DB_PATH)
        count_targets_after = db.get_count_targets(config.DB_PATH)
        new_targets_count = count_targets_after - count_targets_before
        logging.print_info(f"Added {new_targets_count} subdomains")
        logging.print_info(f"Current Total: {count_targets_after} subdomains")

def handle_export(args: argparse.Namespace) -> None:
    extracted_domains = db.get_domains_where(config.DB_PATH, args.where_clause)
    if not extracted_domains:
        logging.print_info(f"No domains matched the where clause criteria")
        return
    logging.print_info(f"Fetched {len(extracted_domains)} domains")
    targets.save_targets_to_file(extracted_domains, args.output_domains)

def handle_stats() -> None:
    stats.get_total_size(__file__)
    count_total = db.get_count_targets(config.DB_PATH)
    logging.print_info(f"{count_total} subdomains")
    count_verified = db.get_count_verified(config.DB_PATH)
    logging.print_info(f"{count_verified} verified subdomains")


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Ilyas Recon Tool")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Subparser for 'enumerate' command
    parser_enumerate = subparsers.add_parser('enumerate', help='Enumerate domains')
    parser_enumerate.add_argument('-l', '--input-file', type=str, required=True,
                                  dest='input_domains', help='Path to the input file containing domains')

    # Subparser for 'import' command
    parser_import = subparsers.add_parser('import', help="Import domains and other things")
    group_import = parser_import.add_mutually_exclusive_group(required=True)
    group_import.add_argument('--nuclei-results', type=str, dest='nuclei_results',
                              help='Path of the nuclei results txt file')
    group_import.add_argument('--targets', type=str, dest='input_target_domains',
                              help='Path of the input domains list txt file')

    # Subparser for 'export' command
    parser_export = subparsers.add_parser('export', help='Export domains and other things')
    parser_export.add_argument('--where', type=str, required=True, dest='where_clause',
                               help='The where statement part of the query to extract the domains')
    parser_export.add_argument('-o', '--output-file', type=str, required=True, dest='output_domains',
                               help='Path to the output file that will contain the domains')

    # Subparser for 'verify' command
    parser_verify = subparsers.add_parser('verify', help='Verify domains')
    group_verify = parser_verify.add_mutually_exclusive_group(required=True)
    group_verify.add_argument('--all', action='store_true', help='Verify all domains')
    group_verify.add_argument('--unverified', action='store_true', help='Verify only unverified domains')
    parser_verify.add_argument('--date', type=str, dest='input_date',
                               help='Verify only unverified domains at this date (YYYY-MM-DD)')

    # Subparser for 'backup' command
    parser_backup = subparsers.add_parser('backup', help='Backup the DB as csv and txt')

    # Subparser for 'stats' command
    parser_stats = subparsers.add_parser('stats', help="Get statistics about the storage space usage and more")

    return parser

def main() -> None:

    # print banner art:
    banner_art = """
    ______                       ____                         
   /  _/ /_  ______ ______      / __ \___  _________  ____     v1.0.0
   / // / / / / __ `/ ___/_____/ /_/ / _ \/ ___/ __ \/ __ \\    ||  ||        
 _/ // / /_/ / /_/ (__  )_____/ _, _/  __/ /__/ /_/ / / / /    \\\()// 
/___/_/\__, /\__,_/____/     /_/ |_|\___/\___/\____/_/ /_/    //(__)\\\\
      /____/                                                                                                                                                                                      
"""

    print(colored(banner_art, "white", attrs=["bold"]))

    db.db_init(config.DB_PATH)
    parser = create_parser()
    args = parser.parse_args()

    if args.command == 'verify':
        if not (args.all or args.unverified):
            logging.print_error("Please specify either '--all' or '--unverified'")
            parser.print_help()
            sys.exit(1)
        if args.input_date and not args.unverified:
            logging.print_error("--date can only be used with --unverified")
            parser.print_help()
            sys.exit(1)

    if args.command == 'enumerate':
        handle_enumerate(args)
    elif args.command == 'backup':
        handle_backup()
    elif args.command == 'verify':
        handle_verify(args)
    elif args.command == 'import':
        handle_import(args)
    elif args.command == 'export':
        handle_export(args)
    elif args.command == 'stats':
        handle_stats()

if __name__ == "__main__":
    main()
