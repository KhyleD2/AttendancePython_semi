# hr_dashboard.py
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from database import Database
from config import COLORS

class HRDashboard:
    def __init__(self, user_data):
        self.window = tk.Tk()
        self.window.title("HR Manager Dashboard - Attendance System")
        self.window.geometry("1200x700")
        self.window.configure(bg=COLORS['bg_main'])
        
        self.user_data = user_data
        self.db = Database()
        self.db.connect()
        
        self.employee = self.db.get_employee_by_id(user_data['employee_id'])
        
        self.setup_ui()
        self.show_dashboard()
        
    def setup_ui(self):
        # Top Header
        header = tk.Frame(self.window, bg=COLORS['secondary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="HR Manager Dashboard", 
                font=("Arial", 18, "bold"),
                bg=COLORS['secondary'], 
                fg="white").pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Label(header, text=f"Welcome, {self.employee['first_name']} {self.employee['last_name']}", 
                font=("Arial", 11),
                bg=COLORS['secondary'], 
                fg="white").pack(side=tk.RIGHT, padx=30)
        
        # Main Container
        main_container = tk.Frame(self.window, bg=COLORS['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main_container, bg=COLORS['bg_white'], width=220)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        sidebar.config(highlightbackground=COLORS['border'], highlightthickness=1)
        
        tk.Label(sidebar, text="", bg=COLORS['bg_white']).pack(pady=10)
        
        # Menu Buttons
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("👥 All Employees", self.show_employees),
            ("📋 Attendance Logs", self.show_attendance_logs),
            ("📈 Reports", self.show_reports),
            ("⏰ My Attendance", self.show_my_attendance),
            ("🚪 Logout", self.logout)
        ]
        
        for text, command in menu_items:
            btn = tk.Button(sidebar, text=text, 
                          font=("Arial", 11),
                          bg=COLORS['bg_white'], 
                          fg=COLORS['text_dark'], 
                          command=command,
                          cursor="hand2", 
                          relief=tk.FLAT, 
                          anchor=tk.W, 
                          padx=20, 
                          pady=12,
                          activebackground=COLORS['hover'])
            btn.pack(fill=tk.X, pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=COLORS['hover']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=COLORS['bg_white']))
        
        # Content Area
        self.content_frame = tk.Frame(main_container, bg=COLORS['bg_main'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="HR Dashboard Overview", 
                font=("Arial", 22, "bold"), 
                fg=COLORS['text_dark'], 
                bg=COLORS['bg_main']).pack(anchor=tk.W, pady=(0, 20))
        
        # Stats Cards
        stats_container = tk.Frame(self.content_frame, bg=COLORS['bg_main'])
        stats_container.pack(fill=tk.X, pady=(0, 30))
        
        stats = self.db.get_dashboard_stats()
        
        cards_data = [
            ("Total Employees", stats['total_employees'], COLORS['primary'], "👥"),
            ("Present Today", stats['present_today'], COLORS['success'], "✓"),
            ("Absent Today", stats['absent_today'], COLORS['danger'], "✗"),
            ("Total Users", stats['total_users'], COLORS['secondary'], "👤")
        ]
        
        for i, (title, value, color, icon) in enumerate(cards_data):
            card = tk.Frame(stats_container, bg=COLORS['bg_white'], 
                          highlightbackground=COLORS['border'], 
                          highlightthickness=1)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            stats_container.columnconfigure(i, weight=1)
            
            card_inner = tk.Frame(card, bg=COLORS['bg_white'])
            card_inner.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            tk.Label(card_inner, text=icon, 
                    font=("Arial", 28), 
                    fg=color, 
                    bg=COLORS['bg_white']).pack()
            
            tk.Label(card_inner, text=str(value), 
                    font=("Arial", 32, "bold"),
                    fg=color, 
                    bg=COLORS['bg_white']).pack(pady=(5, 0))
            
            tk.Label(card_inner, text=title, 
                    font=("Arial", 11),
                    fg=COLORS['text_gray'], 
                    bg=COLORS['bg_white']).pack()
        
        # Recent Attendance
        tk.Label(self.content_frame, text="Recent Attendance Activity", 
                font=("Arial", 16, "bold"), 
                fg=COLORS['text_dark'], 
                bg=COLORS['bg_main']).pack(anchor=tk.W, pady=(20, 15))
        
        table_container = tk.Frame(self.content_frame, bg=COLORS['bg_white'],
                                  highlightbackground=COLORS['border'], 
                                  highlightthickness=1)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Employee", "Department", "Date", "Clock In", "Clock Out", "Status")
        
        tree = ttk.Treeview(table_container, columns=columns, show="headings", height=12)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                       background=COLORS['bg_white'],
                       foreground=COLORS['text_dark'],
                       fieldbackground=COLORS['bg_white'])
        style.configure("Treeview.Heading", 
                       background=COLORS['secondary'],
                       foreground="white",
                       font=("Arial", 10, "bold"))
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        logs = self.db.get_attendance_logs(limit=20)
        for log in logs:
            clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "Active"
            tree.insert("", tk.END, values=(
                f"{log['first_name']} {log['last_name']}",
                log['department'] or "N/A",
                log['date'],
                log['clock_in'].strftime("%I:%M %p"),
                clock_out,
                log['status'].upper()
            ))
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
    
    def show_employees(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="All Employees", 
                font=("Arial", 22, "bold"), 
                fg=COLORS['text_dark'], 
                bg=COLORS['bg_main']).pack(anchor=tk.W, pady=(0, 20))
        
        table_container = tk.Frame(self.content_frame, bg=COLORS['bg_white'],
                                  highlightbackground=COLORS['border'], 
                                  highlightthickness=1)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Name", "Email", "Phone", "Department", "Position", "Hire Date")
        tree = ttk.Treeview(table_container, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        employees = self.db.get_all_employees()
        for emp in employees:
            tree.insert("", tk.END, values=(
                emp['id'],
                f"{emp['first_name']} {emp['last_name']}",
                emp['email'],
                emp['phone'] or "N/A",
                emp['department'] or "N/A",
                emp['position'] or "N/A",
                emp['hire_date']
            ))
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
    
    def show_attendance_logs(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="Attendance Logs", 
                font=("Arial", 22, "bold"), 
                fg=COLORS['text_dark'], 
                bg=COLORS['bg_main']).pack(anchor=tk.W, pady=(0, 20))
        
        table_container = tk.Frame(self.content_frame, bg=COLORS['bg_white'],
                                  highlightbackground=COLORS['border'], 
                                  highlightthickness=1)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ("ID", "Employee", "Department", "Date", "Clock In", "Clock Out", "Status")
        tree = ttk.Treeview(table_container, columns=columns, show="headings", height=20)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        logs = self.db.get_attendance_logs()
        for log in logs:
            clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "Active"
            tree.insert("", tk.END, values=(
                log['id'],
                f"{log['first_name']} {log['last_name']}",
                log['department'] or "N/A",
                log['date'],
                log['clock_in'].strftime("%I:%M %p"),
                clock_out,
                log['status'].upper()
            ))
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
    
    def show_reports(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="HR Reports & Analytics", 
                font=("Arial", 22, "bold"), 
                fg=COLORS['text_dark'], 
                bg=COLORS['bg_main']).pack(anchor=tk.W, pady=(0, 20))
        
        report_container = tk.Frame(self.content_frame, bg=COLORS['bg_white'],
                                   highlightbackground=COLORS['border'], 
                                   highlightthickness=1)
        report_container.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
        
        stats = self.db.get_dashboard_stats()
        
        stats_frame = tk.Frame(report_container, bg=COLORS['bg_white'])
        stats_frame.pack(pady=40, padx=40)
        
        report_data = [
            ("Total Employees", stats['total_employees']),
            ("Present Today", stats['present_today']),
            ("Absent Today", stats['absent_today']),
            ("Attendance Rate", f"{(stats['present_today']/stats['total_employees']*100) if stats['total_employees'] > 0 else 0:.1f}%"),
            ("Total System Users", stats['total_users'])
        ]
        
        for i, (label, value) in enumerate(report_data):
            tk.Label(stats_frame, text=f"{label}:", 
                    font=("Arial", 13, "bold"),
                    fg=COLORS['text_dark'], 
                    bg=COLORS['bg_white']).grid(row=i, column=0, sticky=tk.W, pady=15, padx=(0, 40))
            
            tk.Label(stats_frame, text=str(value), 
                    font=("Arial", 13),
                    fg=COLORS['secondary'], 
                    bg=COLORS['bg_white']).grid(row=i, column=1, sticky=tk.W, pady=15)
    
    def show_my_attendance(self):
        self.clear_content()
        
        tk.Label(self.content_frame, text="My Attendance Clock In/Out", 
                font=("Arial", 22, "bold"), 
                fg=COLORS['text_dark'], 
                bg=COLORS['bg_main']).pack(anchor=tk.W, pady=(0, 20))
        
        clock_container = tk.Frame(self.content_frame, bg=COLORS['bg_white'],
                                  highlightbackground=COLORS['border'], 
                                  highlightthickness=1)
        clock_container.pack(fill=tk.BOTH, expand=True)
        
        clock_frame = tk.Frame(clock_container, bg=COLORS['bg_white'])
        clock_frame.pack(expand=True, pady=40)
        
        self.time_label = tk.Label(clock_frame, text="", 
                                   font=("Arial", 48, "bold"),
                                   fg=COLORS['secondary'], 
                                   bg=COLORS['bg_white'])
        self.time_label.pack(pady=(0, 10))
        
        self.date_label = tk.Label(clock_frame, text="", 
                                   font=("Arial", 14),
                                   fg=COLORS['text_gray'], 
                                   bg=COLORS['bg_white'])
        self.date_label.pack(pady=(0, 30))
        
        self.update_time()
        
        today_status = self.db.get_today_attendance_status(self.employee['id'])
        
        if today_status:
            if today_status['clock_out']:
                status_text = "✓ You have completed your attendance for today"
                status_color = COLORS['success']
                btn_text = "Already Clocked Out"
                btn_state = "disabled"
                btn_color = COLORS['text_gray']
                btn_command = None
            else:
                clock_in_time = today_status['clock_in'].strftime("%I:%M %p")
                status_text = f"⏰ Clocked In at {clock_in_time}"
                status_color = COLORS['warning']
                btn_text = "CLOCK OUT"
                btn_state = "normal"
                btn_color = COLORS['danger']
                btn_command = self.clock_out
        else:
            status_text = "Ready to clock in"
            status_color = COLORS['secondary']
            btn_text = "CLOCK IN"
            btn_state = "normal"
            btn_color = COLORS['success']
            btn_command = self.clock_in
        
        tk.Label(clock_frame, text=status_text, 
                font=("Arial", 13),
                fg=status_color, 
                bg=COLORS['bg_white']).pack(pady=(0, 20))
        
        if btn_command:
            tk.Button(clock_frame, text=btn_text, 
                     font=("Arial", 13, "bold"),
                     bg=btn_color, 
                     fg="white",
                     cursor="hand2", 
                     relief=tk.FLAT,
                     command=btn_command,
                     state=btn_state,
                     padx=50, 
                     pady=15).pack()
        else:
            tk.Button(clock_frame, text=btn_text, 
                     font=("Arial", 13, "bold"),
                     bg=btn_color, 
                     fg="white",
                     relief=tk.FLAT,
                     state=btn_state,
                     padx=50, 
                     pady=15).pack()
    
    def update_time(self):
        now = datetime.now()
        current_time = now.strftime("%I:%M:%S %p")
        current_date = now.strftime("%A, %B %d, %Y")
        
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        
        self.time_label.after(1000, self.update_time)
    
    def clock_in(self):
        success, message = self.db.clock_in(self.employee['id'])
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_my_attendance()
        else:
            messagebox.showerror("Error", message)
    
    def clock_out(self):
        success, message = self.db.clock_out(self.employee['id'])
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_my_attendance()
        else:
            messagebox.showerror("Error", message)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.db.disconnect()
            self.window.destroy()
    
    def run(self):
        self.window.mainloop()