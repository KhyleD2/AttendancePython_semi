import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from config import COLORS

class LeaveRequestView:
    def __init__(self, parent_frame, db, employee):
        self.parent = parent_frame
        self.db = db
        self.employee = employee
        
        self.setup_ui()
        self.load_leave_requests()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.parent, text="Leave Request", 
                        font=("Arial", 20, "bold"),
                        bg=COLORS['bg_main'], 
                        fg=COLORS['text_dark'])
        title.pack(pady=(0, 20))
        
        # Statistics Cards
        self.create_stats_cards()
        
        # Create Leave Request Form
        self.create_leave_form()
        
        # Leave Requests History Table
        self.create_history_table()
    
    def create_stats_cards(self):
        """Create statistics cards showing leave summary"""
        stats_frame = tk.Frame(self.parent, bg=COLORS['bg_main'])
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get statistics
        current_year = datetime.now().year
        total_leaves = self.db.get_employee_leave_count(self.employee['id'], current_year)
        pending_requests = len([r for r in self.db.get_employee_leave_requests(self.employee['id']) 
                               if r['status'] == 'Pending'])
        
        # Total Leaves This Year Card
        total_card = tk.Frame(stats_frame, bg="#d1ecf1", relief=tk.RAISED, bd=2)
        total_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(total_card, text="📅", font=("Arial", 30),
                bg="#d1ecf1").pack(pady=(15, 5))
        tk.Label(total_card, text=f"Total Leaves {current_year}",
                font=("Arial", 11), bg="#d1ecf1",
                fg="#0c5460").pack()
        tk.Label(total_card, text=str(total_leaves),
                font=("Arial", 24, "bold"), bg="#d1ecf1",
                fg="#0c5460").pack(pady=(5, 15))
        
        # Pending Requests Card
        pending_card = tk.Frame(stats_frame, bg="#fff3cd", relief=tk.RAISED, bd=2)
        pending_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))
        
        tk.Label(pending_card, text="⏰", font=("Arial", 30),
                bg="#fff3cd").pack(pady=(15, 5))
        tk.Label(pending_card, text="Pending Requests",
                font=("Arial", 11), bg="#fff3cd",
                fg="#856404").pack()
        tk.Label(pending_card, text=str(pending_requests),
                font=("Arial", 24, "bold"), bg="#fff3cd",
                fg="#856404").pack(pady=(5, 15))
    
    def create_leave_form(self):
        """Create the leave request submission form"""
        form_frame = tk.Frame(self.parent, bg=COLORS['bg_white'], 
                            relief=tk.RAISED, bd=1)
        form_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Form Title
        header_frame = tk.Frame(form_frame, bg=COLORS['bg_white'])
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header_frame, text="Submit New Leave Request",
                font=("Arial", 14, "bold"),
                bg=COLORS['bg_white'],
                fg=COLORS['text_dark']).pack(side=tk.LEFT)
        
        # Form Fields Container - Horizontal Layout
        fields_container = tk.Frame(form_frame, bg=COLORS['bg_white'])
        fields_container.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        # Left Column - Date and Type
        left_col = tk.Frame(fields_container, bg=COLORS['bg_white'])
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Leave Date
        tk.Label(left_col, text="Leave Date *", 
                font=("Arial", 10, "bold"),
                bg=COLORS['bg_white'],
                fg=COLORS['text_dark']).pack(anchor=tk.W, pady=(0, 5))
        self.date_entry = tk.Entry(left_col, font=("Arial", 11), 
                                   relief=tk.SOLID, bd=1)
        self.date_entry.pack(fill=tk.X, pady=(0, 10), ipady=6)
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.date_entry.config(fg='gray')
        self.date_entry.bind('<FocusIn>', self.clear_date_placeholder)
        self.date_entry.bind('<FocusOut>', self.restore_date_placeholder)
        
        # Leave Type
        tk.Label(left_col, text="Leave Type *", 
                font=("Arial", 10, "bold"),
                bg=COLORS['bg_white'],
                fg=COLORS['text_dark']).pack(anchor=tk.W, pady=(0, 5))
        self.leave_type = ttk.Combobox(left_col, 
                                      values=["Sick Leave", "Annual Leave", "Personal Leave", 
                                             "Emergency Leave", "Maternity Leave", "Paternity Leave"],
                                      font=("Arial", 11),
                                      state="readonly")
        self.leave_type.pack(fill=tk.X, ipady=6)
        self.leave_type.set("Sick Leave")
        
        # Right Column - Reason and Button
        right_col = tk.Frame(fields_container, bg=COLORS['bg_white'])
        right_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Reason
        tk.Label(right_col, text="Reason/Description *", 
                font=("Arial", 10, "bold"),
                bg=COLORS['bg_white'],
                fg=COLORS['text_dark']).pack(anchor=tk.W, pady=(0, 5))
        
        reason_frame = tk.Frame(right_col, bg=COLORS['bg_white'])
        reason_frame.pack(fill=tk.BOTH, expand=True)
        
        self.reason_text = tk.Text(reason_frame, font=("Arial", 11), 
                                  height=4, relief=tk.SOLID, bd=1,
                                  wrap=tk.WORD)
        reason_scrollbar = tk.Scrollbar(reason_frame, command=self.reason_text.yview)
        self.reason_text.config(yscrollcommand=reason_scrollbar.set)
        
        self.reason_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        reason_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Submit Button
        button_frame = tk.Frame(form_frame, bg=COLORS['bg_white'])
        button_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        submit_btn = tk.Button(button_frame, text="✓ Submit Leave Request",
                              font=("Arial", 11, "bold"),
                              bg="#28a745",
                              fg="white",
                              command=self.submit_leave_request,
                              cursor="hand2",
                              relief=tk.FLAT,
                              padx=20,
                              pady=10)
        submit_btn.pack(side=tk.LEFT)
        submit_btn.bind("<Enter>", lambda e: submit_btn.config(bg="#218838"))
        submit_btn.bind("<Leave>", lambda e: submit_btn.config(bg="#28a745"))
        
        refresh_btn = tk.Button(button_frame, text="🔄 Clear Form",
                               font=("Arial", 11),
                               bg=COLORS['primary'],
                               fg="white",
                               command=self.clear_form,
                               cursor="hand2",
                               relief=tk.FLAT,
                               padx=20,
                               pady=10)
        refresh_btn.pack(side=tk.LEFT, padx=(10, 0))
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#0056b3"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg=COLORS['primary']))
    
    def clear_date_placeholder(self, event):
        if self.date_entry.get() == "YYYY-MM-DD":
            self.date_entry.delete(0, tk.END)
            self.date_entry.config(fg='black')
    
    def restore_date_placeholder(self, event):
        if not self.date_entry.get():
            self.date_entry.insert(0, "YYYY-MM-DD")
            self.date_entry.config(fg='gray')
    
    def clear_form(self):
        """Clear all form fields"""
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, "YYYY-MM-DD")
        self.date_entry.config(fg='gray')
        self.leave_type.set("Sick Leave")
        self.reason_text.delete("1.0", tk.END)
    
    def create_history_table(self):
        """Create the leave requests history table"""
        history_frame = tk.Frame(self.parent, bg=COLORS['bg_white'], 
                               relief=tk.RAISED, bd=1)
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table Header
        header_frame = tk.Frame(history_frame, bg=COLORS['bg_white'])
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header_frame, text="My Leave Requests",
                font=("Arial", 14, "bold"),
                bg=COLORS['bg_white'],
                fg=COLORS['text_dark']).pack(side=tk.LEFT)
        
        refresh_btn = tk.Button(header_frame, text="🔄 Refresh",
                               font=("Arial", 10),
                               bg=COLORS['primary'],
                               fg="white",
                               command=self.load_leave_requests,
                               cursor="hand2",
                               relief=tk.FLAT,
                               padx=15,
                               pady=6)
        refresh_btn.pack(side=tk.RIGHT)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#0056b3"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg=COLORS['primary']))
        
        # Create Treeview
        tree_frame = tk.Frame(history_frame, bg=COLORS['bg_white'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame,
                                columns=("Date", "Type", "Reason", "Status", "Submitted"),
                                show="headings",
                                yscrollcommand=vsb.set,
                                xscrollcommand=hsb.set,
                                height=10)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("Date", text="Leave Date")
        self.tree.heading("Type", text="Leave Type")
        self.tree.heading("Reason", text="Reason")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Submitted", text="Submitted On")
        
        self.tree.column("Date", width=120, anchor=tk.CENTER)
        self.tree.column("Type", width=140, anchor=tk.W)
        self.tree.column("Reason", width=300, anchor=tk.W)
        self.tree.column("Status", width=120, anchor=tk.CENTER)
        self.tree.column("Submitted", width=180, anchor=tk.CENTER)
        
        # Pack elements
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure tags for status colors
        self.tree.tag_configure('pending', background='#fff3cd')
        self.tree.tag_configure('approved', background='#d4edda')
        self.tree.tag_configure('rejected', background='#f8d7da')
    
    def submit_leave_request(self):
        """Submit a new leave request"""
        # Get form values
        leave_date = self.date_entry.get()
        leave_type = self.leave_type.get()
        reason = self.reason_text.get("1.0", tk.END).strip()
        
        # Validate
        if leave_date == "YYYY-MM-DD" or not leave_date:
            messagebox.showerror("Error", "Please enter a valid leave date")
            return
        
        if not leave_type:
            messagebox.showerror("Error", "Please select a leave type")
            return
        
        if not reason:
            messagebox.showerror("Error", "Please provide a reason for your leave")
            return
        
        # Validate date format
        try:
            leave_date_obj = datetime.strptime(leave_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD")
            return
        
        # Check if date is in the future
        if leave_date_obj.date() < date.today():
            messagebox.showerror("Error", "Leave date cannot be in the past")
            return
        
        # Submit to database
        success = self.db.create_leave_request(
            self.employee['id'],
            leave_date,
            leave_type,
            reason
        )
        
        if success:
            messagebox.showinfo("Success", "Leave request submitted successfully!")
            self.clear_form()
            self.load_leave_requests()
            self.refresh_stats()
        else:
            messagebox.showerror("Error", "Failed to submit leave request")
    
    def load_leave_requests(self):
        """Load employee's leave requests into the table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get leave requests from database
        requests = self.db.get_employee_leave_requests(self.employee['id'])
        
        if not requests:
            # Show "No data" message
            self.tree.insert("", tk.END, values=("", "No leave requests found", "", "", ""))
            return
        
        # Populate table
        for req in requests:
            # Truncate long reasons
            reason = req['reason']
            if len(reason) > 50:
                reason = reason[:47] + "..."
            
            # Determine tag based on status
            status = req['status']
            tag = status.lower()
            
            self.tree.insert("", tk.END, 
                           values=(
                               req['leave_date'],
                               req['leave_type'],
                               reason,
                               status,
                               req['created_at']
                           ),
                           tags=(tag,))
    
    def refresh_stats(self):
        """Refresh the statistics cards"""
        # Find and destroy stats frame
        for widget in self.parent.winfo_children():
            if isinstance(widget, tk.Frame):
                # Check if it's the stats frame (second frame from top)
                children = self.parent.winfo_children()
                if children.index(widget) == 1:  # Stats frame is at index 1
                    widget.destroy()
                    break
        
        # Recreate stats at the correct position
        self.create_stats_cards()
        
        # Reorder widgets to maintain correct layout
        children = self.parent.winfo_children()
        if len(children) >= 2:
            children[1].pack_forget()
            children[1].pack(after=children[0], fill=tk.X, pady=(0, 20))