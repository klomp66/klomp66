#######################################
# MoveStagedFiles
# Created 5/5/2022 JvS
# Moving files from a staging folder to a working folder for processing.
# This is used when inbound files can be coming in at any time (near real time) and if the processing takes awhile, and then the last step
# of the processing deletes the *.txt files (or whatever) in that folder, we could half-process a late-arrival file, and then delete it before
# we get the chance to process it properly.  To avoid this, we stage the files first, and then copy them to a processing folder before processing.
########################################

import shutil
import os

CUSTOM_FUNCTIONS_RULE = "_Custom_MDM_Functions"
runEditRuleWithName(CUSTOM_FUNCTIONS_RULE)

SOURCE_DIR = 'C:/Interfaces/Inbound/%s' % (ENVIRONMENT)  # This comes from the Constants file declared in the CUSTOM_FUNCTIONS_RULE - DEV, TEST, PROD - make sure it's there.
PROCESSING_FOLDERNAME = "Processing"
FILE_EXTENSION = ".xml"

# define function to move files
def _moveFiles(source_dir, processingFolderName, extensionToSearch, target_dir = ""):
    ### Function to move files of a specific filetype to another specified folder/directory.
    # If there isn't a target folder provided, then the target will be the processing directory under the Source directory
    if target_dir in [None, ""]:
        target_dir = '%s/%s' % (source_dir, processingFolderName)

    # Retrieve the list of filenames
    file_names = os.listdir(source_dir)

    # If any files are found, then for each file containing the sought-after extension, move it to the target folder
    if _listChecksOut(file_names, "List of files in %s" %(source_dir)):
        for file_name in file_names:
            if extensionToSearch in file_name:
                shutil.move(os.path.join(source_dir, file_name), target_dir)
    else:
        return False

    return True

success = _moveFiles(SOURCE_DIR, PROCESSING_FOLDERNAME, FILE_EXTENSION)
