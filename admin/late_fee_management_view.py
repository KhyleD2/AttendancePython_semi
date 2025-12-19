import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS

class LateFeeManagementView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.all_data = []  # Store all data for filtering
        self.department_filters = {}  # Track department filter states
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

        # --- Filter Section ---
        filter_frame = tk.Frame(self.parent_frame, bg="white", padx=20, pady=15)
        filter_frame.pack(fill=tk.X)

        # Search Filter
        search_frame = tk.Frame(filter_frame, bg="white")
        search_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(search_frame, text="🔍 Search Employee:", 
                font=("Segoe UI", 10), bg="white").pack(anchor="w")
        
        search_container = tk.Frame(search_frame, bg="white")
        search_container.pack(fill=tk.X, pady=(5, 0))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.apply_filters())
        
        search_entry = tk.Entry(search_container, textvariable=self.search_var,
                               font=("Segoe UI", 10), width=25)
        search_entry.pack(side=tk.LEFT, ipady=3)
        
        search_btn = tk.Button(search_container, text="🔍",
                              bg="#3498db", fg="white", font=("Segoe UI", 9),
                              relief=tk.FLAT, padx=8, cursor="hand2",
                              command=self.apply_filters)
        search_btn.pack(side=tk.LEFT, padx=(5, 0))

        # Department Filter
        dept_frame = tk.Frame(filter_frame, bg="white")
        dept_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(dept_frame, text="🏢 Department Filter:", 
                font=("Segoe UI", 10), bg="white").pack(anchor="w")
        
        dept_checkbox_frame = tk.Frame(dept_frame, bg="white")
        dept_checkbox_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Department checkboxes
        departments = ["Finance", "IT", "Marketing", "Operations", "Sales"]
        for dept in departments:
            var = tk.BooleanVar(value=True)
            self.department_filters[dept] = var
            
            cb = tk.Checkbutton(dept_checkbox_frame, text=dept, variable=var,
                               font=("Segoe UI", 9), bg="white",
                               command=self.apply_filters, cursor="hand2")
            cb.pack(side=tk.LEFT, padx=5)

        # Payment Status Filter
        status_frame = tk.Frame(filter_frame, bg="white")
        status_frame.pack(side=tk.LEFT)
        
        tk.Label(status_frame, text="💳 Payment Status:", 
                font=("Segoe UI", 10), bg="white").pack(anchor="w")
        
        status_checkbox_frame = tk.Frame(status_frame, bg="white")
        status_checkbox_frame.pack(fill=tk.X, pady=(5, 0))
        
        # Payment status checkboxes
        self.status_paid = tk.BooleanVar(value=True)
        self.status_pending = tk.BooleanVar(value=True)
        
        cb_paid = tk.Checkbutton(status_checkbox_frame, text="Paid", 
                                variable=self.status_paid,
                                font=("Segoe UI", 9), bg="white",
                                command=self.apply_filters, cursor="hand2")
        cb_paid.pack(side=tk.LEFT, padx=5)
        
        cb_pending = tk.Checkbutton(status_checkbox_frame, text="Pending", 
                                   variable=self.status_pending,
                                   font=("Segoe UI", 9), bg="white",
                                   command=self.apply_filters, cursor="hand2")
        cb_pending.pack(side=tk.LEFT, padx=5)

        # --- Table Container ---
        container = tk.Frame(self.parent_frame, bg="white", padx=20, pady=20)
        container.pack(fill=tk.BOTH, expand=True)

        # Table
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
        
        # Style alternating rows
        self.tree.tag_configure('oddrow', background='#f9f9f9')
        self.tree.tag_configure('evenrow', background='white')
        
        self.load_data()

    def load_data(self):
        """Load late fee summary data from database"""
        try:
            print("DEBUG - Fetching admin fee summary...")
            data = self.db.get_admin_fee_summary()
            print(f"DEBUG - Got {len(data) if data else 0} records")
            
            if data:
                self.all_data = []
                for row in data:
                    print(f"DEBUG - Processing row: {row}, type: {type(row)}")
                    
                    # Handle both dictionary and tuple formats
                    if isinstance(row, dict):
                        record = {
                            'name': row.get('name', 'Unknown'),
                            'dept': row.get('department', 'N/A'),
                            'late_count': row.get('late_count', 0),
                            'total_fees': float(row.get('total_fees', 0) or 0),
                            'paid': float(row.get('paid', 0) or 0),
                            'unpaid': float(row.get('unpaid', 0) or 0)
                        }
                    else:
                        # Tuple format: (id, name, dept, late_count, total_fees, paid, unpaid)
                        record = {
                            'name': row[1],
                            'dept': row[2],
                            'late_count': row[3],
                            'total_fees': float(row[4] or 0),
                            'paid': float(row[5] or 0),
                            'unpaid': float(row[6] or 0)
                        }
                    
                    self.all_data.append(record)
                
                print("DEBUG - Data loaded successfully!")
                self.apply_filters()
            else:
                print("DEBUG - No late fee data found")
                self.all_data = []
                self.display_data([])
                
        except Exception as e:
            error_msg = f"Failed to load late fee data:\n{e}"
            messagebox.showerror("Error", error_msg)
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    def apply_filters(self):
        """Apply search and department filters to the data"""
        search_term = self.search_var.get().lower().strip()
        
        # Get selected departments
        selected_depts = [dept for dept, var in self.department_filters.items() 
                         if var.get()]
        
        # Get payment status filters
        show_paid = self.status_paid.get()
        show_pending = self.status_pending.get()
        
        # Filter data
        filtered_data = []
        for record in self.all_data:
            # Check department filter
            if record['dept'] not in selected_depts:
                continue
            
            # Check search filter
            if search_term and search_term not in record['name'].lower():
                continue
            
            # Check payment status filter
            is_paid = record['unpaid'] == 0
            is_pending = record['unpaid'] > 0
            
            if is_paid and not show_paid:
                continue
            if is_pending and not show_pending:
                continue
            
            filtered_data.append(record)
        
        self.display_data(filtered_data)

    def display_data(self, data):
        """Display filtered data in the tree"""
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert filtered data
        for idx, record in enumerate(data):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert("", tk.END, values=(
                record['name'],
                record['dept'],
                record['late_count'],
                f"₱{record['total_fees']:.2f}",
                f"₱{record['paid']:.2f}",
                f"₱{record['unpaid']:.2f}"
            ), tags=(tag,))