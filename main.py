# main.py
"""
Employee Attendance Monitoring System - Light Theme
Main application entry point
"""

import sys
from login import LoginWindow
from admin_dashboard import AdminDashboard
from employee_dashboard import EmployeeDashboard
from hr_dashboard import HRDashboard
from config import ROLE_ADMIN, ROLE_EMPLOYEE, ROLE_HR

def main():
    """Main application loop"""
    
    print("=" * 60)
    print("   Employee Attendance Monitoring System")
    print("   Version 2.0 - Light Theme Edition")
    print("=" * 60)
    print("\nStarting application...")
    print("Make sure XAMPP MySQL is running!")
    print("-" * 60)
    
    while True:
        # Show login window
        login_window = LoginWindow()
        user_data = login_window.run()
        
        # If login was cancelled or failed
        if not user_data:
            print("\nApplication closed by user.")
            break
        
        print(f"\n✓ User logged in: {user_data['username']} (Role: {user_data['role']})")
        
        # Route to appropriate dashboard based on role
        try:
            if user_data['role'] == ROLE_ADMIN:
                print("Loading Admin Dashboard...")
                dashboard = AdminDashboard(user_data)
                dashboard.run()
                
            elif user_data['role'] == ROLE_EMPLOYEE:
                print("Loading Employee Dashboard...")
                dashboard = EmployeeDashboard(user_data)
                dashboard.run()
                
            elif user_data['role'] == ROLE_HR:
                print("Loading HR Manager Dashboard...")
                dashboard = HRDashboard(user_data)
                dashboard.run()
            
            print("\n✓ User logged out successfully.")
            
        except Exception as e:
            print(f"\n✗ Error occurred: {e}")
            import traceback
            traceback.print_exc()
            break
    
    print("\n" + "=" * 60)
    print("Thank you for using the Attendance System!")
    print("=" * 60)

if __name__ == "__main__":
    main()