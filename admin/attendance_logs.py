import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv

try:
    from tkcalendar import DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

class AttendanceLogsView:
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
        
        self.render()
    
    def render(self):
        # Clear existing widgets
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Main container with padding
        main_container = tk.Frame(self.parent_frame, bg='#f5f6fa', padx=20, pady=20)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # --- 1. Header Section ---
        header_frame = tk.Frame(main_container, bg='#f5f6fa')
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(header_frame, text="Attendance Logs", 
                 font=("Segoe UI", 24, "bold"), 
                 fg="#2c3e50", 
                 bg='#f5f6fa').pack(side=tk.LEFT)

        # Buttons frame
        buttons_frame = tk.Frame(header_frame, bg='#f5f6fa')
        buttons_frame.pack(side=tk.RIGHT)

        # Refresh Button
        refresh_btn = tk.Button(buttons_frame, text="↻ Refresh", 
                  bg="#3498db", fg="white", 
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                  command=self.reset_filters)
        refresh_btn.pack(side=tk.RIGHT, padx=(5, 0))

        # Export Button
        export_btn = tk.Button(buttons_frame, text="📥 Export", 
                  bg="#27ae60", fg="white", 
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                  command=self.export_logs)
        export_btn.pack(side=tk.RIGHT)

        # --- 2. Filters Section ---
        filters_container = tk.Frame(main_container, bg="white", relief=tk.RIDGE, bd=1)
        filters_container.pack(fill=tk.X, pady=(0, 15))
        
        filters_frame = tk.Frame(filters_container, bg="white", padx=20, pady=15)
        filters_frame.pack(fill=tk.X)

        # Row 1: Search and Date Range
        row1 = tk.Frame(filters_frame, bg="white")
        row1.pack(fill=tk.X, pady=(0, 10))

        # Search Box
        search_frame = tk.Frame(row1, bg="white")
        search_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(search_frame, text="🔍 Search Employee:", 
                font=("Segoe UI", 10, "bold"), 
                bg="white", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 10), width=30, relief=tk.SOLID, bd=1)
        self.search_entry.pack()
        self.search_entry.bind('<KeyRelease>', lambda e: self.apply_filters())

        # Date Range Filter
        date_frame = tk.Frame(row1, bg="white")
        date_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(date_frame, text="📅 Date Range:", 
                font=("Segoe UI", 10, "bold"), 
                bg="white", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
        
        date_inputs_frame = tk.Frame(date_frame, bg="white")
        date_inputs_frame.pack()
        
        tk.Label(date_inputs_frame, text="From:", 
                font=("Segoe UI", 9), 
                bg="white").grid(row=0, column=0, padx=(0, 5), sticky='w')
        
        if HAS_CALENDAR:
            self.start_date_entry = DateEntry(
                date_inputs_frame,
                font=("Segoe UI", 9),
                width=12,
                background='#3498db',
                foreground='white',
                borderwidth=1,
                date_pattern='yyyy-mm-dd'
            )
            self.start_date_entry.set_date(datetime.now() - timedelta(days=30))
            self.start_date_entry.bind('<<DateEntrySelected>>', lambda e: self.apply_filters())
        else:
            self.start_date_entry = tk.Entry(date_inputs_frame, font=("Segoe UI", 9), width=12, relief=tk.SOLID, bd=1)
            self.start_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
        
        self.start_date_entry.grid(row=0, column=1, padx=(0, 10))
        
        tk.Label(date_inputs_frame, text="To:", 
                font=("Segoe UI", 9), 
                bg="white").grid(row=0, column=2, padx=(0, 5), sticky='w')
        
        if HAS_CALENDAR:
            self.end_date_entry = DateEntry(
                date_inputs_frame,
                font=("Segoe UI", 9),
                width=12,
                background='#3498db',
                foreground='white',
                borderwidth=1,
                date_pattern='yyyy-mm-dd'
            )
            self.end_date_entry.bind('<<DateEntrySelected>>', lambda e: self.apply_filters())
        else:
            self.end_date_entry = tk.Entry(date_inputs_frame, font=("Segoe UI", 9), width=12, relief=tk.SOLID, bd=1)
            self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        self.end_date_entry.grid(row=0, column=3)

        # Apply Button
        apply_btn = tk.Button(row1, text="Apply Filters", 
                  bg="#3498db", fg="white", 
                  font=("Segoe UI", 9, "bold"), 
                  relief=tk.FLAT, padx=20, pady=8, cursor="hand2",
                  command=self.apply_filters)
        apply_btn.pack(side=tk.LEFT)

        # Row 2: Department Checkboxes
        row2 = tk.Frame(filters_frame, bg="white")
        row2.pack(fill=tk.X)

        tk.Label(row2, text="🏢 Department Filter:", 
                font=("Segoe UI", 10, "bold"), 
                bg="white", fg="#2c3e50").pack(anchor='w', pady=(0, 5))
        
        dept_checkboxes_frame = tk.Frame(row2, bg="white")
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

        # --- 4. Style the Table ---
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

        # --- 5. Create the Table ---
        scroll_y = tk.Scrollbar(table_container)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        scroll_x = tk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        columns = ("name", "dept", "date", "in", "out", "status")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", 
                                 yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)
        
        headers = {
            "name": "Employee Name",
            "dept": "Department",
            "date": "Date",
            "in": "Clock In",
            "out": "Clock Out",
            "status": "Status"
        }

        for col, text in headers.items():
            self.tree.heading(col, text=text, anchor=tk.W)
            self.tree.column(col, anchor=tk.W)

        self.tree.column("name", width=200, minwidth=150)
        self.tree.column("dept", width=150, minwidth=100)
        self.tree.column("date", width=120, minwidth=100)
        self.tree.column("in", width=120, minwidth=100)
        self.tree.column("out", width=120, minwidth=100)
        self.tree.column("status", width=100, minwidth=80)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        self.tree.tag_configure('oddrow', background="#f8f9fa")
        self.tree.tag_configure('evenrow', background="white")
        self.tree.tag_configure('present', foreground="#27ae60")
        self.tree.tag_configure('absent', foreground="#e74c3c")
        self.tree.tag_configure('late', foreground="#f39c12")

        # --- 6. Pagination Controls ---
        pagination_frame = tk.Frame(main_container, bg='#f5f6fa')
        pagination_frame.pack(fill=tk.X)

        # Left side - Records info
        self.records_label = tk.Label(
            pagination_frame, 
            text="Showing 0 of 0 records", 
            font=("Segoe UI", 10),
            bg='#f5f6fa',
            fg="#2c3e50"
        )
        self.records_label.pack(side=tk.LEFT)

        # Right side - Pagination buttons
        pagination_controls = tk.Frame(pagination_frame, bg='#f5f6fa')
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
            bg='#f5f6fa',
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
            bg='#f5f6fa',
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

    def get_filtered_logs(self):
        """Get logs with filters applied"""
        try:
            # Build the base query
            query = """
                SELECT 
                    e.first_name, e.last_name, e.department,
                    a.date, a.clock_in, a.clock_out, a.status
                FROM attendance a
                JOIN employees e ON a.employee_id = e.id
                WHERE 1=1
            """
            params = []

            # Apply search filter
            search = self.search_entry.get().strip()
            if search:
                query += " AND (e.first_name LIKE %s OR e.last_name LIKE %s)"
                params.extend([f"%{search}%", f"%{search}%"])

            # Apply department filter
            selected_depts = [dept for dept, var in self.dept_vars.items() if var.get()]
            if selected_depts and len(selected_depts) < len(self.dept_vars):  # Only filter if not all selected
                placeholders = ','.join(['%s'] * len(selected_depts))
                query += f" AND e.department IN ({placeholders})"
                params.extend(selected_depts)

            # Apply date range filter
            try:
                if HAS_CALENDAR:
                    start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
                    end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
                else:
                    start_date = self.start_date_entry.get().strip()
                    end_date = self.end_date_entry.get().strip()
                
                if start_date:
                    query += " AND a.date >= %s"
                    params.append(start_date)
                if end_date:
                    query += " AND a.date <= %s"
                    params.append(end_date)
            except Exception as e:
                print(f"Date filter error: {e}")

            query += " ORDER BY a.date DESC, a.clock_in DESC"

            # Get total count for pagination
            count_query = f"SELECT COUNT(*) as total FROM ({query}) as filtered"
            count_result = self.db.execute_query(count_query, tuple(params), fetch=True)
            self.total_records = count_result[0]['total'] if count_result else 0
            self.total_pages = max(1, (self.total_records + self.records_per_page - 1) // self.records_per_page)

            # Add pagination
            offset = (self.current_page - 1) * self.records_per_page
            query += f" LIMIT %s OFFSET %s"
            params.extend([self.records_per_page, offset])

            return self.db.execute_query(query, tuple(params), fetch=True) or []

        except Exception as e:
            print(f"Error getting filtered logs: {e}")
            import traceback
            traceback.print_exc()
            return []

    def load_data(self):
        """Load data into the table"""
        # Clear current data
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            logs = self.get_filtered_logs()
            
            if not logs:
                # Show "No records found" message
                self.tree.insert("", tk.END, values=("No records found", "", "", "", "", ""), tags=('oddrow',))
            else:
                count = 0
                for log in logs:
                    full_name = f"{log['first_name']} {log['last_name']}"
                    clock_in = self.format_time(log.get('clock_in'))
                    clock_out = self.format_time(log.get('clock_out'))
                    status = str(log.get('status', 'absent')).upper()

                    values = (
                        full_name,
                        log.get('department', 'N/A'),
                        str(log.get('date', '')),
                        clock_in,
                        clock_out,
                        status
                    )

                    row_tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                    
                    # Add status color tag
                    tags = [row_tag]
                    if status.lower() == 'present':
                        tags.append('present')
                    elif status.lower() == 'absent':
                        tags.append('absent')
                    elif status.lower() == 'late':
                        tags.append('late')
                    
                    self.tree.insert("", tk.END, values=values, tags=tuple(tags))
                    count += 1

            self.update_pagination_controls()
                
        except Exception as e:
            print(f"Error loading logs: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load attendance logs: {str(e)}")

    def update_pagination_controls(self):
        """Update pagination labels and button states"""
        # Update records label
        start_record = (self.current_page - 1) * self.records_per_page + 1
        end_record = min(self.current_page * self.records_per_page, self.total_records)
        
        if self.total_records == 0:
            self.records_label.config(text="No records found")
        else:
            self.records_label.config(text=f"Showing {start_record}-{end_record} of {self.total_records} records")

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
        
        # Reset dates
        if HAS_CALENDAR:
            self.start_date_entry.set_date(datetime.now() - timedelta(days=30))
            self.end_date_entry.set_date(datetime.now())
        else:
            self.start_date_entry.delete(0, tk.END)
            self.start_date_entry.insert(0, (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'))
            self.end_date_entry.delete(0, tk.END)
            self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        self.current_page = 1
        self.load_data()

    def export_logs(self):
        """Export filtered logs to CSV"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"attendance_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if filename:
                # Get all filtered logs without pagination
                query = """
                    SELECT 
                        e.first_name, e.last_name, e.department,
                        a.date, a.clock_in, a.clock_out, a.status
                    FROM attendance a
                    JOIN employees e ON a.employee_id = e.id
                    WHERE 1=1
                """
                params = []

                # Apply same filters
                search = self.search_entry.get().strip()
                if search:
                    query += " AND (e.first_name LIKE %s OR e.last_name LIKE %s)"
                    params.extend([f"%{search}%", f"%{search}%"])

                selected_depts = [dept for dept, var in self.dept_vars.items() if var.get()]
                if selected_depts and len(selected_depts) < len(self.dept_vars):
                    placeholders = ','.join(['%s'] * len(selected_depts))
                    query += f" AND e.department IN ({placeholders})"
                    params.extend(selected_depts)

                try:
                    if HAS_CALENDAR:
                        start_date = self.start_date_entry.get_date().strftime('%Y-%m-%d')
                        end_date = self.end_date_entry.get_date().strftime('%Y-%m-%d')
                    else:
                        start_date = self.start_date_entry.get().strip()
                        end_date = self.end_date_entry.get().strip()
                    
                    if start_date:
                        query += " AND a.date >= %s"
                        params.append(start_date)
                    if end_date:
                        query += " AND a.date <= %s"
                        params.append(end_date)
                except:
                    pass

                query += " ORDER BY a.date DESC, a.clock_in DESC"
                
                logs = self.db.execute_query(query, tuple(params), fetch=True) or []
                
                with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Employee Name', 'Department', 'Date', 'Clock In', 'Clock Out', 'Status'])
                    
                    for log in logs:
                        full_name = f"{log['first_name']} {log['last_name']}"
                        clock_in = self.format_time(log.get('clock_in'))
                        clock_out = self.format_time(log.get('clock_out'))
                        
                        writer.writerow([
                            full_name,
                            log.get('department', 'N/A'),
                            str(log.get('date', '')),
                            clock_in,
                            clock_out,
                            str(log.get('status', 'absent')).upper()
                        ])
                
                messagebox.showinfo("Success", f"Exported {len(logs)} records to:\n{filename}")
                
        except Exception as e:
            print(f"Export error: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to export: {str(e)}")

    def format_time(self, time_obj):
        """Helper to convert Military Time/Objects to Standard AM/PM"""
        if not time_obj:
            return "---"
            
        if hasattr(time_obj, 'strftime'):
            return time_obj.strftime("%I:%M %p")
        
        raw_str = str(time_obj)
        try:
            # Handle timedelta objects
            if 'day' in raw_str:
                return raw_str
            # Try parsing as time
            t_obj = datetime.strptime(raw_str, "%H:%M:%S")
            return t_obj.strftime("%I:%M %p")
        except:
            return raw_str