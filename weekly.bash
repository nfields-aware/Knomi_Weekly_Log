#!/bin/bash

SOURCE_DIR="/opt/aware/document_workflow_services/logs/document_workflow/requests/"
DEST_DIR="/home/ubuntu/logs/"

find "$SOURCE_DIR" -type f -name "*response*.json" -exec cp {} "$DEST_DIR" \; -exec echo "Copied {} to $DEST_DIR" \;

JSON_FILES=("$DEST_DIR"/*.json)

for JSON_FILE in "${JSON_FILES[@]}"; do
    FILE_DATE=$(basename "$JSON_FILE" | grep -oP '\d{4}-\d{2}-\d{2}')
    WEEK_START=$(date -d "$FILE_DATE -$(date -d "$FILE_DATE" '+%u') days" "+%b_%d_%Y")
    WEEK_END=$(date -d "$FILE_DATE +$((7 - $(date -d "$FILE_DATE" '+%u'))) days" "+%b_%d_%Y")
    WEEK_DIR="$DEST_DIR/$WEEK_START---$WEEK_END"
    mkdir -p "$WEEK_DIR"
    mv "$JSON_FILE" "$WEEK_DIR/"
    echo "Moved $JSON_FILE to $WEEK_DIR/"
done

