# ilyas-recon
## Overview
ilyas-recon is a comprehensive reconnaissance tool designed for subdomain enumeration, DNS validation, import/export, and backup operations.
Furthermore, your recon data is stored in a SQLite3 database, giving you the power to use SQL to query it later on.
It uses many other popular tools behind the scenes, such as:
- Amass
- MassDNS
- Subfinder
- Sublist3r
- Nuclei (not directly)

## Why I made this tool and why you should use it?
I created ilyas-recon to assist me during my bug bounty engagements. Initially, my reconnaissance data was disorganized and spread across multiple files and formats, making it difficult to manage and analyze effectively. I wanted a solution that could consolidate all my recon data into a structured format using an SQL database. I can now see all my discovered subdomains in one place, as well as see the results of the Nuclei scans associated with each subdomain and even the associated DNS records, making techniques like CVE-Hunting way easier. 

## Features
- **Subdomain Enumeration**: Uses multiple tools to discover subdomains.
- **Verification**: Validates the discovered subdomains.
- **Import**: Handles the import of new subdomains and nuclei scan results
- **Export**: Handles the export of stored subdomains for subsequent scanning
- **Backup**: Backs up the database.
- **Statistics**: Provides storage space usage and subdomains statistics.

## Installation
1. Clone the repo:
```bash
git clone https://github.com/ilyasben26/ilyas-recon.git
cd ilyas-recon
```
2. (Optional but recommended) Create a virtual environment and activate it
```bash
python -m venv ./myvenv
source ./myvenv/bin/activate
```
3. Install the python requirements
```bash
pip install -r requirements.txt
```
4. Make sure to have the following tools already installed (if you want to use the subdomain enumeration feature):
    - amass v4.2.0 (https://github.com/owasp-amass/amass)
    - oam-tools (https://github.com/owasp-amass/oam-tools)
    - Sublist3r (https://github.com/aboul3la/Sublist3r)
    - Subfinder v2.6.6 (https://github.com/projectdiscovery/subfinder)
5. Install massdns if you want to use the subdomain validation feature (https://github.com/blechschmidt/massdns)
6. Go to `core/config.py` and edit it to point to where your tools are located:
```python
# Edit these with your own tool locations
SUBLIST3R_PATH = "sublit3r.py path"
SUBFINDER_PATH = "subfinder go executable path"
OAM_SUBS_PATH = "oam_subs go executable path" # installed with oam-tools
```
The other tools, amass and massdns should be installed globally.

## Practical Getting Started
Let's say you already have a list of subdomains you already discovered, you can import them using:
```bash
python ilyas-recon.py import --targets <subdomain_list.txt>
```
It doesn't matter what your input looks like, as long as it contains subdomains, these will be detected and inserted into a Sqlite3 DB called ilyas-recon.sqlite3.
<br>
<br>
Great! Now you have some subdomains in your DB.
Next step is to verify these subdomains using:
```bash
python ilyas-recon.py verify --unverified
```
This will take all your newly inserted subdomain, validate them using massdns and then store the found DNS records in the DB and mark the subdomain as validated.
One trick that I came up with to verify as many of these records as possible is to use a bash script that I run over night to run the previous command 50 times or more, see `workflows/mass_verify.sh`.
You can also specify your own list of DNS resolvers in `inputs/resolvers.txt`. Also each time you run this verify command the order of the subdomains is randomized to guarantee that more subdomains get verified.
<br>
<br>
Now that you verified your subdomains, you want to run nuclei scans on them to perhaps detect what technology is being used by each subdomain. You can extract the validated subdomains using:
```bash
python3 ilyas-recon.py export --where "validated=1" -o ./outputs/extracted_subdomains.txt
```
You can now use those extracted subdomains to run a nuclei scan on them.
After running the nuclei scans, you are left with the ouput file generated by nuclei. You can now integrate these results to your DB using:
```bash
python ilyas-recon.py import --nuclei-results <nuclei_output_file>
```
You now have a DB full of insights, to query it further, you can use your favorite SQL browser, I recommend https://sqlitebrowser.org .
<br>
<br>
This is what the the DB table schema looks like:

*Table*: **targets**
| Column          | Type                | Description                                                                                   |
|-----------------|---------------------|-----------------------------------------------------------------------------------------------|
| id              | INTEGER PRIMARY KEY AUTOINCREMENT | Primary key for the table, auto-incremented.                                                  |
| domain          | TEXT NOT NULL UNIQUE | The domain name of the target.      |
| tags            | TEXT                | Nuclei tags associated with the target.                                               |
| validated       | BOOL                | Boolean flag indicating whether the target has been validated.                                |
| last_scanned    | DATETIME            | Timestamp indicating when the target was last scanned.                                         |
| created_at      | DATETIME NOT NULL   | Timestamp indicating when the record was created.                   |
| records         | TEXT                | DNS records associated with the target.                       |






## Usage

### Command-line Arguments

The tool uses various subcommands to handle different tasks. Below is a breakdown of the available subcommands and their arguments:

### Enumerate

Enumerate subdomains 

```bash
python ilyas_recon.py enumerate -l <input_file>
```
- `-l`, `--input-file`: Path to the input file containing root domains.

### Import
```bash
python ilyas_recon.py import --nuclei-results <results_file>
python ilyas_recon.py import --targets <input_file>
```
- `--nuclei-results`: Path to the output file generated by a default Nuclei scan. 
- `--targets`: Path to the subdomains you want to import into the database (your subdomains from previous recons)

### Export
Export subdomains based on a specific condition

```bash
python ilyas_recon.py export --where <sql_where_clause> -o <output_file>
```
- `--where`: The where statement part of the sql query to extract the domains.
- `-o`, `--output-file`: Path to the output file that will contain the extracted subdomains.

### Verify
Verify subdomains, either all or only unverified ones
```bash
python ilyas_recon.py verify --all
python ilyas_recon.py verify --unverified [--date <YYYY-MM-DD>]
```
- `--all`: Verify all domains.
- `--unverified`: Verify only unverified domains.
- `--date`: Verify only unverified domains created on this date (YYYY-MM-DD). Can only be used with `--unverified`.

### Backup
Backup the database as CSV and TXT.
```bash
python ilyas_recon.py backup
```

### Get Statistics
```bash
python ilyas_recon.py stats
```