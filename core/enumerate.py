import subprocess
from core.db import insert_targets
import core.config as config
from termcolor import colored  # type: ignore
from typing import Optional


def run_command(command: str, timeout: Optional[int] = None) -> Optional[str]:
    """Run a shell command with an optional timeout and return the output."""
    try:
        result = subprocess.run(command, shell=True, timeout=timeout, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"Command '{command}' timed out after {timeout} seconds.")
    except subprocess.CalledProcessError as e:
        print(f"Command '{command}' failed with error:\n{e.stderr}")
    return None


def enumerate_domain_sublist3r(domain: str) -> None:
    """Enumerate subdomains using Sublist3r and insert them into the database."""
    print(f"Enumerating domain using Sublist3r: {domain}")
    run_command(f"python3 {config.SUBLIST3R_PATH} -d {domain} -o {config.SUBLIST3R_TEMP}")

    with open(config.SUBLIST3R_TEMP, 'r') as file:
        subdomains = file.read().splitlines()
    
    if subdomains:
        insert_targets(subdomains, config.DB_PATH)
        with open(config.SUBLIST3R_TEMP, 'w') as file:
            pass
    else:
        print(colored("-- No subdomains found using Sublist3r --", "red"))


def enumerate_domain_subfinder(domain: str) -> None:
    """Enumerate subdomains using Subfinder and insert them into the database."""
    print(f"Enumerating domain using subfinder: {domain}")
    run_command(f"{config.SUBFINDER_PATH} -d {domain} -o {config.SUBFINDER_TEMP}")

    with open(config.SUBFINDER_TEMP, 'r') as file:
        subdomains = file.read().splitlines()
    
    if subdomains:
        insert_targets(subdomains, config.DB_PATH)
        with open(config.SUBFINDER_TEMP, 'w') as file:
            pass
    else:
        print(colored("-- No subdomains found using subfinder --", "red"))


def enumerate_domain_amass(domain: str) -> None:
    """Enumerate subdomains using Amass and insert them into the database."""
    print(f"Enumerating domain using amass: {domain}")
    run_command(f"timeout 5m amass enum -d {domain} -dns-qps 20")
    run_command(f"{config.OAM_SUBS_PATH} -names -d {domain} -o {config.AMASS_TEMP}")

    with open(config.AMASS_TEMP, 'r') as file:
        subdomains = file.read().splitlines()
    
    if subdomains:
        insert_targets(subdomains, config.DB_PATH)
        with open(config.AMASS_TEMP, 'w') as file:
            pass
    else:
        print(colored("-- No subdomains found using amass --", "red"))
