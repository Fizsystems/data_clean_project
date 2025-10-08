"""
Traveler & Travel Records GUI App
Author: Olusoji Matthew
Description: Tkinter-based GUI to display, visualize, save, and print traveler travel records.
Includes validation to ensure traveler IDs match and dates are valid.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

# ------------------------------
# Global DataFrames
# ------------------------------
travelers = pd.DataFrame()
travels = pd.DataFrame()
current_fig = None  # To store the current chart figure

# ------------------------------
# Functions
# ------------------------------


def load_default_csvs():
    """Load default travelers.csv and travels.csv if they exist"""
    global travelers, travels
    if os.path.exists("travelers.csv"):
        load_travelers_csv("travelers.csv")
    else:
        messagebox.showwarning(
            "Warning", "travelers.csv not found in project directory."
        )
    if os.path.exists("travels.csv"):
        load_travels_csv("travels.csv")
    else:
        messagebox.showwarning("Warning", "travels.csv not found in project directory.")


def load_travelers_csv(file_path=None):
    """Load travelers CSV (default or user-selected)"""
    global travelers
    if not file_path:
        file_path = filedialog.askopenfilename(
            title="Select Travelers CSV", filetypes=[("CSV Files", "*.csv")]
        )
    if not file_path:
        return
    travelers = pd.read_csv(file_path)
    required_cols = {"traveler_id", "name"}
    if not required_cols.issubset(travelers.columns):
        messagebox.showerror(
            "Error", f"Travelers CSV must contain columns: {required_cols}"
        )
        travelers = pd.DataFrame()
        return
    travelers["name"] = travelers["name"].fillna("Unknown").str.title()
    traveler_combo["values"] = travelers["name"].tolist()
    messagebox.showinfo(
        "Success", f"Loaded travelers data from {os.path.basename(file_path)}"
    )


def load_travels_csv(file_path=None):
    """Load travels CSV (default or user-selected)"""
    global travels
    if not file_path:
        file_path = filedialog.askopenfilename(
            title="Select Travels CSV", filetypes=[("CSV Files", "*.csv")]
        )
    if not file_path:
        return
    travels = pd.read_csv(file_path)
    required_cols = {
        "travel_id",
        "traveler_id",
        "destination",
        "departure_date",
        "return_date",
        "purpose",
    }
    if not required_cols.issubset(travels.columns):
        messagebox.showerror(
            "Error", f"Travels CSV must contain columns: {required_cols}"
        )
        travels = pd.DataFrame()
        return
    travels["destination"] = travels["destination"].fillna("Unknown").str.title()
    travels["purpose"] = travels["purpose"].fillna("Unknown").str.capitalize()
    travels["departure_date"] = pd.to_datetime(
        travels["departure_date"], errors="coerce"
    )
    travels["return_date"] = pd.to_datetime(travels["return_date"], errors="coerce")
    travels.dropna(subset=["departure_date", "return_date"], inplace=True)
    if travels.empty:
        messagebox.showwarning("Warning", "No valid travel records found in the CSV.")
    else:
        messagebox.showinfo(
            "Success", f"Loaded travel records from {os.path.basename(file_path)}"
        )


def show_travels():
    """Display traveler records and plot trips"""
    global current_fig
    if travelers.empty or travels.empty:
        messagebox.showwarning(
            "Data Missing", "Please load travelers and travels CSV first."
        )
        return
    selected_name = traveler_var.get()
    if not selected_name:
        messagebox.showwarning("Warning", "Please select a traveler.")
        return
    # Check if traveler exists
    traveler_row = travelers[travelers["name"] == selected_name]
    if traveler_row.empty:
        messagebox.showerror(
            "Error", f"Traveler '{selected_name}' not found in travelers.csv"
        )
        return
    t_id = traveler_row["traveler_id"].values[0]

    traveler_travels = travels[travels["traveler_id"] == t_id]
    if traveler_travels.empty:
        messagebox.showinfo(
            "No Records", f"No travel records found for {selected_name}."
        )
        # Clear previous records and chart
        for widget in frame_records.winfo_children():
            widget.destroy()
        for widget in frame_chart.winfo_children():
            widget.destroy()
        current_fig = None
        return

    # Display records
    for widget in frame_records.winfo_children():
        widget.destroy()
    for idx, row in traveler_travels.iterrows():
        tk.Label(
            frame_records,
            text=f"{row['destination']} | {row['departure_date'].date()} → {row['return_date'].date()} | {row['purpose']}",
            anchor="w",
        ).pack(fill="x")

    # Plot trips
    fig, ax = plt.subplots(figsize=(6, 3))
    durations = (
        traveler_travels["return_date"] - traveler_travels["departure_date"]
    ).dt.days
    ax.bar(traveler_travels["destination"], durations, color="skyblue")
    ax.set_title(f"{selected_name}'s Trips Duration")
    ax.set_ylabel("Duration (days)")
    ax.set_xlabel("Destination")
    plt.tight_layout()

    # Embed chart in Tkinter
    for widget in frame_chart.winfo_children():
        widget.destroy()
    canvas_fig = FigureCanvasTkAgg(fig, master=frame_chart)
    canvas_fig.draw()
    canvas_fig.get_tk_widget().pack(fill="both", expand=True)

    current_fig = fig


def save_chart():
    """Save current chart as PNG or PDF"""
    if current_fig is None:
        messagebox.showwarning("No Chart", "Please generate a chart first.")
        return
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG Image", "*.png"), ("PDF Document", "*.pdf")],
    )
    if not file_path:
        return
    if file_path.endswith(".png"):
        current_fig.savefig(file_path)
    else:
        c = canvas.Canvas(file_path, pagesize=letter)
        c.drawString(100, 750, "Traveler Travel Chart")
        c.showPage()
        c.save()
    messagebox.showinfo("Saved", f"Chart saved to {file_path}")


def print_chart():
    """Print current chart"""
    if current_fig is None:
        messagebox.showwarning("No Chart", "Please generate a chart first.")
        return
    file_path = "temp_print.png"
    current_fig.savefig(file_path)
    os.startfile(file_path, "print")


# ------------------------------
# GUI Setup
# ------------------------------
root = tk.Tk()
root.title("Traveler & Travel Records App - Developed by Olusoji Matthew")
root.geometry("900x650")
root.config(bg="#e8f0fe")

# Header
tk.Label(
    root,
    text="🧳 Traveler & Travel Records Management",
    font=("Segoe UI", 16, "bold"),
    bg="#e8f0fe",
).pack(pady=10)

# Load CSV Buttons
tk.Button(
    root,
    text="Load Travelers CSV",
    command=load_travelers_csv,
    bg="#3498DB",
    fg="white",
).pack(pady=5)
tk.Button(
    root, text="Load Travels CSV", command=load_travels_csv, bg="#3498DB", fg="white"
).pack(pady=5)

# Traveler selection dropdown
tk.Label(root, text="Select Traveler:", bg="#e8f0fe").pack()
traveler_var = tk.StringVar()
traveler_combo = ttk.Combobox(
    root, textvariable=traveler_var, state="readonly", width=50
)
traveler_combo.pack(pady=5)

# Show travels button
tk.Button(
    root, text="Show Travels & Plot", bg="#27AE60", fg="white", command=show_travels
).pack(pady=10)

# Frame to display travel records
frame_records = tk.Frame(root, bg="#f0f0f0", height=100)
frame_records.pack(fill="both", expand=False, padx=20, pady=5)

# Frame to display chart
frame_chart = tk.Frame(root, bg="#ffffff")
frame_chart.pack(fill="both", expand=True, padx=20, pady=5)

# Save & Print buttons
tk.Button(
    root, text="Save Chart (PNG/PDF)", bg="#F39C12", fg="white", command=save_chart
).pack(side="left", padx=50, pady=10)
tk.Button(root, text="Print Chart", bg="#E74C3C", fg="white", command=print_chart).pack(
    side="right", padx=50, pady=10
)

# Footer
tk.Label(
    root, text="Developed by Olusoji Matthew © 2025", bg="#e8f0fe", font=("Segoe UI", 9)
).pack(side="bottom", pady=5)

# Load default CSVs if present
load_default_csvs()

root.mainloop()
