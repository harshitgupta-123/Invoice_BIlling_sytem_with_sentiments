import tkinter as tk
from tkinter import messagebox
import csv
import os
from datetime import datetime
import joblib
model = joblib.load("sentiment_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

# File paths
SALES_CSV = "sales.csv"
INVOICE_FOLDER = "invoices"

if not os.path.exists(INVOICE_FOLDER):
    os.makedirs(INVOICE_FOLDER)

# GUI window
root = tk.Tk()
root.title("Smart Invoice Billing System")
root.geometry("450x600")

items = []

# --- Functions ---
def add_item():
    try:
        name = item_name.get().strip()
        qty = int(item_qty.get())
        price = float(item_price.get())
        if name == "":
            raise ValueError("Item name required")
        items.append((name, qty, price))
        listbox.insert(tk.END, f"{name} x{qty} @ ₹{price}")
        item_name.delete(0, tk.END)
        item_qty.delete(0, tk.END)
        item_price.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("Input Error", str(e))

def generate_invoice():
    if not items:
        messagebox.showwarning("No items", "Add at least one item.")
        return

    subtotal = sum(q * p for _, q, p in items)
    gst = subtotal * 0.18
    total = subtotal + gst

    feedback = feedback_entry.get().strip()
    X = vectorizer.transform([feedback])
    pred = model.predict(X)[0]
    sentiment = "Positive" if pred == 1 else "Negative"
 # Placeholder for future ML model

    # Generate bill number and file
    bill_no = len(os.listdir(INVOICE_FOLDER)) + 1
    bill_file = os.path.join(INVOICE_FOLDER, f"invoice_{bill_no:04d}.txt")

    # Save invoice to text file
    with open(bill_file, "w") as f:
        f.write("=== ABC STORE INVOICE ===\n")
        f.write(f"Invoice No: {bill_no:04d}\n")
        f.write(f"Date: {datetime.now().strftime('%d-%m-%Y %H:%M')}\n")
        f.write("-----------------------------\n")
        for name, qty, price in items:
            f.write(f"{name:12} x{qty} @ Rs{price:.2f}\n")
        f.write("-----------------------------\n")
        f.write(f"Subtotal: Rs{subtotal:.2f}\n")
        f.write(f"GST (18%): Rs{gst:.2f}\n")
        f.write(f"Total: Rs{total:.2f}\n")
        f.write("-----------------------------\n")
        f.write(f"Feedback: {feedback}\n")
        f.write(f"Sentiment: {sentiment}\n")
        f.write("=============================\n")

    # Append to CSV
    with open(SALES_CSV, "a", newline="") as csvfile:
        writer = csv.writer(csvfile)
        if os.stat(SALES_CSV).st_size == 0:
            writer.writerow(["Invoice No", "Date", "Subtotal", "GST", "Total", "Feedback", "Sentiment"])
        writer.writerow([bill_no, datetime.now().strftime("%d-%m-%Y %H:%M"), subtotal, gst, total, feedback, sentiment])

    messagebox.showinfo("Invoice Generated", f"Invoice saved as invoice_{bill_no:04d}.txt")
    items.clear()
    listbox.delete(0, tk.END)
    feedback_entry.delete(0, tk.END)

# --- GUI Layout ---
tk.Label(root, text="Item Name").pack()
item_name = tk.Entry(root)
item_name.pack()

tk.Label(root, text="Quantity").pack()
item_qty = tk.Entry(root)
item_qty.pack()

tk.Label(root, text="Price per Unit").pack()
item_price = tk.Entry(root)
item_price.pack()

tk.Button(root, text="Add Item", command=add_item).pack(pady=10)

listbox = tk.Listbox(root, width=50)
listbox.pack(pady=10)

tk.Label(root, text="Customer Feedback").pack()
feedback_entry = tk.Entry(root, width=40)
feedback_entry.pack(pady=5)

tk.Button(root, text="Generate Invoice", command=generate_invoice).pack(pady=20)

root.mainloop()
