import tkinter as tk
from tkinter import ttk
from datetime import datetime
from config import COLORS

class AttendanceLogsView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.render()
    
    def render(self):
        # --- 1. Header Section ---
        header_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(header_frame, text="Attendance Logs", 
                 font=("Segoe UI", 24, "bold"), 
                 fg="#2c3e50", 
                 bg=COLORS['bg_main']).pack(side=tk.LEFT)

        # Refresh Button
        tk.Button(header_frame, text="↻ Refresh Logs", 
                  bg="#2980b9", fg="white", 
                  font=("Segoe UI", 10, "bold"), 
                  relief=tk.FLAT, padx=15, pady=5, cursor="hand2",
                  command=self.load_data).pack(side=tk.RIGHT)

        # --- 2. Table Container (Card Effect) ---
        container = tk.Frame(self.parent_frame, bg="white", padx=2, pady=2)
        container.pack(fill=tk.BOTH, expand=True)

        # --- 3. Style the Table ---
        style = ttk.Style()
        style.theme_use("clam")

        # Row Styling
        style.configure("Treeview",
                        background="white",
                        foreground="black",
                        rowheight=35,
                        fieldbackground="white",
                        font=("Segoe UI", 11))
        
        # Header Styling
        style.configure("Treeview.Heading",
                        background="#34495e", # Dark Slate Blue
                        foreground="white",
                        relief="flat",
                        font=("Segoe UI", 11, "bold"))
        
        # Selection Color
        style.map("Treeview", background=[('selected', '#3498db')])

        # --- 4. Create the Table ---
        scroll_y = tk.Scrollbar(container)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("name", "dept", "date", "in", "out", "status")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", yscrollcommand=scroll_y.set)
        
        # Define Headings
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

        # Adjust Column Widths
        self.tree.column("name", width=200)
        self.tree.column("dept", width=120)
        self.tree.column("date", width=100)
        self.tree.column("in", width=100)
        self.tree.column("out", width=100)
        self.tree.column("status", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True)
        scroll_y.config(command=self.tree.yview)

        # Define tags for stripes & status colors
        self.tree.tag_configure('oddrow', background="white")
        self.tree.tag_configure('evenrow', background="#f7f9fa")
        self.tree.tag_configure('present', foreground="#27ae60") # Green
        self.tree.tag_configure('absent', foreground="#c0392b")  # Red

        # Load Data
        self.load_data()

    def format_time(self, time_obj):
        """Helper to convert Military Time/Objects to Standard AM/PM"""
        if not time_obj:
            return "---"
            
        # If it's already a datetime/time object with formatting capabilities
        if hasattr(time_obj, 'strftime'):
            return time_obj.strftime("%I:%M %p")
        
        # If it's a string or timedelta (like "14:30:00")
        raw_str = str(time_obj)
        try:
            # Try parsing "HH:MM:SS" string
            t_obj = datetime.strptime(raw_str, "%H:%M:%S")
            return t_obj.strftime("%I:%M %p")
        except:
            # If parsing fails (maybe it's already formatted or different), return as is
            return raw_str

    def load_data(self):
        # Clear current data
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            logs = self.db.get_attendance_logs()
            
            count = 0
            for log in logs:
                # 1. Format Name
                full_name = f"{log['first_name']} {log['last_name']}"
                
                # 2. Format Times using the helper function
                clock_in = self.format_time(log['clock_in'])
                clock_out = self.format_time(log['clock_out'])

                # 3. Prepare Row
                values = (
                    full_name,
                    log['department'],
                    str(log['date']),
                    clock_in,
                    clock_out,
                    str(log['status']).upper()
                )

                # 4. Determine Stripe Color
                row_tag = 'evenrow' if count % 2 == 0 else 'oddrow'
                
                # Insert
                self.tree.insert("", tk.END, values=values, tags=(row_tag,))
                count += 1
                
        except Exception as e:
            print(f"Error loading logs: {e}")