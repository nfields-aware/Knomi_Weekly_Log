#!/bin/bash

# Set the source directory where your log files are stored
SOURCE_DIR="/opt/aware/document_workflow_services/logs/document_workflow/requests/"

# Set the destination directory where you want to save the log files
DEST_DIR="/home/ubuntu/logs/"

# Use find to locate and copy matching files
find "$SOURCE_DIR" -type f -name "*response*.json" -exec cp {} "$DEST_DIR" \; -exec echo "Copied {} to $DEST_DIR" \;

# Get the list of JSON files in the destination directory
JSON_FILES=("$DEST_DIR"/*.json)

# Loop through each JSON file and sort it into a weekly folder
for JSON_FILE in "${JSON_FILES[@]}"; do
    # Extract the date from the JSON filename (e.g., 2023-09-29_14.14.48.688)
    FILE_DATE=$(basename "$JSON_FILE" | grep -oP '\d{4}-\d{2}-\d{2}')
    
    # Extract the start and end dates for the week range
    WEEK_START=$(date -d "$FILE_DATE -$(date -d "$FILE_DATE" '+%u') days" "+%b_%d_%Y")
    WEEK_END=$(date -d "$FILE_DATE +$((7 - $(date -d "$FILE_DATE" '+%u'))) days" "+%b_%d_%Y")
    
    # Create the target directory for the week range (e.g., /home/ubuntu/logs/Sept_17_2023---Sept_23_2023)
    WEEK_DIR="$DEST_DIR/$WEEK_START---$WEEK_END"
    
    # Create the target directory if it doesn't exist
    mkdir -p "$WEEK_DIR"
    
    # Move the JSON file to the appropriate weekly folder
    mv "$JSON_FILE" "$WEEK_DIR/"
    
    # Optional: You can print a message for each file moved
    echo "Moved $JSON_FILE to $WEEK_DIR/"
done
