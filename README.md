**CML Biologic file classifier**  
## Description
This classifier is a file crawler that copies Biologic files (*.mpr extension) from the the CML folder (source dir) in the Biologic cycler, classifies them according to test type, and copies them to a new folder (destination_base_dir) according to the classification.  
The classification is made according to parts of the filename as detailed in the 'mappings.yaml' file.  
The directories need to be specified in the file 'directory_config_template.yaml' as follows:  
* base_directory : Directory where the python scripts are located.    
* source_dir: Directory where the Biologic files are located.  
* destination_base_dir: Directory where the classified files will be copied to.

## Installation  
1. Clone the repo
2. Specify the directories in the file 'directory_config_template.yaml'
3. Run the main file
