import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, date
from config import COLORS

class LeaveManagementView:
    def __init__(self, parent_frame, db):
        self.parent = parent_frame
        self.db = db
        self.current_filter = "Pending"
        
        self.setup_ui()
        self.load_leave_requests()
    
    def setup_ui(self):
        # Title
        title = tk.Label(self.parent, text="Leave Management", 
                        font=("Arial", 20, "bold"),
                        bg=COLORS['bg_main'], 
                        fg=COLORS['text_dark'])
        title.pack(pady=(0, 20))
        
        # Statistics Cards
        self.create_stats_cards()
        
        # Filter and Table
        self.create_leave_table()
    
    def create_stats_cards(self):
        """Create statistics cards showing leave counts"""
        stats_frame = tk.Frame(self.parent, bg=COLORS['bg_main'])
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Get statistics
        pending_count = len(self.db.get_pending_leave_requests())
        today = date.today().strftime("%Y-%m-%d")
        on_leave_today = len(self.db.get_leaves_for_date(today))
        
        # Pending Requests Card
        pending_card = tk.Frame(stats_frame, bg="#fff3cd", relief=tk.RAISED, bd=2)
        pending_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(pending_card, text="⏰", font=("Arial", 30),
                bg="#fff3cd").pack(pady=(15, 5))
        tk.Label(pending_card, text="Pending Requests",
                font=("Arial", 11), bg="#fff3cd",
                fg="#856404").pack()
        tk.Label(pending_card, text=str(pending_count),
                font=("Arial", 24, "bold"), bg="#fff3cd",
                fg="#856404").pack(pady=(5, 15))
        
        # On Leave Today Card
        leave_card = tk.Frame(stats_frame, bg="#d1ecf1", relief=tk.RAISED, bd=2)
        leave_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 0))
        
        tk.Label(leave_card, text="📅", font=("Arial", 30),
                bg="#d1ecf1").pack(pady=(15, 5))
        tk.Label(leave_card, text="On Leave Today",
                font=("Arial", 11), bg="#d1ecf1",
                fg="#0c5460").pack()
        tk.Label(leave_card, text=str(on_leave_today),
                font=("Arial", 24, "bold"), bg="#d1ecf1",
                fg="#0c5460").pack(pady=(5, 15))
    
    def create_leave_table(self):
        """Create the leave requests table with filters"""
        table_frame = tk.Frame(self.parent, bg=COLORS['bg_white'], 
                             relief=tk.RAISED, bd=1)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with Filter
        header_frame = tk.Frame(table_frame, bg=COLORS['bg_white'])
        header_frame.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header_frame, text="Leave Requests",
                font=("Arial", 14, "bold"),
                bg=COLORS['bg_white'],
                fg=COLORS['text_dark']).pack(side=tk.LEFT)
        
        # Filter Dropdown
        filter_frame = tk.Frame(header_frame, bg=COLORS['bg_white'])
        filter_frame.pack(side=tk.RIGHT)
        
        tk.Label(filter_frame, text="Filter:", 
                font=("Arial", 11),
                bg=COLORS['bg_white']).pack(side=tk.LEFT, padx=(0, 5))
        
        self.filter_var = tk.StringVar(value="Pending")
        filter_combo = ttk.Combobox(filter_frame,
                                   textvariable=self.filter_var,
                                   values=["All", "Pending", "Approved", "Rejected"],
                                   state="readonly",
                                   width=15,
                                   font=("Arial", 10))
        filter_combo.pack(side=tk.LEFT)
        filter_combo.bind("<<ComboboxSelected>>", lambda e: self.load_leave_requests())
        
        # Create Treeview
        tree_frame = tk.Frame(table_frame, bg=COLORS['bg_white'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Treeview
        self.tree = ttk.Treeview(tree_frame,
                                columns=("ID", "Employee", "Date", "Type", "Reason", "Status", "Submitted"),
                                show="headings",
                                yscrollcommand=vsb.set,
                                xscrollcommand=hsb.set,
                                height=12)
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Employee", text="Employee Name")
        self.tree.heading("Date", text="Leave Date")
        self.tree.heading("Type", text="Leave Type")
        self.tree.heading("Reason", text="Reason")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Submitted", text="Submitted On")
        
        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Employee", width=150, anchor=tk.W)
        self.tree.column("Date", width=100, anchor=tk.CENTER)
        self.tree.column("Type", width=120, anchor=tk.W)
        self.tree.column("Reason", width=200, anchor=tk.W)
        self.tree.column("Status", width=100, anchor=tk.CENTER)
        self.tree.column("Submitted", width=140, anchor=tk.CENTER)
        
        # Pack elements
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Configure tags for status colors
        self.tree.tag_configure('pending', background='#fff3cd')
        self.tree.tag_configure('approved', background='#d4edda')
        self.tree.tag_configure('rejected', background='#f8d7da')
        
        # Action Buttons
        action_frame = tk.Frame(table_frame, bg=COLORS['bg_white'])
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 15))
        
        approve_btn = tk.Button(action_frame, text="✓ Approve Selected",
                              font=("Arial", 11, "bold"),
                              bg="#28a745",
                              fg="white",
                              command=self.approve_selected,
                              cursor="hand2",
                              relief=tk.FLAT,
                              padx=20,
                              pady=8)
        approve_btn.pack(side=tk.LEFT, padx=(0, 10))
        approve_btn.bind("<Enter>", lambda e: approve_btn.config(bg="#218838"))
        approve_btn.bind("<Leave>", lambda e: approve_btn.config(bg="#28a745"))
        
        reject_btn = tk.Button(action_frame, text="✗ Reject Selected",
                             font=("Arial", 11, "bold"),
                             bg="#dc3545",
                             fg="white",
                             command=self.reject_selected,
                             cursor="hand2",
                             relief=tk.FLAT,
                             padx=20,
                             pady=8)
        reject_btn.pack(side=tk.LEFT)
        reject_btn.bind("<Enter>", lambda e: reject_btn.config(bg="#c82333"))
        reject_btn.bind("<Leave>", lambda e: reject_btn.config(bg="#dc3545"))
        
        refresh_btn = tk.Button(action_frame, text="🔄 Refresh",
                              font=("Arial", 11),
                              bg=COLORS['primary'],
                              fg="white",
                              command=self.load_leave_requests,
                              cursor="hand2",
                              relief=tk.FLAT,
                              padx=20,
                              pady=8)
        refresh_btn.pack(side=tk.RIGHT)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#0056b3"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg=COLORS['primary']))
    
    def load_leave_requests(self):
        """Load leave requests based on selected filter"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Get filter value
        filter_val = self.filter_var.get()
        
        # Get data from database
        if filter_val == "All":
            requests = self.db.get_all_leave_requests()
        elif filter_val == "Pending":
            requests = self.db.get_pending_leave_requests()
        elif filter_val == "Approved":
            requests = self.db.get_approved_leave_requests()
        else:  # Rejected
            requests = self.db.get_rejected_leave_requests()
        
        if not requests:
            self.tree.insert("", tk.END, values=("", "No leave requests found", "", "", "", "", ""))
            return
        
        # Populate table
        for req in requests:
            # Truncate long reasons
            reason = req['reason']
            if len(reason) > 40:
                reason = reason[:37] + "..."
            
            # Determine tag based on status
            status = req['status']
            tag = status.lower()
            
            self.tree.insert("", tk.END, 
                           values=(
                               req['id'],
                               req['employee_name'],
                               req['leave_date'],
                               req['leave_type'],
                               reason,
                               status,
                               req['created_at']
                           ),
                           tags=(tag,))
    
    def approve_selected(self):
        """Approve the selected leave request"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a leave request to approve")
            return
        
        # Get the leave request ID
        item = self.tree.item(selected[0])
        leave_id = item['values'][0]
        employee_name = item['values'][1]
        status = item['values'][5]
        
        if status != "Pending":
            messagebox.showinfo("Info", "Only pending requests can be approved")
            return
        
        # Confirm action
        if not messagebox.askyesno("Confirm Approval", 
                                   f"Approve leave request for {employee_name}?"):
            return
        
        # Approve in database (admin_id = 1 for now, you can pass actual admin ID)
        success = self.db.approve_leave_request(leave_id, admin_id=1)
        
        if success:
            messagebox.showinfo("Success", "Leave request approved successfully!")
            self.load_leave_requests()
            # Refresh stats
            self.refresh_stats()
        else:
            messagebox.showerror("Error", "Failed to approve leave request")
    
    def reject_selected(self):
        """Reject the selected leave request"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a leave request to reject")
            return
        
        # Get the leave request ID
        item = self.tree.item(selected[0])
        leave_id = item['values'][0]
        employee_name = item['values'][1]
        status = item['values'][5]
        
        if status != "Pending":
            messagebox.showinfo("Info", "Only pending requests can be rejected")
            return
        
        # Confirm action
        if not messagebox.askyesno("Confirm Rejection", 
                                   f"Reject leave request for {employee_name}?"):
            return
        
        # Reject in database (admin_id = 1 for now)
        success = self.db.reject_leave_request(leave_id, admin_id=1, rejection_reason="Rejected by admin")
        
        if success:
            messagebox.showinfo("Success", "Leave request rejected successfully!")
            self.load_leave_requests()
            # Refresh stats
            self.refresh_stats()
        else:
            messagebox.showerror("Error", "Failed to reject leave request")
    
    def refresh_stats(self):
        """Refresh the statistics cards"""
        # Destroy and recreate stats
        for widget in self.parent.winfo_children():
            if isinstance(widget, tk.Frame) and widget != self.parent.winfo_children()[-1]:
                widget.destroy()
                break
        self.create_stats_cards()