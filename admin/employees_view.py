import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from config import COLORS

class EmployeesView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        
        # Pagination variables
        self.current_page = 1
        self.records_per_page = 20
        self.total_records = 0
        self.total_pages = 1
        
        # Filter variables
        self.dept_vars = {}
        self.search_text = ""
        
        self.render()

    def render(self):
        # Clear existing widgets
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Main container with padding
        main_container = tk.Frame(self.parent_frame, bg=COLORS['bg_main'], padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # --- 1. Header Section ---
        header_frame = tk.Frame(main_container, bg=COLORS['bg_main'])
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
                  relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                  command=self.delete_employee).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="✏️ Edit", 
                  bg="#27ae60", fg="white",
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                  command=self.edit_employee).pack(side=tk.RIGHT, padx=(5, 0))
        
        tk.Button(button_frame, text="↻ Refresh", 
                  bg="#2980b9", fg="white",
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                  command=self.reset_filters).pack(side=tk.RIGHT)

        # --- 2. Filters Section ---
        filters_container = tk.Frame(main_container, bg="white", relief=tk.RIDGE, bd=1)
        filters_container.pack(fill=tk.X, pady=(0, 15))
        
        filters_frame = tk.Frame(filters_container, bg="white", padx=20, pady=15)
        filters_frame.pack(fill=tk.X)

        # Search Box
        search_frame = tk.Frame(filters_frame, bg="white")
        search_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(search_frame, text="🔍 Search Employee:", 
                font=("Segoe UI", 10, "bold"), 
                bg="white", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
        
        search_input_frame = tk.Frame(search_frame, bg="white")
        search_input_frame.pack()
        
        self.search_entry = tk.Entry(search_input_frame, font=("Segoe UI", 10), width=30, relief=tk.SOLID, bd=1)
        self.search_entry.pack(side=tk.LEFT, ipady=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        tk.Button(search_input_frame, text="🔍", 
                  bg="#3498db", fg="white", 
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=10, cursor="hand2",
                  command=self.apply_filters).pack(side=tk.LEFT, padx=(5, 0))

        # Department Filter
        dept_frame = tk.Frame(filters_frame, bg="white")
        dept_frame.pack(side=tk.LEFT)
        
        tk.Label(dept_frame, text="🏢 Department Filter:", 
                font=("Segoe UI", 10, "bold"), 
                bg="white", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
        
        dept_checkboxes_frame = tk.Frame(dept_frame, bg="white")
        dept_checkboxes_frame.pack(anchor='w')
        
        departments = self.get_departments()
        
        if departments:
            for i, dept in enumerate(departments):
                var = tk.BooleanVar(value=True)
                self.dept_vars[dept] = var
                cb = tk.Checkbutton(
                    dept_checkboxes_frame, 
                    text=dept, 
                    variable=var,
                    bg="white",
                    font=("Segoe UI", 9),
                    command=self.apply_filters,
                    cursor="hand2"
                )
                cb.grid(row=i//4, column=i%4, sticky='w', padx=(0, 15), pady=2)
        else:
            tk.Label(dept_checkboxes_frame, text="No departments found", 
                    font=("Segoe UI", 9, "italic"), 
                    bg="white", fg="#7f8c8d").pack()

        # --- 3. Table Container ---
        table_container = tk.Frame(main_container, bg="white", relief=tk.RIDGE, bd=1)
        table_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # --- 4. Style ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background="white", 
                        foreground="#2c3e50", 
                        rowheight=35, 
                        fieldbackground="white", 
                        font=("Segoe UI", 10),
                        borderwidth=0)
        style.configure("Treeview.Heading", 
                        background="#34495e", 
                        foreground="white", 
                        relief="flat", 
                        font=("Segoe UI", 11, "bold"),
                        borderwidth=0)
        style.map("Treeview", 
                  background=[('selected', '#3498db')],
                  foreground=[('selected', 'white')])

        # --- 5. Create Table ---
        scroll_y = tk.Scrollbar(table_container)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Columns include 'real_id' (hidden)
        columns = ("id", "first_name", "last_name", "email", "phone", 
                   "department", "position", "hire_date", "real_id")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", 
                                yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
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
        self.tree.column("first_name", width=120, minwidth=100)
        self.tree.column("last_name", width=120, minwidth=100)
        self.tree.column("email", width=200, minwidth=150)
        self.tree.column("phone", width=120, minwidth=100)
        self.tree.column("department", width=120, minwidth=100)
        self.tree.column("position", width=120, minwidth=100)
        self.tree.column("hire_date", width=120, minwidth=100)
        self.tree.column("real_id", width=0, stretch=tk.NO)  # Completely hidden

        self.tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.tag_configure('oddrow', background="#f8f9fa")
        self.tree.tag_configure('evenrow', background="white")

        # --- Context Menu (Right Click) ---
        self.menu = tk.Menu(self.parent_frame, tearoff=0, font=("Segoe UI", 10))
        self.menu.add_command(label="✏️ Edit Employee", command=self.edit_employee)
        self.menu.add_separator()
        self.menu.add_command(label="🗑️ Delete Employee", command=self.delete_employee)
        
        # Bind Right Click event
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Also bind double-click for editing
        self.tree.bind("<Double-1>", lambda e: self.edit_employee())

        # --- 6. Pagination Controls ---
        pagination_frame = tk.Frame(main_container, bg=COLORS['bg_main'])
        pagination_frame.pack(fill=tk.X)

        # Left side - Records info
        self.records_label = tk.Label(
            pagination_frame, 
            text="Showing 0 of 0 employees", 
            font=("Segoe UI", 10),
            bg=COLORS['bg_main'],
            fg="#2c3e50"
        )
        self.records_label.pack(side=tk.LEFT)

        # Right side - Pagination buttons
        pagination_controls = tk.Frame(pagination_frame, bg=COLORS['bg_main'])
        pagination_controls.pack(side=tk.RIGHT)

        self.btn_first = tk.Button(
            pagination_controls, text="⏮ First", 
            font=("Segoe UI", 9), bg="#ecf0f1", fg="#2c3e50",
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=self.first_page
        )
        self.btn_first.pack(side=tk.LEFT, padx=2)

        self.btn_prev = tk.Button(
            pagination_controls, text="◀ Prev", 
            font=("Segoe UI", 9), bg="#ecf0f1", fg="#2c3e50",
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=self.prev_page
        )
        self.btn_prev.pack(side=tk.LEFT, padx=2)

        self.page_label = tk.Label(
            pagination_controls, 
            text="Page 1 of 1", 
            font=("Segoe UI", 10, "bold"),
            bg=COLORS['bg_main'],
            fg="#2c3e50",
            padx=15
        )
        self.page_label.pack(side=tk.LEFT)

        self.btn_next = tk.Button(
            pagination_controls, text="Next ▶", 
            font=("Segoe UI", 9), bg="#ecf0f1", fg="#2c3e50",
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=self.next_page
        )
        self.btn_next.pack(side=tk.LEFT, padx=2)

        self.btn_last = tk.Button(
            pagination_controls, text="Last ⏭", 
            font=("Segoe UI", 9), bg="#ecf0f1", fg="#2c3e50",
            relief=tk.FLAT, padx=10, pady=5, cursor="hand2",
            command=self.last_page
        )
        self.btn_last.pack(side=tk.LEFT, padx=2)

        # Records per page selector
        tk.Label(
            pagination_controls, 
            text="Per page:", 
            font=("Segoe UI", 9),
            bg=COLORS['bg_main'],
            fg="#2c3e50"
        ).pack(side=tk.LEFT, padx=(15, 5))

        self.per_page_var = tk.StringVar(value="20")
        per_page_combo = ttk.Combobox(
            pagination_controls,
            textvariable=self.per_page_var,
            values=["10", "20", "50", "100"],
            width=5,
            state="readonly",
            font=("Segoe UI", 9)
        )
        per_page_combo.pack(side=tk.LEFT)
        per_page_combo.bind('<<ComboboxSelected>>', self.change_per_page)

        # Load initial data
        self.load_data()

    def get_departments(self):
        """Get list of all departments from employees table"""
        try:
            query = "SELECT DISTINCT department FROM employees WHERE department IS NOT NULL AND department != '' ORDER BY department"
            result = self.db.execute_query(query, fetch=True)
            return [row['department'] for row in result] if result else []
        except Exception as e:
            print(f"Error getting departments: {e}")
            return []

    def get_filtered_employees(self):
        """Get employees with filters applied"""
        try:
            # Build the base query
            query = """
                SELECT 
                    id, first_name, last_name, email, phone,
                    department, position, hire_date, id as real_id
                FROM employees
                WHERE 1=1
            """
            params = []

            # Apply search filter
            search = self.search_entry.get().strip()
            if search:
                query += " AND (first_name LIKE %s OR last_name LIKE %s OR email LIKE %s OR phone LIKE %s)"
                search_param = f"%{search}%"
                params.extend([search_param, search_param, search_param, search_param])

            # Apply department filter
            selected_depts = [dept for dept, var in self.dept_vars.items() if var.get()]
            if selected_depts and len(selected_depts) < len(self.dept_vars):  # Only filter if not all selected
                placeholders = ','.join(['%s'] * len(selected_depts))
                query += f" AND department IN ({placeholders})"
                params.extend(selected_depts)

            query += " ORDER BY id ASC"

            # Get total count for pagination
            count_query = f"SELECT COUNT(*) as total FROM ({query}) as filtered"
            count_result = self.db.execute_query(count_query, tuple(params), fetch=True)
            self.total_records = count_result[0]['total'] if count_result else 0
            self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)

            # Add pagination
            offset = (self.current_page - 1) * self.records_per_page
            query += f" LIMIT %s OFFSET %s"
            params.extend([self.records_per_page, offset])

            result = self.db.execute_query(query, tuple(params), fetch=True)
            
            # Convert result to list of tuples matching the tree column structure
            if result:
                return [tuple(row[col] for col in ['id', 'first_name', 'last_name', 'email', 
                                                     'phone', 'department', 'position', 'hire_date', 'real_id']) 
                        for row in result]
            return []

        except Exception as e:
            print(f"Error getting filtered employees: {e}")
            import traceback
            traceback.print_exc()
            return []

    def load_data(self):
        """Load all employees from database into the table"""
        # Clear current data
        try:
            self.tree.delete(*self.tree.get_children())
        except Exception:
            pass

        try:
            employees = self.get_filtered_employees()
            
            if not employees:
                # Show "No employees found" message
                self.tree.insert("", tk.END, values=("", "No employees found", "", "", "", "", "", "", ""), tags=('oddrow',))
            else:
                count = 0
                for emp in employees:
                    tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    self.tree.insert("", tk.END, values=emp, tags=(tag,))
                    count += 1
            
            self.update_pagination_controls()
            
        except Exception as e:
            print(f"Warning: Error loading data table: {e}")
            import traceback
            traceback.print_exc()

    def update_pagination_controls(self):
        """Update pagination labels and button states"""
        # Update records label
        start_record = (self.current_page - 1) * self.records_per_page + 1
        end_record = min(self.current_page * self.records_per_page, self.total_records)
        
        if self.total_records == 0:
            self.records_label.config(text="No employees found")
        else:
            self.records_label.config(text=f"Showing {start_record}-{end_record} of {self.total_records} employees")

        # Update page label
        self.page_label.config(text=f"Page {self.current_page} of {self.total_pages}")

        # Update button states
        if self.current_page <= 1:
            self.btn_first.config(state='disabled', bg='#bdc3c7')
            self.btn_prev.config(state='disabled', bg='#bdc3c7')
        else:
            self.btn_first.config(state='normal', bg='#ecf0f1')
            self.btn_prev.config(state='normal', bg='#ecf0f1')

        if self.current_page >= self.total_pages:
            self.btn_next.config(state='disabled', bg='#bdc3c7')
            self.btn_last.config(state='disabled', bg='#bdc3c7')
        else:
            self.btn_next.config(state='normal', bg='#ecf0f1')
            self.btn_last.config(state='normal', bg='#ecf0f1')

    def first_page(self):
        """Go to first page"""
        self.current_page = 1
        self.load_data()

    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        """Go to next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_data()

    def last_page(self):
        """Go to last page"""
        self.current_page = self.total_pages
        self.load_data()

    def change_per_page(self, event=None):
        """Change records per page"""
        self.records_per_page = int(self.per_page_var.get())
        self.current_page = 1
        self.load_data()

    def apply_filters(self):
        """Apply all filters and reload data"""
        self.current_page = 1
        self.load_data()

    def reset_filters(self):
        """Reset all filters to default"""
        self.search_entry.delete(0, tk.END)
        
        # Check all departments
        for var in self.dept_vars.values():
            var.set(True)
        
        self.current_page = 1
        self.load_data()

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
        
        # Check if it's the "no employees found" row
        if values[1] == "No employees found":
            return
        
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
        
        # Check if it's the "no employees found" row
        if values[1] == "No employees found":
            return
        
        real_id = values[8]  # Hidden ID column (Index 8)
        
        # Create Popup Window - MUCH BIGGER NOW!
        edit_win = Toplevel(self.parent_frame)
        edit_win.title("Edit Employee")
        edit_win.geometry("650x850")  # MUCH BIGGER!
        edit_win.configure(bg="white")
        edit_win.resizable(True, True)  # Can resize by dragging edges!
        edit_win.minsize(500, 700)  # Minimum size
        
        # Center the window
        edit_win.transient(self.parent_frame)
        edit_win.grab_set()
        
        # Bind keyboard shortcuts
        edit_win.bind('<Return>', lambda e: save_changes())  # Enter key to save
        edit_win.bind('<Escape>', lambda e: cancel_edit())   # Escape key to cancel
        
        # Header - BIGGER
        header = tk.Frame(edit_win, bg=COLORS['primary'], height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title with keyboard hint
        title_frame = tk.Frame(header, bg=COLORS['primary'])
        title_frame.pack(expand=True)
        
        tk.Label(title_frame, text="Edit Employee Details", 
                 font=("Segoe UI", 22, "bold"), 
                 bg=COLORS['primary'], fg="white").pack()
        
        tk.Label(title_frame, text="Press Enter to Save • Press Esc to Cancel", 
                 font=("Segoe UI", 10), 
                 bg=COLORS['primary'], fg="#ecf0f1").pack(pady=(5, 0))
        
        # Form Container with scrollbar support
        canvas_frame = tk.Frame(edit_win, bg="white")
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=30)
        
        form_frame = tk.Frame(canvas_frame, bg="white")
        form_frame.pack(fill=tk.BOTH, expand=True)
        
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
        
        # Create form fields - MUCH BIGGER!
        for label, val in fields:
            frame = tk.Frame(form_frame, bg="white")
            frame.pack(fill=tk.X, pady=15)  # More spacing
            
            tk.Label(frame, text=label, bg="white", 
                     font=("Segoe UI", 13, "bold"),  # Bigger font
                     fg="#34495e").pack(anchor="w", pady=(0, 10))
            
            e = tk.Entry(frame, font=("Segoe UI", 14),  # Bigger font
                         relief=tk.SOLID, bd=2)  # Thicker border
            e.insert(0, str(val) if val else "")
            e.pack(fill=tk.X, ipady=15)  # Taller input
            
            entries[label] = e
        
        # Spacer to push buttons to bottom
        tk.Frame(form_frame, bg="white", height=40).pack()
        
        # Button Frame - Fixed at bottom with MORE SPACE
        btn_frame = tk.Frame(edit_win, bg="white")
        btn_frame.pack(fill=tk.X, padx=50, pady=(15, 50), side=tk.BOTTOM)
            
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
        
        # Save Button - SUPER VISIBLE NOW!
        save_btn = tk.Button(btn_frame, text="✅ SAVE CHANGES", 
                  bg="#27ae60", fg="white", 
                  font=("Segoe UI", 15, "bold"),  # BIGGER FONT!
                  relief=tk.FLAT, cursor="hand2",
                  activebackground="#229954",
                  command=save_changes)
        save_btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, ipady=22, padx=(0, 15))  # TALLER BUTTON!
        
        # Cancel Button - SUPER VISIBLE NOW!
        cancel_btn = tk.Button(btn_frame, text="❌ CANCEL", 
                  bg="#e74c3c", fg="white", 
                  font=("Segoe UI", 15, "bold"),  # BIGGER FONT!
                  relief=tk.FLAT, cursor="hand2",
                  activebackground="#c0392b",
                  command=cancel_edit)
        cancel_btn.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, ipady=22, padx=(15, 0))  # TALLER BUTTON!