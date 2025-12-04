# admin_dashboard.py (MAIN FILE - Entry Point)
import tkinter as tk
from tkinter import messagebox
from database import Database
from config import COLORS

# Import separate modules from admin folder
from admin.dashboard_view import DashboardView
from admin.attendance_logs import AttendanceLogsView
from admin.employees_view import EmployeesView
from admin.create_employee_view import CreateEmployeeView
from admin.create_hr_view import CreateHRView
from admin.reports_view import ReportsView
from admin.leave_management_view import LeaveManagementView
from admin.settings_view import SettingsView
from admin.late_fee_management_view import LateFeeManagementView  # <--- NEW IMPORT

class AdminDashboard:
    def __init__(self, user_data):
        self.window = tk.Tk()
        self.window.title("Admin Dashboard - Attendance System")
        self.window.geometry("1200x700")
        self.window.configure(bg=COLORS['bg_main'])
        
        self.user_data = user_data
        self.db = Database()
        self.db.connect()
        
        self.setup_ui()
        self.show_dashboard()
        
    def setup_ui(self):
        # Top Header
        header = tk.Frame(self.window, bg=COLORS['primary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Admin Dashboard", 
                font=("Arial", 18, "bold"),
                bg=COLORS['primary'], 
                fg="white").pack(side=tk.LEFT, padx=30, pady=20)
        
        tk.Label(header, text=f"Welcome, {self.user_data['username']}", 
                font=("Arial", 11),
                bg=COLORS['primary'], 
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
        
        # Menu Items - Added Late Fees here
        menu_items = [
            ("📊 Dashboard", self.show_dashboard),
            ("📋 Attendance Logs", self.show_attendance_logs),
            ("💰 Late Fees", self.show_late_fees_management),  # <--- NEW BUTTON
            ("👥 Employees", self.show_employees),
            ("📝 Leave Requests", self.show_leave_requests),
            ("📈 Reports", self.show_reports),
            ("⚙ Settings", self.show_settings),
            ("➕ Create Employee", self.show_create_employee),
            ("👔 Create HR Manager", self.show_create_hr),
        ]
        
        # Create Menu Buttons
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
        
        # Spacer
        spacer = tk.Frame(sidebar, bg=COLORS['bg_white'])
        spacer.pack(fill=tk.BOTH, expand=True)
        
        # Logout Button
        logout_btn = tk.Button(sidebar, text="🚪 Logout", 
                             font=("Arial", 11, "bold"),
                             bg="#e74c3c", 
                             fg="white", 
                             command=self.logout,
                             cursor="hand2", 
                             relief=tk.FLAT, 
                             anchor=tk.W, 
                             padx=20, 
                             pady=12,
                             activebackground="#c0392b")
        logout_btn.pack(fill=tk.X, pady=2, side=tk.BOTTOM)
        logout_btn.bind("<Enter>", lambda e, b=logout_btn: b.config(bg="#c0392b"))
        logout_btn.bind("<Leave>", lambda e, b=logout_btn: b.config(bg="#e74c3c"))
        
        # Content Area
        self.content_frame = tk.Frame(main_container, bg=COLORS['bg_main'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
    def clear_content(self):
        """Clear all widgets from content frame"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def show_dashboard(self):
        """Display Dashboard Overview"""
        self.clear_content()
        DashboardView(self.content_frame, self.db)
    
    def show_attendance_logs(self):
        """Display Attendance Logs"""
        self.clear_content()
        AttendanceLogsView(self.content_frame, self.db)

    def show_late_fees_management(self):  # <--- NEW FUNCTION
        """Display Late Fee Management View"""
        self.clear_content()
        LateFeeManagementView(self.content_frame, self.db)
    
    def show_employees(self):
        """Display All Employees"""
        self.clear_content()
        EmployeesView(self.content_frame, self.db)
    
    def show_leave_requests(self):
        """Display Leave Requests Management"""
        self.clear_content()
        LeaveManagementView(self.content_frame, self.db)
    
    def show_reports(self):
        """Display Reports & Analytics"""
        self.clear_content()
        ReportsView(self.content_frame, self.db)

    def show_settings(self):
        """Display Settings View"""
        self.clear_content()
        SettingsView(self.content_frame, self.db)
    
    def show_create_employee(self):
        """Display Create Employee Form"""
        self.clear_content()
        CreateEmployeeView(self.content_frame, self.db)
    
    def show_create_hr(self):
        """Display Create HR Manager Form"""
        self.clear_content()
        CreateHRView(self.content_frame, self.db)

    def logout(self):
        """Logout and close application"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.db.disconnect()
            self.window.destroy()
    
    def run(self):
        """Run the admin dashboard"""
        self.window.mainloop()