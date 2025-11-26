import tkinter as tk
from tkinter import ttk
from config import COLORS

class ReportsView:
    def __init__(self, parent_frame, db, employee):
        self.parent_frame = parent_frame
        self.db = db
        self.employee = employee
        self.render()
    
    def render(self):
        tk.Label(self.parent_frame, text="My Attendance Reports", 
                font=("Arial", 22, "bold"), 
                fg=COLORS['text_dark'], 
                bg=COLORS['bg_main']).pack(anchor=tk.W, pady=(0, 20))
        
        # Table
        table_container = tk.Frame(self.parent_frame, bg=COLORS['bg_white'],
                                  highlightbackground=COLORS['border'], 
                                  highlightthickness=1)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Date", "Clock In", "Clock Out", "Status")
        tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background=COLORS['bg_white'],
                       foreground=COLORS['text_dark'],
                       fieldbackground=COLORS['bg_white'])
        style.configure("Treeview.Heading", 
                       background=COLORS['success'],
                       foreground="white",
                       font=("Arial", 10, "bold"))
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=200, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        logs = self.db.get_attendance_logs(employee_id=self.employee['id'])
        
        for log in logs:
            clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "Active"
            tree.insert("", tk.END, values=(
                log['date'],
                log['clock_in'].strftime("%I:%M %p"),
                clock_out,
                log['status'].upper()
            ))
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)