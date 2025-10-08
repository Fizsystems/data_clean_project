"""
Traveler & Travel Records GUI App (Auto-Load Cleaned CSVs)
Author: Olusoji Matthew
Description: Load, display, and visualize travel records with options to save or print charts.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from reportlab.pdfgen import canvas
import os

# -------------------------------
# Global Variables
# -------------------------------
travelers_df = pd.DataFrame()
travels_df = pd.DataFrame()


# -------------------------------
# Load CSV Functions
# -------------------------------
def load_travelers(file_path=None):
    global travelers_df
    if not file_path:
        # Try loading cleaned file automatically
        if os.path.exists("travelers_clean.csv"):
            file_path = "travelers_clean.csv"
        else:
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if not file_path:
                return
    travelers_df = pd.read_csv(file_path)
    populate_travelers_table()
    populate_traveler_dropdown()


def load_travels(file_path=None):
    global travels_df
    if not file_path:
        # Try loading cleaned file automatically
        if os.path.exists("travels_clean.csv"):
            file_path = "travels_clean.csv"
        else:
            file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
            if not file_path:
                return
    travels_df = pd.read_csv(file_path)
    populate_travels_table()
    # Update chart for all travelers
    plot_chart(travels_df)


# -------------------------------
# Populate Tables
# -------------------------------
def populate_travelers_table():
    for row in traveler_table.get_children():
        traveler_table.delete(row)
    for _, row in travelers_df.iterrows():
        traveler_table.insert(
            "",
            "end",
            values=(
                row["traveler_id"],
                row["name"],
                row["email"],
                row["phone"],
                row["passport_number"],
            ),
        )


def populate_travels_table(filtered_df=None):
    for row in travel_table.get_children():
        travel_table.delete(row)
    df = filtered_df if filtered_df is not None else travels_df
    for _, row in df.iterrows():
        travel_table.insert(
            "",
            "end",
            values=(
                row["travel_id"],
                row["traveler_id"],
                row["destination"],
                row["departure_date"],
                row["return_date"],
                row["purpose"],
            ),
        )


# -------------------------------
# Traveler Dropdown
# -------------------------------
def populate_traveler_dropdown():
    if travelers_df.empty:
        traveler_dropdown["values"] = ["All Travelers"]
        traveler_dropdown.current(0)
        return
    traveler_dropdown["values"] = ["All Travelers"] + travelers_df["name"].tolist()
    traveler_dropdown.current(0)


def on_traveler_select(event):
    selected = traveler_dropdown.get()
    if selected == "All Travelers":
        populate_travels_table()
        plot_chart(travels_df)
    else:
        traveler_id = travelers_df[travelers_df["name"] == selected][
            "traveler_id"
        ].values[0]
        filtered_df = travels_df[travels_df["traveler_id"] == traveler_id]
        populate_travels_table(filtered_df)
        plot_chart(filtered_df)


# -------------------------------
# Plot Chart
# -------------------------------
def plot_chart(df):
    for widget in chart_frame.winfo_children():
        widget.destroy()
    if df.empty:
        return
    df["departure_date"] = pd.to_datetime(df["departure_date"])
    df["return_date"] = pd.to_datetime(df["return_date"])
    df["duration_days"] = (df["return_date"] - df["departure_date"]).dt.days
    agg = df.groupby("destination")["duration_days"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    agg.plot(kind="bar", ax=ax, color="skyblue")
    ax.set_title("Total Trip Duration by Destination")
    ax.set_ylabel("Days")
    ax.set_xlabel("Destination")
    plt.xticks(rotation=45)
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()


# -------------------------------
# Save / Print Chart
# -------------------------------
def save_chart_png():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".png", filetypes=[("PNG Image", "*.png")]
    )
    if file_path:
        plt.savefig(file_path)
        messagebox.showinfo("Saved", f"Chart saved as {file_path}")


def save_chart_pdf():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".pdf", filetypes=[("PDF File", "*.pdf")]
    )
    if file_path:
        c = canvas.Canvas(file_path)
        c.drawString(100, 750, "Travel Duration Chart")
        c.showPage()
        c.save()
        messagebox.showinfo("Saved", f"Chart PDF saved as {file_path}")


# -------------------------------
# GUI Setup
# -------------------------------
root = tk.Tk()
root.title("Traveler & Travel Records App")
root.geometry("1000x700")
root.config(bg="#f0f0f0")

# Load Buttons
btn_frame = tk.Frame(root, bg="#f0f0f0")
btn_frame.pack(pady=10)

tk.Button(
    btn_frame, text="Load Travelers CSV", command=lambda: load_travelers(None)
).grid(row=0, column=0, padx=10)
tk.Button(btn_frame, text="Load Travels CSV", command=lambda: load_travels(None)).grid(
    row=0, column=1, padx=10
)

# Traveler Dropdown
tk.Label(btn_frame, text="Select Traveler:", bg="#f0f0f0").grid(row=0, column=2, padx=5)
traveler_dropdown = ttk.Combobox(btn_frame, state="readonly")
traveler_dropdown.grid(row=0, column=3, padx=5)
traveler_dropdown.bind("<<ComboboxSelected>>", on_traveler_select)

# Tables
traveler_table = ttk.Treeview(
    root,
    columns=("ID", "Name", "Email", "Phone", "Passport"),
    show="headings",
    height=8,
)
for col in traveler_table["columns"]:
    traveler_table.heading(col, text=col)
traveler_table.pack(pady=10, fill="x")

travel_table = ttk.Treeview(
    root,
    columns=(
        "Travel ID",
        "Traveler ID",
        "Destination",
        "Departure",
        "Return",
        "Purpose",
    ),
    show="headings",
    height=10,
)
for col in travel_table["columns"]:
    travel_table.heading(col, text=col)
travel_table.pack(pady=10, fill="x")

# Chart Frame
chart_frame = tk.Frame(root)
chart_frame.pack(pady=10, fill="both", expand=True)

# Save/Print Buttons
chart_btn_frame = tk.Frame(root, bg="#f0f0f0")
chart_btn_frame.pack(pady=10)
tk.Button(chart_btn_frame, text="Save Chart as PNG", command=save_chart_png).grid(
    row=0, column=0, padx=10
)
tk.Button(chart_btn_frame, text="Save Chart as PDF", command=save_chart_pdf).grid(
    row=0, column=1, padx=10
)

# -------------------------------
# Auto-load cleaned CSVs
# -------------------------------
load_travelers()
load_travels()

# Start GUI
root.mainloop()
