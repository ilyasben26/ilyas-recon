import sqlite3
from datetime import datetime
import csv
from termcolor import colored  # type: ignore
import os
from typing import List, Dict, Tuple, Any
import core.logging as logging


def db_init(db_path: str) -> None:
    """Initialize the database by creating necessary tables."""
    if not os.path.exists(db_path):
        print(colored(f"Database file {db_path} does not exist. Creating it...", "blue"))
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domains (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL UNIQUE,
                last_scanned DATETIME,
                created_at DATETIME NOT NULL
            )
        ''')
        conn.commit()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL UNIQUE,
                tags TEXT,
                validated BOOL,
                last_scanned DATETIME,
                created_at DATETIME NOT NULL,
                records TEXT
            )
        ''')
        conn.commit()

    except sqlite3.Error as e:
        logging.print_error(f"An error occurred with the SQLite database: {e}")
    finally:
        if conn:
            conn.close()


def insert_domains(domain_list: List[str], db_path: str) -> None:
    """Insert a list of domains into the 'domains' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for domain in domain_list:
            try:
                cursor.execute('''
                    INSERT INTO domains (domain, created_at)
                    VALUES (?, ?)
                ''', (domain, now))
                print(colored(f"[+] seed domain: {domain}", "green"))
            except sqlite3.IntegrityError:
                print(colored(f"[-] seed domain: {domain}", "yellow"))

        conn.commit()

    except sqlite3.Error as e:
        logging.print_error(f"An error occurred with the SQLite database: {e}")
    finally:
        if conn:
            conn.close()


def insert_targets(target_list: List[str], db_path: str) -> None:
    """Insert a list of targets into the 'targets' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for domain in target_list:
            try:
                cursor.execute('''
                    INSERT INTO targets (domain, created_at)
                    VALUES (?, ?)
                ''', (domain, now))
                print(colored(f"[+] {domain}", "green"))
            except sqlite3.IntegrityError:
                print(colored(f"[-] {domain}", "yellow"))

        conn.commit()
    except sqlite3.Error as e:
        logging.print_error(f"An error occurred with the SQLite database: {e}")
    finally:
        if conn:
            conn.close()


def backup(db_path: str, backup_dir: str) -> None:
    """Backup the database by exporting 'targets' table to CSV and text files."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM targets")
        rows = cursor.fetchall()

        headers = [description[0] for description in cursor.description]

        cursor.execute("SELECT domain FROM targets")
        domains = cursor.fetchall()

        csv_file_path = os.path.join(backup_dir, 'targets.csv')
        with open(csv_file_path, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
            csvwriter.writerow(headers)
            csvwriter.writerows(rows)

        txt_file_path = os.path.join(backup_dir, 'target_subdomains.txt')
        with open(txt_file_path, 'w') as txtfile:
            for domain in domains:
                txtfile.write(f"{domain[0]}\n")

        print(f"DB was successfully backed-up in {backup_dir}")

    except sqlite3.Error as e:
        logging.print_error(f"SQLite error: {e}")
    except Exception as e:
        logging.print_error(f"{e}")
    finally:
        if conn:
            conn.close()


def get_count_targets(db_path: str) -> int:
    """Return the count of targets in the 'targets' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(domain) FROM targets")
        count = cursor.fetchone()[0]
    except sqlite3.Error as e:
        logging.print_error(f"SQLite error: {e}")
        count = 0
    except Exception as e:
        logging.print_error(f"An error occurred when fetching count of targets: {e}")
        count = 0
    finally:
        if conn:
            conn.close()
    return count


