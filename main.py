import hashlib
import os
import shutil
import asyncio

asyncio.set_event_loop(asyncio.new_event_loop())
eventloop = asyncio.get_event_loop()

# TODO:
# dummy proof the inputs
# path has to be a string
# synch_interval needs to be a positive number
# log_path has to be a string


def user_input():
    path_user_selected = input("Enter the Folder path: \n")
    log_directory = input("Enter the Log file path: \n")
    synch_interval = input("Enter the synchronization interval in MINUTES: \n")

    if path_user_selected == log_directory:
        eventloop.create_task(sync(int(synch_interval)*60, path_user_selected,
                                   get_folder_name(path_user_selected)))
    else:
        eventloop.create_task(sync(int(synch_interval)*60, path_user_selected, log_directory))
    eventloop.run_forever()


async def sync(delay, path_user_selected, log_directory):
    while eventloop.is_running():
        file_verification(path_user_selected, log_directory)
        await asyncio.sleep(delay)


def get_folder_name(path_user, before=True):  # P:\Projects\Python\Folder_Backupper\folder_test
    last_occurrence = path_user.rfind("\\")  # finds the index of the last occurrence of the backslash
    if last_occurrence != -1:  # if no \ is found, rfind returns -1
        return path_user[last_occurrence + 1:]  # copies everything after the backslash


def create_backup_folder(path):  # P:\Projects\Python\Folder_Backupper\folder_test
    folder_name = get_folder_name(path)
    directory = os.path.dirname(path)
    path_backup = os.path.join(directory, folder_name + "_backup")

    if not os.path.isdir(path_backup):  # P:\Projects\Python\Folder_Backupper\folder_test_backup
        shutil.copytree(path, path_backup)  # creates a folder as original_backup. In the directory of the original
        return path_backup
    return path_backup


def file_verification(path, log_path):  # P:\Projects\Python\Folder_Backupper\folder_test
    buffer_size = bytearray(131072) #128KB buffer
    backup_folder = create_backup_folder(path)  # P:\Projects\Python\Folder_Backupper\folder_test_backup
    log = []

    hash_original = set(os.listdir(path))
    hash_backup = set(os.listdir(backup_folder))

    added_files = hash_original - hash_backup
    if added_files:
        log.append(("Copied Files: ", added_files))
        add_files(added_files, path, backup_folder)

    deleted_files = hash_backup - hash_original
    if deleted_files:
        log.append(("Deleted Files: ", deleted_files))
        remove_files(deleted_files, backup_folder)

    common_files = hash_original & hash_backup
    files_unsync = set()
    for file in common_files:
        file1 = os.path.join(path, file)
        file2 = os.path.join(backup_folder, file)
        with open(file1, "rb") as f1, open(file2, "rb") as f2:
            hash_file1 = hashlib.md5(f1.read(buffer_size)).hexdigest()
            hash_file2 = hashlib.md5(f2.read(buffer_size)).hexdigest()
            if hash_file1 != hash_file2:
                log.append(("Modified Files: ", file))
                files_unsync.add(file)
    sync_files(files_unsync, path, backup_folder)
    log.append(("Common Files: ", common_files))

    generate_log(log, log_path)


def add_files(files, original_folder, folder_target):
    for file_name in files:
        shutil.copyfile(original_folder+"\\"+file_name, folder_target+"\\"+file_name)


def sync_files(files, original_folder, folder_target):
    for file in files:
        if os.path.isfile(folder_target+"\\"+file):
            with open(original_folder+"\\"+file, "r") as src:
                with open(folder_target+"\\"+file, "w") as dst:
                    dst.write(src.read())


def remove_files(files, folder_target):
    for file in files:
        file_path = os.path.join(folder_target, file)
        os.remove(file_path)


def generate_log(log, log_path):
    if os.path.isfile(log_path+"\\"+"log.txt"):
        with open(log_path+"\\"+"log.txt", "a") as lg:
            lg.write(str(log)+"\n")
    else:
        with open(log_path+"\\"+"log.txt", "w") as lg:
            lg.write(str(log)+"\n")
    print("Finished writing log." + log)


user_input()
