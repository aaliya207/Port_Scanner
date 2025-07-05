import socket
import threading
from queue import Queue
import tkinter as tk
from tkinter import ttk, messagebox

# ------------------ Port Scanning Core ------------------ #
def scan_port(host, port, open_ports):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        result = sock.connect_ex((host, port))
        if result == 0:
            open_ports.append(port)

def worker(host, port_queue, open_ports):
    while not port_queue.empty():
        port = port_queue.get()
        scan_port(host, port, open_ports)
        port_queue.task_done()

def threaded_scan(host, start_port, end_port, thread_count=100):
    open_ports = []
    port_queue = Queue()

    for port in range(start_port, end_port + 1):
        port_queue.put(port)

    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=worker, args=(host, port_queue, open_ports))
        thread.daemon = True
        thread.start()

    port_queue.join()
    return sorted(open_ports)

# ------------------ GUI Setup ------------------ #
def start_scan():
    host = host_entry.get().strip()
    try:
        start = int(start_port_entry.get())
        end = int(end_port_entry.get())
    except ValueError:
        messagebox.showerror("Invalid Input", "Start and End ports must be numbers.")
        return

    if start > end or start < 0 or end > 65535:
        messagebox.showerror("Invalid Port Range", "Please enter a valid port range (0–65535).")
        return

    result_display.config(state='normal')
    result_display.delete(1.0, tk.END)
    result_display.insert(tk.END, f"🔍 Scanning ports {start} to {end} on {host}...\n\n")
    result_display.config(state='disabled')
    root.update()

    def run_scan():
        open_ports = threaded_scan(host, start, end)
        result_display.config(state='normal')
        result_display.delete(1.0, tk.END)
        if open_ports:
            result_display.insert(tk.END, "✅ Open Ports:\n")
            for port in open_ports:
                result_display.insert(tk.END, f" - Port {port} is open\n")
        else:
            result_display.insert(tk.END, "❌ No open ports found.")
        result_display.config(state='disabled')

    threading.Thread(target=run_scan).start()

# ------------------ GUI Design ------------------ #
root = tk.Tk()
root.title("Port Scanner")
root.geometry("550x520")
root.configure(bg="#FFE3F1")  # Light pastel pink background

style = ttk.Style()
style.theme_use("default")

# Label Style
style.configure("TLabel", font=("Helvetica", 12, "bold"), foreground="#B0578D", background="#FFE3F1")

# Button Style
style.configure("TButton",
                font=("Helvetica", 12, "bold"),
                foreground="white",
                background="#D988B9",
                padding=8)
style.map("TButton",
          background=[("active", "#C147E9")])

# Title
title_label = ttk.Label(root, text="💖 Port Scanner", font=("Helvetica", 20, "bold"), foreground="#8E44AD", background="#FFE3F1")
title_label.pack(pady=20)

# Input frame
frame = tk.Frame(root, bg="#FFE3F1")
frame.pack(pady=10)

ttk.Label(frame, text="Target Host:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
host_entry = ttk.Entry(frame, width=30, font=("Helvetica", 11))
host_entry.grid(row=0, column=1, padx=5, pady=5)
host_entry.insert(0, "127.0.0.1")

ttk.Label(frame, text="Start Port:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
start_port_entry = ttk.Entry(frame, width=12, font=("Helvetica", 11))
start_port_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
start_port_entry.insert(0, "20")

ttk.Label(frame, text="End Port:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
end_port_entry = ttk.Entry(frame, width=12, font=("Helvetica", 11))
end_port_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
end_port_entry.insert(0, "100")

# Scan Button
scan_button = ttk.Button(root, text="🚀 Start Scan", command=start_scan)
scan_button.pack(pady=20)

# Results Box
result_display = tk.Text(root, width=65, height=14, bg="#FDE2FF", fg="#5D3FD3",
                         font=("Courier New", 11, "bold"), bd=0)
result_display.pack(padx=10, pady=10)
result_display.config(state='disabled')

root.mainloop()
