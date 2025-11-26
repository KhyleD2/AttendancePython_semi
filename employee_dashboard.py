# employee_dashboard.py
import tkinter as tk
from tkinter import messagebox
from database import Database
from config import COLORS
from employee.dashboard_view import DashboardView
from employee.attendance_view import AttendanceView
from employee.reports_view import ReportsView
from employee.leave_request_view import LeaveRequestView  # NEW IMPORT

class EmployeeDashboard:
    def __init__(self, user_data):
        self.window = tk.Tk()
        self.window.title("Employee Dashboard - Attendance System")
        self.window.geometry("1100x650")
        self.window.configure(bg=COLORS['bg_main'])
        
        self.user_data = user_data
        self.db = Database()
        self.db.connect()
        
        self.employee = self.db.get_employee_by_id(user_data['employee_id'])
        
        self.setup_ui()
        self.show_dashboard()
        
    def setup_ui(self):
        # Top Header
        header = tk.Frame(self.window, bg=COLORS['success'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Employee Dashboard", 
                font=("Arial", 18, "bold"),
                bg=COLORS['success'], 
                fg="white").pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Label(header, text=f"Welcome, {self.employee['first_name']} {self.employee['last_name']}", 
                font=("Arial", 11),
                bg=COLORS['success'], 
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
        
        # Menu Buttons (without Logout)
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("⏰ Clock In/Out", self.show_attendance),
            ("📝 Leave Request", self.show_leave_request),  # NEW MENU ITEM
            ("📈 My Reports", self.show_reports),
        ]
        
        # Regular menu items
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
        
        # Spacer to push logout to bottom
        spacer = tk.Frame(sidebar, bg=COLORS['bg_white'])
        spacer.pack(fill=tk.BOTH, expand=True)
        
        # Logout Button - Red at bottom
        logout_btn = tk.Button(sidebar, text="🚪 Logout", 
                              font=("Arial", 11, "bold"),
                              bg="#e74c3c",  # Red color
                              fg="white", 
                              command=self.logout,
                              cursor="hand2", 
                              relief=tk.FLAT, 
                              anchor=tk.W, 
                              padx=20, 
                              pady=12,
                              activebackground="#c0392b")  # Darker red on hover
        logout_btn.pack(fill=tk.X, pady=2, side=tk.BOTTOM)
        logout_btn.bind("<Enter>", lambda e, b=logout_btn: b.config(bg="#c0392b"))
        logout_btn.bind("<Leave>", lambda e, b=logout_btn: b.config(bg="#e74c3c"))
        
        # Content Area
        self.content_frame = tk.Frame(main_container, bg=COLORS['bg_main'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        self.clear_content()
        DashboardView(self.content_frame, self.db, self.employee)
    
    def show_attendance(self):
        self.clear_content()
        AttendanceView(self.content_frame, self.db, self.employee)
    
    def show_leave_request(self):
        """Display Leave Request Form - NEW METHOD"""
        self.clear_content()
        LeaveRequestView(self.content_frame, self.db, self.employee)
    
    def show_reports(self):
        self.clear_content()
        ReportsView(self.content_frame, self.db, self.employee)
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.db.disconnect()
            self.window.destroy()
    
    def run(self):
        self.window.mainloop()