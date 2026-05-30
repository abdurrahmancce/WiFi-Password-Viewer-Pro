import tkinter as tk
from tkinter import messagebox
import subprocess


# ==========================================
# MAIN WINDOW
# ==========================================

root = tk.Tk()
root.title("WiFi Password Viewer Pro")
root.geometry("1200x700")
root.minsize(1000, 600)
root.configure(bg="#0f172a")


# ==========================================
# COLORS
# ==========================================

BG = "#0f172a"
CARD = "#1e293b"
CARD2 = "#334155"
TEXT = "#f8fafc"
MUTED = "#94a3b8"
ACCENT = "#38bdf8"

SUCCESS = "#22c55e"
PRIMARY = "#2563eb"
WARNING = "#f59e0b"
DANGER = "#ef4444"


# ==========================================
# GLOBAL VARIABLES
# ==========================================

wifi_profiles = []


# FUNCTIONS
# ==========================================

def get_wifi_profiles():
    """Load saved WiFi profiles"""

    global wifi_profiles

    try:
        output = subprocess.check_output(
            "netsh wlan show profiles",
            shell=True
        ).decode("utf-8", errors="ignore")

        wifi_profiles.clear()

        for line in output.split("\n"):

            if "All User Profile" in line:
                profile = line.split(":")[1].strip()
                wifi_profiles.append(profile)

        update_wifi_list(wifi_profiles)

        status_label.config(
            text=f"Loaded {len(wifi_profiles)} WiFi Profiles"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_wifi_list(data):

    wifi_listbox.delete(0, tk.END)

    for item in data:
        wifi_listbox.insert(tk.END, item)


def search_wifi(event=None):

    keyword = search_entry.get().lower()

    filtered = [
        wifi for wifi in wifi_profiles
        if keyword in wifi.lower()
    ]

    update_wifi_list(filtered)


def show_password():

    try:
        selected = wifi_listbox.curselection()

        if not selected:
            messagebox.showwarning(
                "Warning",
                "Please select a WiFi network."
            )
            return

        wifi_name = wifi_listbox.get(selected[0])

        result = subprocess.check_output(
            f'netsh wlan show profile "{wifi_name}" key=clear',
            shell=True
        ).decode("utf-8", errors="ignore")

        password = None
        auth_type = "Unknown"
        security_key = "Unknown"

        for line in result.split("\n"):

            line = line.strip()

            # Authentication Type
            if "Authentication" in line:
                auth_type = line.split(":")[1].strip()

            # Security Key
            if "Security key" in line:
                security_key = line.split(":")[1].strip()

            # Password
            if "Key Content" in line:
                password = line.split(":")[1].strip()

        # Handle Enterprise WiFi
        if password is None:

            if "Enterprise" in auth_type:
                password = "Enterprise Network (No Stored Password)"

            elif security_key.lower() == "absent":
                password = "Open Network"

            else:
                password = "No Password Found"

        # Update UI
        wifi_name_label.config(text=wifi_name)
        password_label.config(text=password)
        auth_type_label.config(text=auth_type)

        # Color Based on Result
        if "Enterprise" in password:
            password_label.config(fg="#f59e0b")

        elif "No Password" in password:
            password_label.config(fg="#ef4444")

        else:
            password_label.config(fg="#38bdf8")

        # Show Details
        details_text.delete("1.0", tk.END)
        details_text.insert(tk.END, result)

        status_label.config(
            text=f"Showing details for: {wifi_name}"
        )

    except Exception as e:
        messagebox.showerror("Error", str(e))


def copy_password():

    password = password_label.cget("text")

    if password:

        root.clipboard_clear()
        root.clipboard_append(password)

        messagebox.showinfo(
            "Copied",
            "Password copied to clipboard!"
        )


def clear_output():

    details_text.delete("1.0", tk.END)

    wifi_name_label.config(text="No WiFi Selected")
    password_label.config(text="********")
    auth_type_label.config(text="Unknown")

    status_label.config(text="Output Cleared")


# HEADER

header = tk.Frame(root, bg=BG)
header.pack(fill="x", pady=10)

title = tk.Label(
    header,
    text="📶 WiFi Password Viewer Pro",
    font=("Segoe UI", 28, "bold"),
    bg=BG,
    fg=TEXT
)

title.pack()

subtitle = tk.Label(
    header,
    text="Modern Tkinter GUI for Windows WiFi Profiles",
    font=("Segoe UI", 11),
    bg=BG,
    fg=MUTED
)

subtitle.pack()


# MAIN FRAME

main_frame = tk.Frame(root, bg=BG)
main_frame.pack(fill="both", expand=True, padx=15, pady=10)


# SIDEBAR

sidebar = tk.Frame(
    main_frame,
    bg=CARD,
    width=320
)

sidebar.pack(side="left", fill="y", padx=(0, 10))
sidebar.pack_propagate(False)


# Search Box

search_entry = tk.Entry(
    sidebar,
    font=("Segoe UI", 11),
    bg=CARD2,
    fg="white",
    insertbackground="white",
    relief="flat"
)

search_entry.pack(
    fill="x",
    padx=15,
    pady=15,
    ipady=10
)

search_entry.bind("<KeyRelease>", search_wifi)


# WiFi Listbox

wifi_listbox = tk.Listbox(
    sidebar,
    bg="#020617",
    fg="white",
    font=("Segoe UI", 11),
    relief="flat",
    selectbackground=ACCENT,
    selectforeground="black"
)

wifi_listbox.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=10
)


