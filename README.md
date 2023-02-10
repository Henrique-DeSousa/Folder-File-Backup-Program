# Folder and File Backup Program

This program, written in Python, is used to backup existing folders into a new folder located **one** directory up.

To perform a backup, you only need to provide three inputs:
- The path of the folder you want to backup;
- The path for the log file where you want to view the changes;
- The synchronization interval.

Given the path of the folder you want to backup (e.g. C:\Pictures\Important_Pictures), the backup folder will be named as: *C:\Pictures\Important_Pictures_backup*.
The log file also requires a path and does not have to be in the same directory or folder as the original folder.
The synchronization interval is in **minutes**, so any input given will be converted to minutes. For example: 01 is equivalent to 1 minute, -1 is not a valid input, and 0 is also not a valid input. There is currently no limit to the amount of time it may take to synchronize.
