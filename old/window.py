import os
import threading
import socket
from tkinter import *
from tkinter import filedialog, messagebox
import main

user = os.getlogin()
window = Tk()
window.geometry("400x400")
window.title('Backup Program')

#client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#client_socket.connect(("localhost", 12345))
sync_thread = None  # variable to hold the sync thread
stop_sync_flag = False  # event to signal the sync thread to stop


def browse_folder():
    folder_name = filedialog.askdirectory()
    folder_entry.delete(0, END)
    folder_entry.insert(END, folder_name)


def browse_log_file():
    log_file = filedialog.askdirectory()
    log_file_entry.delete(0, END)
    log_file_entry.insert(END, log_file)


def start_sync():
    global sync_thread, stop_sync_flag
    folder_path = folder_entry.get()
    log_file_path = log_file_entry.get()
    sync_interval = interval_entry.get()

    # Disable UI elements while syncing
    folder_entry.config(state=DISABLED)
    folder_button.config(state=DISABLED)
    log_file_entry.config(state=DISABLED)
    log_file_button.config(state=DISABLED)
    interval_entry.config(state=DISABLED)
    sync_button.config(state=DISABLED)
    stop_button.config(state=NORMAL)

    # Create a new thread for syncing
    sync_thread = threading.Thread(target=main.user_input, args=(str(folder_path), str(log_file_path), int(sync_interval)))
    sync_thread.start()

    # Create a socket to listen for stop requests
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("localhost", 12345))
    server_socket.listen(1)

    def stop_thread():
        global stop_sync_flag
        while True:
            conn, addr = server_socket.accept()
            data = conn.recv(1024)
            if data == b'stop':
                stop_sync_flag = True
                break
            conn.close()
        server_socket.close()
        stop_sync()

    # Start the stop request listener in a separate thread
    stop_thread = threading.Thread(target=stop_thread)
    stop_thread.start()


def stop_sync():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("localhost", 12345))
    client_socket.sendall(b'stop')
    client_socket.close()

    # Wait for the sync thread to stop before enabling UI elements
    sync_thread.join()

    stop_button.config(state=DISABLED)
    # Enable UI elements after stopping
    folder_entry.config(state=NORMAL)
    folder_button.config(state=NORMAL)
    log_file_entry.config(state=NORMAL)
    log_file_button.config(state=NORMAL)
    interval_entry.config(state=NORMAL)
    sync_button.config(state=NORMAL)


def exit_program():
    window.destroy()
    stop_sync()



def on_closing():
    # Override the default close behavior
    window.withdraw()  # hide the window
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        exit_program()
        return True
    else:
        window.deiconify()  # restore the window
        return False


folder_label = Label(window, text="Folder to be Backedup", width=100, height=4, fg="blue")
folder_entry = Entry(window, width=50)
folder_button = Button(window, text="Browse Folder", command=browse_folder)

log_file_label = Label(window, text="Log Folder", width=100, height=4, fg="blue")
log_file_entry = Entry(window, width=50)
log_file_button = Button(window, text="Browse Log Folder", command=browse_log_file)

interval_label = Label(window, text="Sync Interval (Minutes)", width=100, height=4, fg="blue")
interval_entry = Entry(window, width=50)

sync_button = Button(window, text="Sync", command=start_sync)
stop_button = Button(window, text="Stop", command=stop_sync, state=DISABLED)
exit_button = Button(window, text="Exit", command=exit_program)

# place widgets on the window
folder_label.pack()
folder_entry.pack()
folder_button.pack()

log_file_label.pack()
log_file_entry.pack()
log_file_button.pack()

interval_label.pack()
interval_entry.pack()

sync_button.pack()
stop_button.pack()
exit_button.pack()

# center the window on the screen
#sync_thread.join()
#client_socket.close()


window.update_idletasks()
window.mainloop()

