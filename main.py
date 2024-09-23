import shutil
from pathlib import Path
from logger_configurator import configure_logging
import logging
import yaml

# Dry run flag: Set to True for a dry run (no actual file operations)
dry_run = False

# Load directory configuration file
with open("directory_config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Load the mappings file. Mappings help to classify the test type according to substrings in the filenames
with open("mappings.yaml", "r") as file:
    mappings_data = yaml.safe_load(file)

#######################################################################################################################
# Load file or files and logging
# Access directories and other configurations
base_directory = config['directories']['base_directory']
SOURCE_DIR = Path(config['directories']['source_dir'])
DESTINATION_BASE_DIR = Path(config['directories']['destination_base_dir'])

# Ensure the destination base directory exists
DESTINATION_BASE_DIR.mkdir(parents=True, exist_ok=True)

# Log files loaded from YAML configuration
UNCLASSIFIED_LOG = DESTINATION_BASE_DIR / config['logs']['unclassified_log']
COPIED_LOG = DESTINATION_BASE_DIR / config['logs']['copied_log']
REPLACED_LOG = DESTINATION_BASE_DIR / config['logs']['replaced_log']
SKIPPED_LOG = DESTINATION_BASE_DIR / config['logs']['skipped_log']

# Load logger configuration
configure_logging(base_directory)
# Log the start of the program
logging.debug("MAIN. MPR file classifier started")

# Access the mappings
mappings = mappings_data['mappings']

# Define the file extension to filter ('.mpr')
FILE_EXTENSION = ".mpr"

# File counters
total_files_found = 0
files_copied = 0
files_unclassified = 0
files_replaced = 0
files_skipped = 0
files_with_error = 0

# Open the log files in append mode to preserve logs between runs
with open(UNCLASSIFIED_LOG, 'a') as log_unclassified, \
        open(COPIED_LOG, 'a') as log_copied, \
        open(REPLACED_LOG, 'a') as log_replaced, \
        open(SKIPPED_LOG, 'a') as log_skipped:
    # Iterate over all files in the source directory and subdirectories with the specified extension
    for file_path in SOURCE_DIR.rglob(f"*{FILE_EXTENSION}"):
        filename = file_path.name
        matched = False

        # Iterate through the mappings to find a match
        for mapping in mappings:
            if mapping['substring1'] in filename and mapping['substring2'] in filename:
                test_type = mapping['test_type']
                destination_dir = DESTINATION_BASE_DIR / test_type
                destination_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

                # Define the destination file path
                destination_file = destination_dir / filename

                try:
                    # If the file has been already classified and copied, compare sizes to check if the file has been
                    # updated. This comparison is necessary for tests that take several days.
                    if destination_file.exists():
                        source_size = file_path.stat().st_size
                        dest_size = destination_file.stat().st_size

                        # If the file is larger, copy the file.
                        if source_size > dest_size:
                            if not dry_run:
                                shutil.copy2(file_path, destination_file)
                                log_replaced.write(f"{file_path} → {destination_file}\n")
                            logging.info(f"Replaced: {file_path} → {destination_file} (dry run={dry_run})")
                            files_replaced += 1
                        else:
                            # Sizes are the same or destination is larger; skip copying
                            log_skipped.write(
                                f"{file_path} (size: {source_size}) → {destination_file} (size: {dest_size})\n")
                            logging.info(f"Skipped (no update needed): {file_path} (dry run={dry_run})")
                            files_skipped += 1
                    else:
                        # If the file has not been copied, copy the file.
                        if not dry_run:
                            shutil.copy2(file_path, destination_file)
                            log_copied.write(f"{file_path} → {destination_file}\n")
                        logging.info(f"Copied: {file_path} → {destination_file} (dry run={dry_run})")
                        files_copied += 1

                except Exception as e:
                    logging.error(f"Failed to copy {file_path} to {destination_file}: {e}")
                    files_with_error += 1

                matched = True
                break  # Stop checking other mappings once a match is found to avoid multiple classifications.

        if not matched:
            # Log the unclassified file
            log_unclassified.write(f"{file_path}\n")
            logging.warning(f"Unclassified: {file_path} (dry run={dry_run})")
            files_unclassified += 1
        total_files_found += 1


# Logging information.
logging.info("File classification and copying completed (dry run=%s).", dry_run)
logging.info("File classification and copying completed.")
logging.info(f"Unclassified files are logged in: {UNCLASSIFIED_LOG}")
logging.info(f"Copied files are logged in: {COPIED_LOG}")
logging.info(f"Replaced files are logged in: {REPLACED_LOG}")
logging.info(f"Skipped files are logged in: {SKIPPED_LOG}")
logging.info(f"File processing summary: {total_files_found} total files found, "
             f"{files_copied} files copied, {files_unclassified} files unclassified, "
             f"{files_replaced} files replaced, {files_skipped} files skipped,"
             f"{files_with_error} files with error")