def get_all_targets(db_path: str) -> List[str]:
    """Return a list of all targets from the 'targets' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT domain FROM targets")
        domains = cursor.fetchall()
        domains = [domain[0] for domain in domains]
    except sqlite3.Error as e:
        logging.print_error(f"SQLite error: {e}")
        domains = []
    except Exception as e:
        logging.print_error(f"An error occurred when fetching all targets: {e}")
        domains = []
    finally:
        if conn:
            conn.close()
    return domains


def get_unverified_targets(db_path: str) -> List[str]:
    """Return a list of unverified targets from the 'targets' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT domain
            FROM targets
            WHERE validated != 1 OR validated IS NULL 
        ''')
        domains = cursor.fetchall()
        domains = [domain[0] for domain in domains]
    except sqlite3.Error as e:
        logging.print_error(f"SQLite error: {e}")
        domains = []
    except Exception as e:
        logging.print_error(f"An error occurred when fetching unverified targets: {e}")
        domains = []
    finally:
        if conn:
            conn.close()
    return domains


def get_unverified_date_targets(db_path: str, date: str) -> List[str]:
    """Return a list of unverified targets created on a specific date."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT domain
            FROM targets
            WHERE (validated != 1 OR validated IS NULL)
            AND DATE(created_at) = ?
        ''', (date,))
        domains = cursor.fetchall()
        domains = [domain[0] for domain in domains]
    except sqlite3.Error as e:
        logging.print_error(f"SQLite error: {e}")
        domains = []
    except Exception as e:
        logging.print_error(f"An error occurred when fetching unverified targets by date: {e}")
        domains = []
    finally:
        if conn:
            conn.close()
    return domains


def get_count_verified(db_path: str) -> int:
    """Return the count of verified targets in the 'targets' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(domain) FROM targets WHERE validated == 1")
        count = cursor.fetchone()[0]
    except sqlite3.Error as e:
        logging.print_error(f"SQLite error: {e}")
        count = 0
    except Exception as e:
        logging.print_error(f"An error occurred when fetching count of verified targets: {e}")
        count = 0
    finally:
        if conn:
            conn.close()
    return count



def update_dns_records(domain_dict: Dict[str, List[str]], db_path: str) -> None:
    """Update the DNS records for domains in the 'targets' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for domain, records in domain_dict.items():
            records_str = ', '.join(records)
            cursor.execute('SELECT id FROM targets WHERE domain = ?', (domain,))
            row = cursor.fetchone()

            if row:
                cursor.execute('''
                    UPDATE targets
                    SET records = ?, validated = ?
                    WHERE domain = ?
                ''', (records_str, True, domain))
                print(colored(f"[+] {domain}: {records_str}", "green"))

        conn.commit()
    except sqlite3.Error as e:
        logging.print_error(f"An error occurred with the SQLite database: {e}")
    finally:
        if conn:
            conn.close()


def update_tags(domain_tags_tuple: List[Tuple[str, str]], db_path: str) -> None:
    """Update the nuclei tags for domains in the 'targets' table."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        for domain, tag in domain_tags_tuple:
            cursor.execute('SELECT tags FROM targets WHERE domain = ?', (domain,))
            result = cursor.fetchone()

            if result:
                existing_tags = result[0]
                if existing_tags:
                    existing_tags_list = existing_tags.split(', ')
                    if tag not in existing_tags_list:
                        new_tags = f"{existing_tags}, {tag}"
                        cursor.execute('UPDATE targets SET tags = ?, last_scanned = ? WHERE domain = ?', 
                                       (new_tags, datetime.now(), domain))
                        print(colored(f"[+]{new_tags}: {domain}", "yellow"))
                else:
                    cursor.execute('UPDATE targets SET tags = ?, last_scanned = ? WHERE domain = ?', 
                                   (tag, datetime.now(), domain))
                    print(colored(f"[+]{tag}: {domain}", "green"))
            else:
                cursor.execute('INSERT INTO targets (domain, tags, last_scanned, created_at) VALUES (?, ?, ?, ?)', 
                               (domain, tag, datetime.now(), datetime.now()))
                print(colored(f"[+]{tag}: [+]{domain} ", "green"))

        conn.commit()
    except sqlite3.Error as e:
        logging.print_error(f"An error occurred with the SQLite database: {e}")
    finally:
        if conn:
            conn.close()


def get_domains_where(db_path: str, where_clause: str) -> List[str]:
    """Return a list of domains from the 'targets' table matching the where clause."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        query = f"SELECT domain FROM targets WHERE {where_clause}"
        cursor.execute(query)
        rows = cursor.fetchall()
        domains = [row[0] for row in rows]

    except sqlite3.Error as e:
        logging.print_error(f"An error occurred with the SQLite database: {e}")
        domains = []
    except Exception as e:
        logging.print_error(f"An error occurred when fetching domains: {e}")
        domains = []
    finally:
        if conn:
            conn.close()

    return domains
