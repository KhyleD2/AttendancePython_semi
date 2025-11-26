import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from config import COLORS

class EmployeesView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.render()

    def render(self):
        # --- 1. Header Section ---
        header_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(header_frame, text="All Employees", 
                 font=("Segoe UI", 24, "bold"), 
                 fg="#2c3e50",
                 bg=COLORS['bg_main']).pack(side=tk.LEFT)

        # Action Buttons
        button_frame = tk.Frame(header_frame, bg=COLORS['bg_main'])
        button_frame.pack(side=tk.RIGHT)
        
        tk.Button(button_frame, text="🗑️ Delete", 
                  bg="#e74c3c", fg="white",
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=5, cursor="hand2",
                  command=self.delete_employee).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="✏️ Edit", 
                  bg="#27ae60", fg="white",
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=5, cursor="hand2",
                  command=self.edit_employee).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="↻ Refresh List", 
                  bg="#2980b9", fg="white",
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=5, cursor="hand2",
                  command=self.load_data).pack(side=tk.RIGHT)

        # --- 2. Table Container ---
        container = tk.Frame(self.parent_frame, bg="white", padx=2, pady=2)
        container.pack(fill=tk.BOTH, expand=True)

        # --- 3. Style ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground="black", 
                        rowheight=35, fieldbackground="white", font=("Segoe UI", 11))
        style.configure("Treeview.Heading", background="#34495e", foreground="white", 
                        relief="flat", font=("Segoe UI", 11, "bold"))
        style.map("Treeview", background=[('selected', '#3498db')])

        # --- 4. Create Table ---
        scroll_y = tk.Scrollbar(container)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        # Columns include 'phone' and 'real_id' (hidden)
        columns = ("id", "first_name", "last_name", "email", "phone", 
                   "department", "position", "hire_date", "real_id")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", 
                                yscrollcommand=scroll_y.set)
        
        # Define Headers
        headers = {
            "id": "ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email",
            "phone": "Phone",
            "department": "Department",
            "position": "Position",
            "hire_date": "Date Hired",
            "real_id": ""  # Hidden
        }

        for col, text in headers.items():
            self.tree.heading(col, text=text, anchor=tk.W)
            self.tree.column(col, anchor=tk.W)

        # Column Widths
        self.tree.column("id", width=80, anchor=tk.CENTER)
        self.tree.column("first_name", width=100)
        self.tree.column("last_name", width=100)
        self.tree.column("email", width=180)
        self.tree.column("phone", width=120)
        self.tree.column("department", width=100)
        self.tree.column("position", width=100)
        self.tree.column("hire_date", width=100)
        self.tree.column("real_id", width=0, stretch=tk.NO)  # Completely hidden

        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree.yview)

        self.tree.tag_configure('oddrow', background="white")
        self.tree.tag_configure('evenrow', background="#f7f9fa")

        # --- Context Menu (Right Click) ---
        self.menu = tk.Menu(self.parent_frame, tearoff=0, font=("Segoe UI", 10))
        self.menu.add_command(label="✏️ Edit Employee", command=self.edit_employee)
        self.menu.add_separator()
        self.menu.add_command(label="🗑️ Delete Employee", command=self.delete_employee)
        
        # Bind Right Click event
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Also bind double-click for editing
        self.tree.bind("<Double-1>", lambda e: self.edit_employee())

        self.load_data()

    def load_data(self):
        """Load all employees from database into the table"""
        # Safe clear
        try:
            self.tree.delete(*self.tree.get_children())
        except Exception:
            pass

        try:
            if hasattr(self.db, 'fetch_all_employees'):
                employees = self.db.fetch_all_employees()
                count = 0
                for emp in employees:
                    tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    self.tree.insert("", tk.END, values=emp, tags=(tag,))
                    count += 1
            else:
                messagebox.showerror("Error", "Database method 'fetch_all_employees' not found")
        except Exception as e:
            # Don't show pop-up error for reload issues to avoid confusing the user
            # Just log it to console so we know
            print(f"Warning: Error reloading data table: {e}")

    def show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.menu.post(event.x_root, event.y_root)

    def delete_employee(self):
        """Delete selected employee after confirmation"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an employee to delete")
            return
        
        # Get employee data
        values = self.tree.item(selected[0])['values']
        emp_name = f"{values[1]} {values[2]}"
        real_id = values[8]  # Hidden ID column (Index 8)
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete employee:\n\n{emp_name}\n\nThis action cannot be undone!",
            icon='warning'
        )
        
        if confirm:
            try:
                # Perform deletion
                self.db.delete_employee(real_id)
                
                # Refresh the table first
                self.load_data()
                
                # Then show success message
                messagebox.showinfo("Success", f"Employee '{emp_name}' deleted successfully!")
                
            except Exception as e:
                # Only show error if there's an actual exception
                messagebox.showerror("Error", f"An error occurred while deleting:\n{e}")
                # Try to refresh anyway in case it partially worked
                try:
                    self.load_data()
                except Exception as reload_error:
                    print(f"Reload failed after delete error: {reload_error}")

    def edit_employee(self):
        """Open edit dialog for selected employee"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an employee to edit")
            return
        
        values = self.tree.item(selected[0])['values']
        real_id = values[8]  # Hidden ID column (Index 8)
        
        # Create Popup Window
        edit_win = Toplevel(self.parent_frame)
        edit_win.title("Edit Employee")
        edit_win.geometry("450x500")
        edit_win.configure(bg="white")
        edit_win.resizable(False, False)
        
        # Center the window
        edit_win.transient(self.parent_frame)
        edit_win.grab_set()
        
        # Header
        header = tk.Frame(edit_win, bg=COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        tk.Label(header, text="Edit Employee Details", 
                 font=("Segoe UI", 16, "bold"), 
                 bg=COLORS['primary'], fg="white").pack(pady=15)
        
        # Form Container
        form_frame = tk.Frame(edit_win, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        entries = {}
        # Map fields to current values from the table
        # Indices: 0=id, 1=first, 2=last, 3=email, 4=phone, 5=dept, 6=pos, 7=hire_date, 8=real_id
        fields = [
            ("First Name", values[1]),
            ("Last Name", values[2]),
            ("Email", values[3]),
            ("Phone", values[4]),
            ("Department", values[5]),
            ("Position", values[6])
        ]
        
        # Create form fields
        for label, val in fields:
            frame = tk.Frame(form_frame, bg="white")
            frame.pack(fill=tk.X, pady=8)
            
            tk.Label(frame, text=label, bg="white", 
                     font=("Segoe UI", 10, "bold"), 
                     fg="#34495e").pack(anchor="w")
            
            e = tk.Entry(frame, font=("Segoe UI", 11), 
                         relief=tk.SOLID, bd=1)
            e.insert(0, str(val))
            e.pack(fill=tk.X, pady=(5, 0), ipady=8)
            
            entries[label] = e
        
        # Button Frame
        btn_frame = tk.Frame(edit_win, bg="white")
        btn_frame.pack(fill=tk.X, padx=30, pady=20)
            
        def save_changes():
            """Save updated employee information"""
            try:
                # Collect values from inputs
                first_name = entries["First Name"].get().strip()
                last_name = entries["Last Name"].get().strip()
                email = entries["Email"].get().strip()
                phone = entries["Phone"].get().strip()
                department = entries["Department"].get().strip()
                position = entries["Position"].get().strip()
                
                # Validate inputs
                if not first_name or not last_name:
                    messagebox.showwarning("Invalid Input", "First Name and Last Name are required!")
                    return
                
                # Call DB update
                # IMPORTANT: We use 'real_id' (the internal integer ID) for the WHERE clause
                self.db.update_employee(
                    real_id,
                    first_name,
                    last_name,
                    email,
                    phone,
                    department,
                    position
                )
                
                # Close the edit window
                edit_win.destroy()
                
                # Refresh the table
                self.load_data()
                
                # Show success message
                messagebox.showinfo("Success", "Employee updated successfully!")
                    
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while updating:\n{str(e)}")
        
        def cancel_edit():
            """Close dialog without saving"""
            edit_win.destroy()
        
        # Save Button
        tk.Button(btn_frame, text="✅ Confirm & Save Changes", 
                  bg=COLORS['primary'], fg="white", 
                  font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, cursor="hand2",
                  command=save_changes).pack(side=tk.LEFT, fill=tk.X, 
                                             expand=True, ipady=12, padx=(0, 5))
        
        # Cancel Button
        tk.Button(btn_frame, text="❌ Cancel", 
                  bg="#95a5a6", fg="white", 
                  font=("Segoe UI", 11, "bold"),
                  relief=tk.FLAT, cursor="hand2",
                  command=cancel_edit).pack(side=tk.RIGHT, fill=tk.X, 
                                            expand=True, ipady=12, padx=(5, 0))