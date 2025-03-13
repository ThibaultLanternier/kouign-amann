# Kouign-Amann

## What is it ?

This is basic tool written in Python to help manage and backup photos from your digital camera.

If like me you struggle to manage the pictures you take I hope this tool will help. 

It usually starts like this : you suddenly realize that your SD card on the camera is full, you need to delete some photos. Some pictures are pretty old and you think that you have already copied them somewhere but you are not completely sure. You're in a hurry so just to be safe you dump the whole card to your computer and put it somewhere in a folder called `BACKUP_2024_11`, thinking that you'll deal with it later.
Couple of month later your pictures are spread between dozens of folders with cryptic names... Your hard drive is full and you have no idea where to find the pictures from your last vacations.

Sounds familiar ?

### Backup and organize your pictures

The idea is you define a unique backup folder on your hard drive. Let's call it `/Photos`. Then you launch the `backup` command with the target path you want to backup ex. `/media/my-camera-sd-card/DCIM`. The application will then crawl your sd card to find `.jpeg` files and will give them a unique id and store them in your `/Photos` folder.

To make it easier to manage pictures will be grouped in sub-folders ex. `/Photos/2024/2024-12-01 <EVENT_DESCRIPTION>`.If the program detects a continuous time period where pictures have been taken it will assume its a single event. Let's say you went on 4 days trip during which you took pictures every day they will be grouped in a single folder.
Once backup has completed you can rename each sub folder to make it easy to find your pictures ex. rename `/Photos/2024/2024-12-01 <EVENT_DESCRIPTION>` to `/Photos/2024/2024-12-01 Family trip to Saint Malo`

Next time you launch `backup` it will only copy photos that have not yet been copied and put them in the relevant event folder.

Unique Ids are generated using a `Perception Hash` meaning that even if a picture has been renamed or resized it will have the same unique Id and therefore will not be duplicated

> Note: if you want more details on perception hashing you can find more details on the [ImageHash library Github](https://github.com/JohannesBuchner/imagehash)


## Installation

### Linux (Debian)

First download `kouign-amann.deb` from the latest release

and install it

```
$ dkpg -i kouign-amann.deb
```

then check it works

```
$ kouign-amann
$ Usage: kouign-amann [OPTIONS] COMMAND [ARGS]...

...
```

### MacOS

> Warning: currently a bit hacky

In order to work you need to have [Brew](https://brew.sh/) installed on your system, because the `.pkg` available in the release will put the binary in `/opt/homebrew/bin`. It seems that MacOs Sequoia is not allowing to deploy binaries in `/usr/local/bin`

If homebrew it should be in your path and it should work

Download `kouign-amann.pkg` from the latest release

Launch the installer

then check it works

```
$ kouign-amann
$ Usage: kouign-amann [OPTIONS] COMMAND [ARGS]...

...
```

### Windows

> Packaging not done yet : you will need to run it directly with a Python interpreter

## Backup your pictures

### Setup the backup folder

```
$ kouign-amann init /home/xxx/<NAME_OF_YOUR_FOLDER>
```

### Backup your pictures
```
$ kouign-amann backup /media/SD_CARD/<FOLDER_YOU_WANT_TO_BACKUP>
```