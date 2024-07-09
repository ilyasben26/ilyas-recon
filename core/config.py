import os
config_dir = os.path.dirname(os.path.abspath(__file__))

# Edit these with your own tool locations
SUBLIST3R_PATH = "/Users/ilyas/Documents/GitHub/My-Recon-Methodology/Sublist3r/sublist3r.py"
SUBFINDER_PATH = "$HOME/go/bin/subfinder"
OAM_SUBS_PATH = "$HOME/go/bin/oam_subs"

# Edit or keep, you choose (just leave it)
RESOLVERS =  os.path.join(config_dir,"../inputs/resolvers.txt")

# DO NOT TOUCH

DB_PATH = os.path.join(config_dir, "../ilyas-recon.sqlite3")
BACKUP_DIR_PATH = os.path.join(config_dir, "../backup")
SUBLIST3R_TEMP = os.path.join(config_dir, "../temp/sublist3r_temp.txt")
AMASS_TEMP = os.path.join(config_dir, "../temp/amass_temp.txt")
SUBFINDER_TEMP = os.path.join(config_dir, "../temp/subfinder_temp.txt")
MASSDNS_INPUT_TEMP = os.path.join(config_dir, "../temp/massdns_input_temp.txt")
MASSDNS_OUTPUT_TEMP = os.path.join(config_dir, "../temp/massdns_output_temp.txt")
NUCLEI_LOGS = os.path.join(config_dir, "../logs/nuclei_logs.txt")


