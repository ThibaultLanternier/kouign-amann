# Kouign-Amann Photo

A simple tool to deduplicate and manage your pictures

## Setup

First you must define in which backup folder your pictures will be stored 

```
cd crawler
python kouign-amann.py init /home/user/backup/MyPictures
```

## Backup pictures

This command will retrieve all .jpg files located in target directoy and will copy them back in your backup folder:
- If it finds duplicate pictures (even if they have been renamed) it will copy them only once
- Pictures are grouped by years and by "EVENT" an event is a continuous list of days with pictures

```
cd crawler
python kouign-amann.py backup /home/user/MyPictures
```
