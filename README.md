# Knomi_Weekly_Log
bash script

This script finds all response jsons within the directory, then sorts them by week. 

Places the log files in different directories. 

Here's the bash script with comments:

#!/bin/bash

# set the source
SOURCE_DIR="/opt/aware/document_workflow_services/logs/document_workflow/requests/"

# sets destination
DEST_DIR="/home/ubuntu/logs/"

# finds response JSONs
find "$SOURCE_DIR" -type f -name "*response*.json" -exec cp {} "$DEST_DIR" \; -exec echo "Copied {} to $DEST_DIR" \;

# takes the jsons and sorts them into a weekly folder
JSON_FILES=("$DEST_DIR"/*.json)
for JSON_FILE in "${JSON_FILES[@]}"; do

    # extracts date from file name
    FILE_DATE=$(basename "$JSON_FILE" | grep -oP '\d{4}-\d{2}-\d{2}')
    
    # create week start and end based on the file name
    WEEK_START=$(date -d "$FILE_DATE -$(date -d "$FILE_DATE" '+%u') days" "+%b_%d_%Y")
    WEEK_END=$(date -d "$FILE_DATE +$((7 - $(date -d "$FILE_DATE" '+%u'))) days" "+%b_%d_%Y")
    
    # creates a new directory by week (ex. Sept_17_2023---Sept_23_2023)
    WEEK_DIR="$DEST_DIR/$WEEK_START---$WEEK_END"
    mkdir -p "$WEEK_DIR"
    
    # moves json to new dir
    mv "$JSON_FILE" "$WEEK_DIR/"
    
    # debug messages for each file moved
    echo "Moved $JSON_FILE to $WEEK_DIR/"
done
