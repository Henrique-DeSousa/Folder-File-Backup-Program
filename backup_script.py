import asyncio
import hashlib
import logging
import os
import shutil

asyncio.set_event_loop(asyncio.new_event_loop())
eventloop = asyncio.get_event_loop()


def user_input():
    while True:
        path_user_selected = input("Enter the Folder path: \n")
        if os.path.exists(path_user_selected):
            break
        print("Invalid path. Provide a valid path.")
    while True:
        log_directory = input("Enter the Log file path: \n")
        if os.path.exists(log_directory):
            break
        print("Invalid path. Provide a valid path.")
    while True:
        try:
            synch_interval = int(input("Enter the synchronization interval in MINUTES: \n"))
            if synch_interval <= 0:
                print("Please insert a valid interval.")
            else:
                break
        except ValueError:
            print("Please insert a valid interval.")
    minutes = synch_interval * 60
    if path_user_selected == log_directory:
        backup_folder_path = create_backup_folder(path_user_selected)
        log_setup(os.path.dirname(path_user_selected))
        eventloop.create_task(sync(minutes, path_user_selected, backup_folder_path))
    else:
        backup_folder_path = create_backup_folder(path_user_selected)
        log_setup(log_directory)
        eventloop.create_task(sync(minutes, path_user_selected, backup_folder_path))
    eventloop.run_forever()


def create_backup_folder(path):
    folder_name = get_folder_name(path)
    directory = os.path.dirname(path)
    path_backup = os.path.join(directory, folder_name + "_backup")

    if not os.path.isdir(path_backup):
        shutil.copytree(path, path_backup)  # creates a folder as original_backup. In the directory of the original
        return path_backup
    return path_backup


async def sync(delay, path_user_selected, backup_folder):
    while eventloop.is_running():
        compare_folders(path_user_selected, backup_folder)
        await asyncio.sleep(delay)


def get_folder_name(path_user):
    last_occurrence = path_user.rfind("\\")  # finds the index of the last occurrence of the backslash
    if last_occurrence != -1:  # if no \ is found, rfind returns -1
        return path_user[last_occurrence + 1:]  # copies everything after the backslash


def compare_folders(user_path_defined, backup_path_defined):
    deleted_data = []
    for data in os.listdir(user_path_defined):  # lists all the contents inside source
        path_source = os.path.join(user_path_defined, data)  # gets the path of the file or folder and joins with source
        path_backup = os.path.join(backup_path_defined, data)  # gets the path of the file or folder with backup
        if os.path.isdir(path_source):  # checks if the path_source is a directory
            if not os.path.isdir(path_backup):  # if it is but not in the backup
                sync_data(user_path_defined, backup_path_defined)  # calls the sync_data func to add the folder
            else:
                compare_folders(path_source, path_backup)  # if it's a folder, just reiterates
        else:
            if not os.path.isfile(path_backup):  # if's it's a file and not in backup
                sync_data(user_path_defined, backup_path_defined)  # creates the file in the backup with sync_data
    for data in os.listdir(backup_path_defined):  # iterates over the backup directories
        path_source = os.path.join(user_path_defined, data)  # generates paths
        path_backup = os.path.join(backup_path_defined, data)  # generates paths
        if not os.path.exists(path_source):  # if the path doesn't exist in the source folder
            deleted_data.append(path_backup)  # appends to a deleted_data due to deleting several things at once
            remove_data(deleted_data)  # calls remove_data function with the deleted_data
    sync_data(user_path_defined, backup_path_defined)  # called to check if any modifications where made


def sync_data(target_path, path_backup):
    buffer_size = 131072  # 128KB buffer
    if not os.path.exists(path_backup):
        os.makedirs(path_backup)  # creates the directories needed to accommodate the folder.
        log_write(f"Created Folder: {os.path.basename(path_backup)}")
    for files in os.listdir(target_path):
        source_folder = os.path.join(target_path, files)
        destination_folder = os.path.join(path_backup, files)
        if os.path.isdir(source_folder):
            sync_data(source_folder, destination_folder) # if it's a folder just reiterates
        else:
            if not os.path.exists(destination_folder):
                shutil.copy(source_folder, destination_folder)
                log_write(f"Created File: {os.path.basename(destination_folder)}")
            else:
                with open(source_folder, "rb+") as f1, open(destination_folder, "rb+") as f2:  # opens files with read bytes
                    hash_source_file = hashlib.md5(f1.read(buffer_size)).hexdigest()  # generates the hash md5 of the file
                    hash_backup_file = hashlib.md5(f2.read(buffer_size)).hexdigest()
                    if hash_source_file != hash_backup_file:  # compares both hashes and checks if there's a change
                        shutil.copy2(source_folder, destination_folder)  # copies the changes
                        log_write(f"Modified File: {files} in {destination_folder}")  # writes to the log file the changes


def remove_data(removed_data):
    for data in removed_data:
        if os.path.isdir(data):
            shutil.rmtree(data)
            log_write(f"Deleted Folder: {data}")
        elif os.path.isfile(data):
            os.remove(data)
            log_write(f"Deleted File: {data}")


def log_setup(log_path):
    log_format = '%(asctime)s %(message)s'
    logging.basicConfig(filename=log_path + "/Log.log", encoding='utf-8', level=logging.INFO,
                        format=log_format, datefmt='%Y-%m-%d %H:%M:%S')


def log_write(log):
    logging.info(log)
    print(log)


user_input()