# BUTTONS

btn_frame = tk.Frame(sidebar, bg=CARD)
btn_frame.pack(fill="x", padx=15, pady=15)

button_style = {
    "font": ("Segoe UI", 10, "bold"),
    "fg": "white",
    "relief": "flat",
    "cursor": "hand2",
    "pady": 10
}

refresh_btn = tk.Button(
    btn_frame,
    text="🔄 Refresh",
    bg=SUCCESS,
    command=get_wifi_profiles,
    **button_style
)

refresh_btn.pack(fill="x", pady=5)

show_btn = tk.Button(
    btn_frame,
    text="🔍 Show Password",
    bg=PRIMARY,
    command=show_password,
    **button_style
)

show_btn.pack(fill="x", pady=5)

copy_btn = tk.Button(
    btn_frame,
    text="📋 Copy Password",
    bg=WARNING,
    command=copy_password,
    **button_style
)

copy_btn.pack(fill="x", pady=5)

clear_btn = tk.Button(
    btn_frame,
    text="🗑 Clear Output",
    bg=DANGER,
    command=clear_output,
    **button_style
)

clear_btn.pack(fill="x", pady=5)


# CONTENT AREA

content = tk.Frame(main_frame, bg=CARD)
content.pack(side="right", fill="both", expand=True)


# TOP CARD

top_card = tk.Frame(
    content,
    bg=CARD2
)

top_card.pack(fill="x", padx=20, pady=20)


# WiFi Name

wifi_title = tk.Label(
    top_card,
    text="Selected WiFi",
    font=("Segoe UI", 11),
    bg=CARD2,
    fg=MUTED
)

wifi_title.pack(anchor="w", padx=20, pady=(20, 5))

wifi_name_label = tk.Label(
    top_card,
    text="No WiFi Selected",
    font=("Segoe UI", 24, "bold"),
    bg=CARD2,
    fg=TEXT
)

wifi_name_label.pack(anchor="w", padx=20)


# Password

password_title = tk.Label(
    top_card,
    text="Password",
    font=("Segoe UI", 11),
    bg=CARD2,
    fg=MUTED
)

password_title.pack(anchor="w", padx=20, pady=(20, 5))

password_label = tk.Label(
    top_card,
    text="********",
    font=("Consolas", 20, "bold"),
    bg=CARD2,
    fg=ACCENT
)

password_label.pack(anchor="w", padx=20)


# Authentication Type

auth_title = tk.Label(
    top_card,
    text="Authentication Type",
    font=("Segoe UI", 11),
    bg=CARD2,
    fg=MUTED
)

auth_title.pack(anchor="w", padx=20, pady=(20, 5))

auth_type_label = tk.Label(
    top_card,
    text="Unknown",
    font=("Segoe UI", 14, "bold"),
    bg=CARD2,
    fg="#facc15"
)

auth_type_label.pack(anchor="w", padx=20, pady=(0, 20))


# ==========================================
# DETAILS SECTION
# ==========================================

details_title = tk.Label(
    content,
    text="Network Details",
    font=("Segoe UI", 16, "bold"),
    bg=CARD,
    fg=TEXT
)

details_title.pack(anchor="w", padx=20)


details_text = tk.Text(
    content,
    bg="#020617",
    fg="#e2e8f0",
    insertbackground="white",
    font=("Consolas", 10),
    relief="flat"
)

details_text.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=15
)


# ==========================================
# STATUS BAR
# ==========================================

status_bar = tk.Frame(root, bg="#020617")
status_bar.pack(fill="x")

status_label = tk.Label(
    status_bar,
    text="Ready",
    bg="#020617",
    fg=MUTED,
    font=("Segoe UI", 9),
    anchor="w",
    padx=10,
    pady=6
)

status_label.pack(fill="x")


# START APP

get_wifi_profiles()

root.mainloop()