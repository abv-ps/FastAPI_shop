#!/bin/bash

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")
BACKUP_DIR="/data/backup/$TIMESTAMP"
mkdir -p "$BACKUP_DIR"

mongodump --host mongo --port 27017 --out "$BACKUP_DIR"

MAX_BACKUPS=24
BACKUP_BASE="/data/backup"

cd "$BACKUP_BASE" || exit

ls -1dt */ | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm -rf
