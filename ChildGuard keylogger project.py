import os
import tkinter as tk
from tkinter import *
from pynput import keyboard
import json
import hashlib
from tkinter import messagebox, simpledialog
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import sys
import datetime
from collections import Counter

root = tk.Tk()
root.geometry("500x400")
root.title("ChildGuard Keylogger")
root.configure(bg="lightblue")

key_list = []
key_strokes = 0  # Counter for the number of key strokes
active_times = []

# Customizable settings
max_key_strokes_per_minute = 100  # Default value, parents can change this
alert_enabled = True  # Default value, parents can change this

def update_txt_file(key):
    with open(os.path.join('logs.txt'), 'w+') as key_stroke:
        key_stroke.write(key)

def update_json_file(key_list):
    with open(os.path.join('logs.json'), 'w') as key_log:
        json.dump(key_list, key_log)

def on_press(key):
    global key_strokes, active_times
    key_strokes += 1
    update_txt_file(str(key_strokes))  # Update the logs.txt file with the number of key strokes
    if len(active_times) == 0 or active_times[-1]["end"] is not None:
        active_times.append({"start": datetime.datetime.now(), "end": None})

    # Perform AI-based anomaly detection here (e.g., check for specific sequences of keys)
    # Add your anomaly detection code here

def on_release(key):
    global key_list, key_strokes, active_times
    key_list.append({'Released': f'{key}'})
    update_json_file(key_list)
    active_times[-1]["end"] = datetime.datetime.now()

    # Check if the alert threshold is exceeded
    if alert_enabled and key_strokes > max_key_strokes_per_minute:
        messagebox.showwarning("Alert", f"Alert: Maximum key strokes per minute exceeded ({key_strokes} > {max_key_strokes_per_minute})")

def butaction():
    consent = messagebox.askyesno("Consent", "Do you want to start the keylogger and log keystrokes?")
    if consent:
        print("[+] Running Keylogger successfully!\n(!) Saving the key logs in 'logs.json'")
        with keyboard.Listener(
                on_press=on_press,
                on_release=on_release) as listener:
            listener.join()

# Function to encrypt data before saving to file
def encrypt_data(data, password):
    salt = get_random_bytes(16)
    kdf = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    key = kdf[:16]  # Use first 16 bytes as the key for AES-128 encryption
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return salt + nonce + ciphertext

def save_encrypted_logs():
    password = simpledialog.askstring("Password", "Enter a secure password for encryption:")
    if password:
        encrypted_data = encrypt_data(str(key_strokes), password)  # Encrypt the number of key strokes
        with open(os.path.join('logs_encrypted.txt'), 'wb+') as key_stroke:
            key_stroke.write(encrypted_data)
        messagebox.showinfo("Success", "Encrypted logs saved successfully!")
    else:
        messagebox.showwarning("Password Required", "Please enter a password to save encrypted logs.")

# Function to display educational resources
def show_resources():
    resources_window = Toplevel(root)
    resources_window.title("Educational Resources")
    resources_window.geometry("300x200")
    
    resources_label = Label(resources_window, text="Educational Resources:\n\n"
                            "1. Keep your child's computer in a common area where you can monitor their online activities.\n"
                            "2. Talk to your child about internet safety and the importance of not sharing personal information online.\n"
                            "3. Use parental control software to restrict access to inappropriate content.\n"
                            "4. Stay involved in your child's online life and have open communication about their online experiences.")
    resources_label.pack()

# Function to display comprehensive report
def show_report():
    total_key_strokes = key_strokes
    most_common_keys = Counter("".join(key_strokes for key_strokes in key_list)).most_common(5)
    total_active_time = sum((time["end"] - time["start"]).total_seconds() for time in active_times if time["end"] is not None)

    report_window = Toplevel(root)
    report_window.title("Comprehensive Report")
    report_window.geometry("400x300")
    
    report_label = Label(report_window, text="Comprehensive Report:\n\n"
                            f"Total Key Strokes: {total_key_strokes}\n"
                            f"Most Common Keys: {[key for key, _ in most_common_keys]}\n"
                            f"Total Active Time (seconds): {total_active_time}")
    report_label.pack()

# Function to show customizable settings
def show_settings():
    settings_window = Toplevel(root)
    settings_window.title("Customizable Settings")
    settings_window.geometry("300x200")

    max_key_strokes_label = Label(settings_window, text="Max Key Strokes per Minute:")
    max_key_strokes_label.pack()
    max_key_strokes_entry = Entry(settings_window)
    max_key_strokes_entry.insert(0, max_key_strokes_per_minute)
    max_key_strokes_entry.pack()

    def update_settings():
        global max_key_strokes_per_minute, alert_enabled
        max_key_strokes_per_minute = int(max_key_strokes_entry.get())
        alert_enabled = alert_var.get()
        settings_window.destroy()

    alert_var = BooleanVar()
    alert_var.set(alert_enabled)
    alert_checkbox = Checkbutton(settings_window, text="Enable Alert Notifications", variable=alert_var)
    alert_checkbox.pack()

    save_button = Button(settings_window, text="Save Settings", command=update_settings)
    save_button.pack()

# Update the key strokes count on the dashboard label
def update_key_strokes_label():
    key_strokes_label.config(text=f"Key Strokes: {key_strokes}")
    root.after(1000, update_key_strokes_label)  # Update every 1 second

empty_label = Label(root, text=" ")
empty_label.grid(row=0, column=0)
title_label = Label(root, text="ChildGuard", font='Verdana 11 bold')
title_label.grid(row=1, column=1)
empty_label2 = Label(root, text=" ")
empty_label2.grid(row=2, column=0)
start_button = Button(root, text="Start Keylogger", command=butaction)
start_button.grid(row=3, column=1)
empty_label3 = Label(root, text=" ")
empty_label3.grid(row=4, column=0)
resources_button = Button(root, text="Educational Resources", command=show_resources)
resources_button.grid(row=5, column=1)
empty_label4 = Label(root, text=" ")
empty_label4.grid(row=6, column=0)
encrypt_button = Button(root, text="Save Encrypted Logs", command=save_encrypted_logs)
encrypt_button.grid(row=7, column=1)
report_button = Button(root, text="Comprehensive Report", command=show_report)
report_button.grid(row=8, column=1)
settings_button = Button(root, text="Customizable Settings", command=show_settings)
settings_button.grid(row=9, column=1)

# Interactive Dashboard
dashboard_frame = Frame(root)
dashboard_frame.grid(row=10, column=1, padx=10, pady=10)

key_strokes_label = Label(dashboard_frame, text="Key Strokes: 0", font='Verdana 10 bold')
key_strokes_label.pack()

# Start updating the key strokes count on the dashboard label
update_key_strokes_label()

root.mainloop()
