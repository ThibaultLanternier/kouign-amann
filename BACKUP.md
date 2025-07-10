# Using `rsync` for backup

In order to keep data safe you should maintain a copy of your backup folder on a second drive

## Install `rsync`

On Ubuntu / Debian if not already present you can install it using `apt` package

```
$ sudo apt update
$ sudo apt install rsync
```

## Synchronize data

### No deletion Mode 
it will not delete new file that might have been deleted (or renamed) on the `SOURCE` in the `DESTINATION` folder it is safer but might consume more disk-space

```
$ rsync -a --progress --stats /home/Photos/ /other-disk/Photos/
```

Note : the trailing slash at the end of `/home/Photos/` is important it tells to synchronize the content of the `/Photos` directory

### With deletion mode
it will delete file in the DESTINATION folder so that SOURCE and DESTINATION are exactly the same

```
$ rsync -a --delete --progress --stats /home/Photos/ /other-disk/Photos/
```

Note : you can add the `--dry-run` option before launching the command in order to avoid any mistakes

```
$ rsync -a --dry-run --delete --progress --stats /home/Photos/ /other-disk/Photos/
```

In order to prevent your system to over-heat and crash it might be a good idea to add the `--bwlimit` option

ex.

```
$ rsync -a --dry-run --progress --stats --bwlimit=3000 /home/Photos/ /other-disk/Photos/
```

will limit transfer rate to ~ 3 MB / s