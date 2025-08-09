import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime


client = MongoClient("mongodb://localhost:27017/")
db = client["expense_tracker"]
collection = db["expenses"]


root = tk.Tk()
root.title("Expense Tracker 📊")
root.geometry("850x650")
root.resizable(True, True)


style = ttk.Style()
style.theme_use("clam")

primary_color = "#4CAF50"
secondary_color = "#2E7D32"
accent_color = "#FFC107"
text_color = "#333333"
background_color = "#F5F5F5"
table_header_color = "#E0E0E0"
selected_row_color = "#BBDEFB"

root.config(bg=background_color)

style.configure("TLabel", font=("Segoe UI", 10), foreground=text_color, background=background_color)
style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"))
style.configure("Error.TLabel", foreground="red", font=("Segoe UI", 9))

style.configure("TEntry", font=("Segoe UI", 10), foreground=text_color, background="white")

style.configure("TButton",
                font=("Segoe UI", 10, "bold"),
                padding=8,
                foreground="white",
                background=primary_color)
style.map("TButton",
          background=[('active', secondary_color)])

style.configure("Treeview.Heading",
                font=("Segoe UI", 10, "bold"),
                foreground=text_color,
                background=table_header_color,
                relief="flat")
style.configure("Treeview",
                font=("Segoe UI", 9),
                foreground=text_color,
                background="white",
                rowheight=25)
style.map('Treeview',
          background=[('selected', selected_row_color)],
          foreground=[('selected', text_color)])

style.configure("TLabelframe", font=("Segoe UI", 11, "bold"), foreground=text_color, background=background_color)
style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground=text_color, background=background_color)


def clear_fields():
    date_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)
    notes_entry.delete(0, tk.END)
    date_entry.focus_set()

def fetch_expenses():
    for row in tree.get_children():
        tree.delete(row)
    for expense in collection.find().sort("date", -1):
        tree.insert("", tk.END, values=(str(expense["_id"]), expense["date"], expense["category"], f"₹{expense['amount']:.2f}", expense.get("notes", "")))

def add_expense():
    date_str = date_entry.get()
    category = category_entry.get()
    amount_str = amount_entry.get()
    notes = notes_entry.get()

    if not date_str or not category or not amount_str:
        messagebox.showerror("Input Error ⚠️", "Date, Category, and Amount are required!")
        return

    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Input Error ⚠️", "Date must be in YYYY-MM-DD format!")
        return

    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showerror("Input Error ⚠️", "Amount must be a positive number!")
            return
    except ValueError:
        messagebox.showerror("Input Error ⚠️", "Amount must be a valid number!")
        return

    expense = {
        "date": date_str,
        "category": category,
        "amount": amount,
        "notes": notes
    }
    collection.insert_one(expense)
    fetch_expenses()
    clear_fields()
    messagebox.showinfo("Success ✅", "Expense added successfully! 🎉")

def select_record(event):
    selected_item = tree.selection()
    if not selected_item:
        return
    
    values = tree.item(selected_item)["values"]

    clear_fields()

    date_entry.insert(0, values[1])
    category_entry.insert(0, values[2])
    
    amount_entry.insert(0, str(values[3]).replace("₹", ""))
    notes_entry.insert(0, values[4])


def update_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error ⚠️", "Select a record to update!")
        return

    date_str = date_entry.get()
    category = category_entry.get()
    amount_str = amount_entry.get()
    notes = notes_entry.get()

    if not date_str or not category or not amount_str:
        messagebox.showerror("Input Error ⚠️", "Date, Category, and Amount are required!")
        return

    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Input Error ⚠️", "Date must be in YYYY-MM-DD format!")
        return

    try:
        amount = float(amount_str)
        if amount <= 0:
            messagebox.showerror("Input Error ⚠️", "Amount must be a positive number!")
            return
    except ValueError:
        messagebox.showerror("Input Error ⚠️", "Amount must be a valid number!")
        return

    expense_id_str = tree.item(selected_item)["values"][0]
    try:
        expense_id = ObjectId(expense_id_str)
    except:
        messagebox.showerror("Data Error ⚠️", "Invalid record ID!")
        return

    new_data = {
        "date": date_str,
        "category": category,
        "amount": amount,
        "notes": notes
    }
    collection.update_one({"_id": expense_id}, {"$set": new_data})
    fetch_expenses()
    clear_fields()
    messagebox.showinfo("Success ✅", "Expense updated successfully! ✨")

def delete_expense():
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error ⚠️", "Select a record to delete!")
        return

    confirm = messagebox.askyesno("Confirm Delete 🗑️", "Are you sure you want to delete this expense?")
    if not confirm:
        return

    expense_id_str = tree.item(selected_item)["values"][0]
    try:
        expense_id = ObjectId(expense_id_str)
    except:
        messagebox.showerror("Data Error ⚠️", "Invalid record ID!")
        return

    collection.delete_one({"_id": expense_id})
    fetch_expenses()
    clear_fields()
    messagebox.showinfo("Deleted ✅", "Expense deleted successfully! 🗑️")


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
        client.close() 
        root.destroy()  


root.columnconfigure(0, weight=1)
root.rowconfigure(2, weight=1) 


input_frame = ttk.LabelFrame(root, text="💰 Enter Expense Details 💰", padding=(20, 10))
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew", columnspan=3)
input_frame.columnconfigure(1, weight=1)

ttk.Label(input_frame, text="📅 Date (YYYY-MM-DD):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
date_entry = ttk.Entry(input_frame)
date_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
date_entry.insert(0, datetime.date.today().strftime("%Y-%m-%d"))

ttk.Label(input_frame, text="🏷️ Category:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
category_entry = ttk.Entry(input_frame)
category_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

ttk.Label(input_frame, text="₹ Amount:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
amount_entry = ttk.Entry(input_frame)
amount_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

ttk.Label(input_frame, text="📝 Notes:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
notes_entry = ttk.Entry(input_frame)
notes_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")


button_frame = ttk.Frame(root, padding=(10, 5))
button_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew", columnspan=3)
button_frame.columnconfigure((0,1,2,3), weight=1)

ttk.Button(button_frame, text="➕ Add Expense", command=add_expense, style="TButton").grid(row=0, column=0, padx=5, pady=5, sticky="ew")
ttk.Button(button_frame, text="🔄 Update Expense", command=update_expense, style="TButton").grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ttk.Button(button_frame, text="🗑️ Delete Expense", command=delete_expense, style="TButton").grid(row=0, column=2, padx=5, pady=5, sticky="ew")
ttk.Button(button_frame, text="🧹 Clear Fields", command=clear_fields, style="TButton").grid(row=0, column=3, padx=5, pady=5, sticky="ew")


tree_frame = ttk.LabelFrame(root, text="📜 Expense History 📜", padding=(10, 10))
tree_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
tree_frame.columnconfigure(0, weight=1)
tree_frame.rowconfigure(0, weight=1)

columns = ("ID", "Date", "Category", "Amount", "Notes")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
for col in columns:
    tree.heading(col, text=col, anchor="w")
    tree.column(col, width=150 if col == "Notes" else 100, anchor="w")

tree.column("ID", width=0, stretch=tk.NO)
tree.column("Amount", anchor="e")

tree.grid(row=0, column=0, sticky="nsew")
tree.bind("<ButtonRelease-1>", select_record)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
scrollbar.grid(row=0, column=1, sticky="ns")
tree.configure(yscrollcommand=scrollbar.set)


fetch_expenses()


root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()