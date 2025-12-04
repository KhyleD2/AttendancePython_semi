import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS

class LateFeeManagementView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.render()

    def render(self):
        # Clear frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # --- Header ---
        header = tk.Frame(self.parent_frame, bg="#072446", padx=20, pady=20)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="💰 Late Fee Overview", 
                font=("Segoe UI", 20, "bold"), 
                fg="white", bg="#072446").pack(side=tk.LEFT)
        
        tk.Button(header, text="↻ Refresh", 
                 bg="#3498db", fg="white", font=("Segoe UI", 10, "bold"),
                 relief=tk.FLAT, padx=15, pady=5, cursor="hand2",
                 command=self.load_data).pack(side=tk.RIGHT)

        # --- Table ---
        container = tk.Frame(self.parent_frame, bg="white", padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "dept", "instances", "total_fees", "paid", "unpaid")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=15)
        
        # Define Headings
        headers = {
            "name": "Employee Name",
            "dept": "Department",
            "instances": "Late Count",
            "total_fees": "Total Charged",
            "paid": "Amount Paid",
            "unpaid": "Balance Due"
        }
        
        for col, title in headers.items():
            self.tree.heading(col, text=title)
            self.tree.column(col, anchor="center", width=120)
        
        # Make the name column wider
        self.tree.column("name", width=200, anchor="w")

        # Scrollbar
        scroll = tk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_data()

    def load_data(self):
        """Load late fee summary data from database"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            print("DEBUG - Fetching admin fee summary...")
            data = self.db.get_admin_fee_summary()
            print(f"DEBUG - Got {len(data) if data else 0} records")
            
            if data:
                for row in data:
                    print(f"DEBUG - Processing row: {row}, type: {type(row)}")
                    
                    # ✅ Handle both dictionary and tuple formats
                    if isinstance(row, dict):
                        # Dictionary format
                        name = row.get('name', 'Unknown')
                        dept = row.get('department', 'N/A')
                        late_count = row.get('late_count', 0)
                        total_fees = float(row.get('total_fees', 0) or 0)
                        paid = float(row.get('paid', 0) or 0)
                        unpaid = float(row.get('unpaid', 0) or 0)
                    else:
                        # Tuple format: (id, name, dept, late_count, total_fees, paid, unpaid)
                        name = row[1]
                        dept = row[2]
                        late_count = row[3]
                        total_fees = float(row[4] or 0)
                        paid = float(row[5] or 0)
                        unpaid = float(row[6] or 0)
                    
                    self.tree.insert("", tk.END, values=(
                        name,
                        dept,
                        late_count,
                        f"₱{total_fees:.2f}",
                        f"₱{paid:.2f}",
                        f"₱{unpaid:.2f}"
                    ))
                    
                print("DEBUG - Data loaded successfully!")
            else:
                print("DEBUG - No late fee data found")
                
        except Exception as e:
            error_msg = f"Failed to load late fee data:\n{e}"
            messagebox.showerror("Error", error_msg)
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()