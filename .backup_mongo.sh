#!/bin/bash

set -e

SPACE_NAME=roastery
FOLDER_NAME=backup_$(date +%y%m%d_%H%M%S)
BACKUP_NAME=dump_$(date +%y%m%d_%H%M%S).tar.gz
MEDIA_BACKUP_NAME=media_$(date +%y%m%d_%H%M%S).tar.gz
DB=core_db

date
echo "Backing up MongoDB database to DigitalOcean Space: $SPACE_NAME"


echo "Dumping MongoDB $DB database to compressed archive"
docker exec -it $DB_CONTAINER_ID bash -c "mongodump --db core_db -u $DB_USERNAME --password $DB_PW"


echo "Copying compressed archive to DigitalOcean Space: $SPACE_NAME"
#zip -r $HOME/backup/tmp_dump.zip ./dump/tmp_dump
tar -zcvf $HOME/backup/tmp_dump.tar.gz ./dump
tar -zcvf $HOME/backup/media.tar.gz ./psg_mvp_backend/media

s3cmd put $HOME/backup/tmp_dump.tar.gz s3://$SPACE_NAME/$FOLDER_NAME/$BACKUP_NAME
s3cmd put $HOME/backup/media.tar.gz s3://$SPACE_NAME/$FOLDER_NAME/$MEDIA_BACKUP_NAME


echo "Cleaning up compressed archive"
rm -rf $HOME/backup/tmp_dump.tar.gz
rm -f $HOME/backup/media.tar.gz


echo 'Backup complete!'
