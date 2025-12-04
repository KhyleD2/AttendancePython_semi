import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG
from datetime import datetime, date, timedelta


class Database:
    def __init__(self):
        self.connection = None
        
    def connect(self):
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def disconnect(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def execute_query(self, query, params=None, fetch=False):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                last_id = cursor.lastrowid
                cursor.close()
                return last_id
        except Error as e:
            print(f"Database error: {e}")
            return None if fetch else False
    
    # User Authentication
    def authenticate_user(self, username, password):
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        result = self.execute_query(query, (username, password), fetch=True)
        return result[0] if result else None
    
    # --- Employee Operations ---
    def create_employee(self, first_name, last_name, email, phone, department, position, hire_date):
        query = """INSERT INTO employees (first_name, last_name, email, phone, department, position, hire_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)"""
        emp_id = self.execute_query(query, (first_name, last_name, email, phone, department, position, hire_date))
        return emp_id
    
    def update_employee(self, emp_id, first_name, last_name, email, phone, department, position, hire_date=None):
        if hire_date:
            query = """UPDATE employees 
                       SET first_name=%s, last_name=%s, email=%s, phone=%s, 
                           department=%s, position=%s, hire_date=%s
                       WHERE id=%s"""
            return self.execute_query(query, (first_name, last_name, email, phone, 
                                             department, position, hire_date, emp_id))
        else:
            query = """UPDATE employees 
                       SET first_name=%s, last_name=%s, email=%s, phone=%s, 
                           department=%s, position=%s
                       WHERE id=%s"""
            return self.execute_query(query, (first_name, last_name, email, phone, 
                                             department, position, emp_id))

    def delete_employee(self, emp_id):
        self.execute_query("DELETE FROM users WHERE employee_id=%s", (emp_id,))
        return self.execute_query("DELETE FROM employees WHERE id=%s", (emp_id,))

    def get_all_employees(self):
        query = "SELECT * FROM employees ORDER BY id DESC"
        return self.execute_query(query, fetch=True)
    
    def get_employee_by_id(self, employee_id):
        query = "SELECT * FROM employees WHERE id = %s"
        result = self.execute_query(query, (employee_id,), fetch=True)
        return result[0] if result else None
    
    # User Operations
    def create_user(self, username, password, role, employee_id=None):
        query = """INSERT INTO users (username, password, role, employee_id)
                   VALUES (%s, %s, %s, %s)"""
        return self.execute_query(query, (username, password, role, employee_id))
    
    def get_all_users(self):
        query = "SELECT u.*, e.first_name, e.last_name FROM users u LEFT JOIN employees e ON u.employee_id = e.id"
        return self.execute_query(query, fetch=True)
    
    # Manager Operations
    def create_manager(self, first_name, last_name, email, phone, username, password, role="HR"):
        query = """INSERT INTO managers (first_name, last_name, email, phone, username, password, role, created_at)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        return self.execute_query(query, (first_name, last_name, email, phone, username, password, role, datetime.now()))
    
    def get_all_managers(self):
        query = "SELECT * FROM managers ORDER BY created_at DESC"
        return self.execute_query(query, fetch=True)
    
    def get_manager_by_id(self, manager_id):
        query = "SELECT * FROM managers WHERE id = %s"
        result = self.execute_query(query, (manager_id,), fetch=True)
        return result[0] if result else None
    
    def delete_manager(self, manager_id):
        query = "DELETE FROM managers WHERE id = %s"
        return self.execute_query(query, (manager_id,))
    
    # Attendance Operations
    def clock_in(self, employee_id):
        today = date.today()
        check_query = "SELECT * FROM attendance WHERE employee_id = %s AND date = %s AND clock_out IS NULL"
        existing = self.execute_query(check_query, (employee_id, today), fetch=True)
        
        if existing:
            return False, "Already clocked in today"
        
        query = """INSERT INTO attendance (employee_id, clock_in, date, status)
                   VALUES (%s, %s, %s, 'present')"""
        result = self.execute_query(query, (employee_id, datetime.now(), today))
        return (True, "Clocked in successfully") if result else (False, "Failed to clock in")
    
    def clock_out(self, employee_id):
        today = date.today()
        query = """UPDATE attendance SET clock_out = %s 
                   WHERE employee_id = %s AND date = %s AND clock_out IS NULL"""
        cursor = self.connection.cursor()
        cursor.execute(query, (datetime.now(), employee_id, today))
        rows_affected = cursor.rowcount
        self.connection.commit()
        cursor.close()
        
        if rows_affected > 0:
            return True, "Clocked out successfully"
        else:
            return False, "No active clock-in found for today"
    
    def get_attendance_logs(self, limit=None, employee_id=None):
        if employee_id:
            query = """SELECT a.*, e.first_name, e.last_name, e.department 
                       FROM attendance a 
                       JOIN employees e ON a.employee_id = e.id 
                       WHERE a.employee_id = %s
                       ORDER BY a.date DESC, a.clock_in DESC"""
            if limit:
                query += f" LIMIT {limit}"
            return self.execute_query(query, (employee_id,), fetch=True)
        else:
            query = """SELECT a.*, e.first_name, e.last_name, e.department 
                       FROM attendance a 
                       JOIN employees e ON a.employee_id = e.id 
                       ORDER BY a.date DESC, a.clock_in DESC"""
            if limit:
                query += f" LIMIT {limit}"
            return self.execute_query(query, fetch=True)
    
    def get_today_attendance_status(self, employee_id):
        today = date.today()
        query = """SELECT * FROM attendance 
                   WHERE employee_id = %s AND date = %s"""
        result = self.execute_query(query, (employee_id, today), fetch=True)
        return result[0] if result else None
    
    # ==================== DASHBOARD STATISTICS METHOD ====================
    def get_dashboard_stats(self):
        """Get dashboard statistics with leave integration"""
        stats = {
            'total_employees': 0,
            'present_today': 0,
            'on_leave': 0,
            'late_employees': 0,
            'absent_today': 0,
            'total_users': 0
        }
        
        try:
            # Total Employees
            query = "SELECT COUNT(*) as count FROM employees"
            result = self.execute_query(query, fetch=True)
            stats['total_employees'] = result[0]['count'] if result else 0
            
            today = date.today()
            
            # Present Today (employees who clocked in)
            query = "SELECT COUNT(DISTINCT employee_id) as count FROM attendance WHERE DATE(clock_in) = %s"
            result = self.execute_query(query, (today,), fetch=True)
            stats['present_today'] = result[0]['count'] if result else 0
            
            # On Leave Today (approved leave requests) - FIXED
            try:
                # First, let's debug what's in the database
                debug_query = """
                    SELECT employee_id, leave_date, status 
                    FROM leave_requests 
                    WHERE leave_date = %s
                """
                debug_result = self.execute_query(debug_query, (today,), fetch=True)
                print(f"DEBUG - All leave requests for today: {debug_result}")
                
                # Now count approved ones (case-insensitive)
                query = """
                    SELECT COUNT(DISTINCT employee_id) as count 
                    FROM leave_requests 
                    WHERE leave_date = %s AND LOWER(status) = 'approved'
                """
                result = self.execute_query(query, (today,), fetch=True)
                stats['on_leave'] = result[0]['count'] if result else 0
                print(f"DEBUG - On Leave Count: {stats['on_leave']}")
            except Exception as e:
                print(f"Error fetching on_leave: {e}")
                import traceback
                traceback.print_exc()
                stats['on_leave'] = 0
            
            # Late Employees (using status column) - FIXED
            try:
                query = """
                    SELECT COUNT(DISTINCT employee_id) as count 
                    FROM attendance 
                    WHERE date = %s AND status = 'late'
                """
                result = self.execute_query(query, (today,), fetch=True)
                stats['late_employees'] = result[0]['count'] if result else 0
                print(f"DEBUG - Late Employees Count: {stats['late_employees']}")  # Debug line
            except Exception as e:
                print(f"Error fetching late_employees: {e}")
                stats['late_employees'] = 0
            
            # Absent Today
            stats['absent_today'] = stats['total_employees'] - stats['present_today'] - stats['on_leave']
        
        except Exception as e:
            print(f"Error fetching dashboard stats: {e}")
        
        return stats
    # ==================== END DASHBOARD STATISTICS METHOD ====================
    
    # --- Daily Attendance Stats (UPDATED WITH LEAVE DATA) ---
    def get_daily_attendance_stats(self, days=7):
        """Get daily attendance stats for last N days including leave data"""
        try:
            total_employees_query = "SELECT COUNT(*) as count FROM employees"
            total_result = self.execute_query(total_employees_query, fetch=True)
            total_employees = total_result[0]['count'] if total_result else 0
            
            # Get attendance data
            attendance_query = """
                SELECT DATE(clock_in) as date,
                       COUNT(DISTINCT employee_id) as present
                FROM attendance
                WHERE DATE(clock_in) >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                GROUP BY DATE(clock_in)
                ORDER BY date ASC
            """
            attendance_result = self.execute_query(attendance_query, (days,), fetch=True)
            
            # Get leave data
            leave_query = """
                SELECT leave_date as date,
                       COUNT(*) as on_leave
                FROM leave_requests
                WHERE leave_date >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
                AND status = 'Approved'
                GROUP BY leave_date
                ORDER BY leave_date ASC
            """
            leave_result = self.execute_query(leave_query, (days,), fetch=True)
            
            # Merge data
            leave_dict = {row['date']: row['on_leave'] for row in leave_result} if leave_result else {}
            
            data_list = []
            if attendance_result:
                for row in attendance_result:
                    if row['date']:
                        leave_count = leave_dict.get(row['date'], 0)
                        present = row['present'] or 0
                        absent = total_employees - present - leave_count
                        data_list.append({
                            'date': row['date'].strftime("%m-%d"),
                            'present': present,
                            'absent': max(0, absent),
                            'leave': leave_count
                        })
            
            return data_list if data_list else []
        except Exception as e:
            print(f"Error fetching daily stats: {e}")
            return []
    
    # --- Weekly Attendance Stats (UPDATED WITH LEAVE DATA) ---
    def get_weekly_attendance_stats(self, weeks=4):
        """Get weekly attendance stats including leave data"""
        try:
            total_employees_query = "SELECT COUNT(*) as count FROM employees"
            total_result = self.execute_query(total_employees_query, fetch=True)
            total_employees = total_result[0]['count'] if total_result else 0
            
            # Get attendance by week
            query = """
                SELECT WEEK(clock_in, 1) as week_num,
                       COUNT(DISTINCT employee_id, DATE(clock_in)) as present
                FROM attendance
                WHERE clock_in >= DATE_SUB(CURDATE(), INTERVAL %s WEEK)
                GROUP BY WEEK(clock_in, 1)
                ORDER BY week_num DESC
            """
            attendance_result = self.execute_query(query, (weeks,), fetch=True)
            
            # Get leaves by week
            leave_query = """
                SELECT WEEK(leave_date, 1) as week_num,
                       COUNT(*) as on_leave
                FROM leave_requests
                WHERE leave_date >= DATE_SUB(CURDATE(), INTERVAL %s WEEK)
                AND status = 'Approved'
                GROUP BY WEEK(leave_date, 1)
            """
            leave_result = self.execute_query(leave_query, (weeks,), fetch=True)
            
            leave_dict = {row['week_num']: row['on_leave'] for row in leave_result} if leave_result else {}
            
            data_list = []
            if attendance_result:
                for row in attendance_result:
                    leave_count = leave_dict.get(row['week_num'], 0)
                    present = row['present'] or 0
                    absent = (total_employees * 7) - present - leave_count
                    data_list.append({
                        'week': f"W{row['week_num']}",
                        'present': present,
                        'absent': max(0, absent),
                        'leave': leave_count
                    })
            
            return data_list if data_list else []
        except Exception as e:
            print(f"Error fetching weekly stats: {e}")
            return []
    
    # --- Monthly Attendance Stats (UPDATED WITH LEAVE DATA) ---
    def get_monthly_attendance_stats(self, months=6):
        """Get monthly attendance stats including leave data"""
        try:
            total_employees_query = "SELECT COUNT(*) as count FROM employees"
            total_result = self.execute_query(total_employees_query, fetch=True)
            total_employees = total_result[0]['count'] if total_result else 0
            
            # Get attendance by month
            query = """
                SELECT MONTH(clock_in) as month, YEAR(clock_in) as year,
                       COUNT(DISTINCT employee_id, DATE(clock_in)) as present
                FROM attendance
                WHERE clock_in >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
                GROUP BY MONTH(clock_in), YEAR(clock_in)
                ORDER BY year DESC, month DESC
            """
            attendance_result = self.execute_query(query, (months,), fetch=True)
            
            # Get leaves by month
            leave_query = """
                SELECT MONTH(leave_date) as month, YEAR(leave_date) as year,
                       COUNT(*) as on_leave
                FROM leave_requests
                WHERE leave_date >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
                AND status = 'Approved'
                GROUP BY MONTH(leave_date), YEAR(leave_date)
            """
            leave_result = self.execute_query(leave_query, (months,), fetch=True)
            
            leave_dict = {(row['month'], row['year']): row['on_leave'] for row in leave_result} if leave_result else {}
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            data_list = []
            if attendance_result:
                for row in attendance_result:
                    leave_count = leave_dict.get((row['month'], row['year']), 0)
                    present = row['present'] or 0
                    # Estimate days in month as 30 for calculation
                    absent = (total_employees * 30) - present - leave_count
                    data_list.append({
                        'month': month_names[(row['month'] - 1) % 12],
                        'present': present,
                        'absent': max(0, absent),
                        'leave': leave_count
                    })
            
            return data_list if data_list else []
        except Exception as e:
            print(f"Error fetching monthly stats: {e}")
            return []
    
    # --- Get Upcoming Holidays ---
    def get_upcoming_holidays(self, limit=5):
        """Get upcoming holidays"""
        try:
            query = """
                SELECT id, name, DATE_FORMAT(holiday_date, '%d-%b') as date
                FROM holidays
                WHERE holiday_date >= CURDATE()
                ORDER BY holiday_date ASC
                LIMIT %s
            """
            result = self.execute_query(query, (limit,), fetch=True)
            
            if result:
                data = [{'name': row['name'], 'date': row['date']} for row in result]
                return data
            else:
                return []
        except Exception as e:
            print(f"Error fetching holidays: {e}")
            return []
    
    # ==================== LEAVE MANAGEMENT METHODS ====================
    
    def create_leave_request(self, employee_id, leave_date, leave_type, reason):
        """Create a new leave request"""
        try:
            query = """INSERT INTO leave_requests 
                       (employee_id, leave_date, leave_type, reason, status, created_at)
                       VALUES (%s, %s, %s, %s, 'Pending', %s)"""
            result = self.execute_query(query, (employee_id, leave_date, leave_type, reason, datetime.now()))
            return result is not False
        except Exception as e:
            print(f"Error creating leave request: {e}")
            return False
    
    def get_employee_leave_requests(self, employee_id):
        """Get all leave requests for a specific employee"""
        try:
            query = """
                SELECT id, leave_date, leave_type, reason, status,
                       DATE_FORMAT(created_at, '%Y-%m-%d %H:%i') as created_at,
                       DATE_FORMAT(approved_at, '%Y-%m-%d %H:%i') as approved_at
                FROM leave_requests 
                WHERE employee_id = %s 
                ORDER BY created_at DESC
            """
            return self.execute_query(query, (employee_id,), fetch=True) or []
        except Exception as e:
            print(f"Error fetching employee leave requests: {e}")
            return []
    
    def get_pending_leave_requests(self):
        """Get all pending leave requests with employee details"""
        try:
            query = """
                SELECT lr.id, lr.employee_id,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                       lr.leave_date, lr.leave_type, lr.reason, lr.status,
                       DATE_FORMAT(lr.created_at, '%Y-%m-%d %H:%i') as created_at
                FROM leave_requests lr
                INNER JOIN employees e ON lr.employee_id = e.id
                WHERE lr.status = 'Pending'
                ORDER BY lr.created_at DESC
            """
            return self.execute_query(query, fetch=True) or []
        except Exception as e:
            print(f"Error fetching pending leave requests: {e}")
            return []
    
    def get_all_leave_requests(self):
        """Get all leave requests with employee details"""
        try:
            query = """
                SELECT lr.id, lr.employee_id,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                       lr.leave_date, lr.leave_type, lr.reason, lr.status,
                       DATE_FORMAT(lr.created_at, '%Y-%m-%d %H:%i') as created_at,
                       DATE_FORMAT(lr.approved_at, '%Y-%m-%d %H:%i') as approved_at
                FROM leave_requests lr
                INNER JOIN employees e ON lr.employee_id = e.id
                ORDER BY lr.created_at DESC
            """
            return self.execute_query(query, fetch=True) or []
        except Exception as e:
            print(f"Error fetching all leave requests: {e}")
            return []
    
    def get_approved_leave_requests(self):
        """Get all approved leave requests"""
        try:
            query = """
                SELECT lr.id, lr.employee_id,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                       lr.leave_date, lr.leave_type, lr.reason, lr.status,
                       DATE_FORMAT(lr.created_at, '%Y-%m-%d %H:%i') as created_at,
                       DATE_FORMAT(lr.approved_at, '%Y-%m-%d %H:%i') as approved_at
                FROM leave_requests lr
                INNER JOIN employees e ON lr.employee_id = e.id
                WHERE lr.status = 'Approved'
                ORDER BY lr.leave_date DESC
            """
            return self.execute_query(query, fetch=True) or []
        except Exception as e:
            print(f"Error fetching approved leave requests: {e}")
            return []
    
    def get_rejected_leave_requests(self):
        """Get all rejected leave requests"""
        try:
            query = """
                SELECT lr.id, lr.employee_id,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                       lr.leave_date, lr.leave_type, lr.reason, lr.status,
                       DATE_FORMAT(lr.created_at, '%Y-%m-%d %H:%i') as created_at,
                       DATE_FORMAT(lr.approved_at, '%Y-%m-%d %H:%i') as approved_at
                FROM leave_requests lr
                INNER JOIN employees e ON lr.employee_id = e.id
                WHERE lr.status = 'Rejected'
                ORDER BY lr.created_at DESC
            """
            return self.execute_query(query, fetch=True) or []
        except Exception as e:
            print(f"Error fetching rejected leave requests: {e}")
            return []
    
    def approve_leave_request(self, leave_id, admin_id):
        """Approve a leave request and mark attendance as leave"""
        try:
            # Get leave request details
            query = "SELECT employee_id, leave_date, leave_type FROM leave_requests WHERE id = %s"
            leave_data = self.execute_query(query, (leave_id,), fetch=True)
            
            if not leave_data:
                return False
            
            leave_info = leave_data[0]
            
            # Update leave request status
            update_query = """UPDATE leave_requests 
                            SET status = 'Approved', approved_by = %s, approved_at = %s 
                            WHERE id = %s"""
            self.execute_query(update_query, (admin_id, datetime.now(), leave_id))
            
            # Mark attendance as leave
            attendance_query = """
                INSERT INTO attendance (employee_id, date, status, leave_type, clock_in)
                VALUES (%s, %s, 'leave', %s, NULL)
                ON DUPLICATE KEY UPDATE 
                    status = 'leave', 
                    leave_type = %s
            """
            self.execute_query(attendance_query, (
                leave_info['employee_id'],
                leave_info['leave_date'],
                leave_info['leave_type'],
                leave_info['leave_type']
            ))
            
            return True
        except Exception as e:
            print(f"Error approving leave request: {e}")
            return False
    
    def reject_leave_request(self, leave_id, admin_id, rejection_reason=""):
        """Reject a leave request"""
        try:
            query = """UPDATE leave_requests 
                       SET status = 'Rejected', approved_by = %s, approved_at = %s
                       WHERE id = %s"""
            result = self.execute_query(query, (admin_id, datetime.now(), leave_id))
            return result is not False
        except Exception as e:
            print(f"Error rejecting leave request: {e}")
            return False
    
    def get_leaves_for_date(self, target_date):
        """Get all employees on leave for a specific date"""
        try:
            query = """
                SELECT lr.id, lr.employee_id,
                       CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                       lr.leave_type, lr.reason
                FROM leave_requests lr
                INNER JOIN employees e ON lr.employee_id = e.id
                WHERE lr.leave_date = %s AND lr.status = 'Approved'
            """
            return self.execute_query(query, (target_date,), fetch=True) or []
        except Exception as e:
            print(f"Error fetching leaves for date: {e}")
            return []
    
    def get_employee_leave_count(self, employee_id, year=None):
        """Get total approved leaves for an employee in a year"""
        try:
            if year is None:
                year = datetime.now().year
            
            query = """
                SELECT COUNT(*) as leave_count
                FROM leave_requests
                WHERE employee_id = %s 
                    AND status = 'Approved'
                    AND YEAR(leave_date) = %s
            """
            result = self.execute_query(query, (employee_id, year), fetch=True)
            return result[0]['leave_count'] if result else 0
        except Exception as e:
            print(f"Error fetching employee leave count: {e}")
            return 0
    
    # ==================== END LEAVE MANAGEMENT METHODS ====================
    
    # OLD LEAVE REQUEST OPERATIONS (Keep for compatibility if needed)
    def get_leave_requests(self, employee_id=None, status=None):
        """Get leave requests with optional filters (OLD METHOD)"""
        query = "SELECT * FROM leave_requests WHERE 1=1"
        params = []
        
        if employee_id:
            query += " AND employee_id = %s"
            params.append(employee_id)
        
        if status:
            query += " AND status = %s"
            params.append(status)
        
        query += " ORDER BY created_at DESC"
        return self.execute_query(query, tuple(params), fetch=True) if params else self.execute_query(query, fetch=True)
    
    def update_leave_request_status(self, leave_id, status):
        """Update leave request status (OLD METHOD - use approve/reject methods instead)"""
        query = "UPDATE leave_requests SET status = %s WHERE id = %s"
        return self.execute_query(query, (status, leave_id))
    
    def fetch_all_employees(self):
        employees = self.get_all_employees()
        formatted_data = []
        if employees:
            for emp in employees:
                display_id = emp.get('Emp_ID') if emp.get('Emp_ID') else str(emp['id'])
                
                row = (
                    display_id,
                    emp['first_name'],
                    emp['last_name'],
                    emp['email'],
                    emp.get('phone', '---'),
                    emp['department'],
                    emp['position'],
                    str(emp['hire_date']) if emp['hire_date'] else "---",
                    emp['id']
                )
                formatted_data.append(row)
        
        return formatted_data
    
# ==================== LATE FEE METHODS ====================
    # Copy and paste this inside your Database class in database.py
    # Make sure these align with your other methods like 'connect' or 'disconnect'

    def clock_in_with_late_fee(self, employee_id):
        """Clock in with automatic late fee calculation"""
        # Import inside function to avoid circular import issues
        from late_fee_calculator import LateFeeCalculator 
        from datetime import datetime, date
        
        today = date.today()
        # Check if already clocked in
        check_query = "SELECT * FROM attendance WHERE employee_id = %s AND date = %s AND clock_out IS NULL"
        existing = self.execute_query(check_query, (employee_id, today), fetch=True)
        
        if existing:
            return False, "Already clocked in today", None
        
        clock_in_time = datetime.now()
        
        # Insert attendance record
        query = """INSERT INTO attendance (employee_id, clock_in, date, status)
                   VALUES (%s, %s, %s, 'present')"""
        attendance_id = self.execute_query(query, (employee_id, clock_in_time, today))
        
        if attendance_id:
            # Calculate and process late fee
            calculator = LateFeeCalculator(self)
            late_result = calculator.process_late_attendance(attendance_id, employee_id, clock_in_time)
            
            return True, late_result['message'], late_result
        else:
            return False, "Failed to clock in", None

    def get_employee_late_fees(self, employee_id):
        """Get all late fees for an employee"""
        query = """SELECT a.id, a.date, a.clock_in, a.minutes_late, 
                          a.late_fee_amount, a.late_fee_paid
                   FROM attendance a
                   WHERE a.employee_id = %s AND a.late_fee_amount > 0
                   ORDER BY a.date DESC"""
        return self.execute_query(query, (employee_id,), fetch=True)

    def get_all_unpaid_late_fees(self):
        """Get all unpaid late fees across all employees"""
        query = """SELECT a.id, a.employee_id, a.date, a.clock_in,
                          CONCAT(e.first_name, ' ', e.last_name) as employee_name,
                          e.department, a.minutes_late, a.late_fee_amount
                   FROM attendance a
                   JOIN employees e ON a.employee_id = e.id
                   WHERE a.late_fee_amount > 0 AND a.late_fee_paid = 0
                   ORDER BY a.date DESC"""
        return self.execute_query(query, fetch=True)

    def get_admin_fee_summary(self):
        """Get late fee summary for all employees (For Admin Dashboard)"""
        query = """SELECT e.id, CONCAT(e.first_name, ' ', e.last_name) as name,
                          e.department,
                          COUNT(CASE WHEN a.late_fee_amount > 0 THEN 1 END) as late_count,
                          COALESCE(SUM(a.late_fee_amount), 0) as total_fees,
                          COALESCE(SUM(CASE WHEN a.late_fee_paid = 1 THEN a.late_fee_amount ELSE 0 END), 0) as paid,
                          COALESCE(SUM(CASE WHEN a.late_fee_paid = 0 THEN a.late_fee_amount ELSE 0 END), 0) as unpaid
                   FROM employees e
                   LEFT JOIN attendance a ON e.id = a.employee_id
                   GROUP BY e.id, e.first_name, e.last_name, e.department
                   HAVING late_count > 0
                   ORDER BY total_fees DESC"""
        return self.execute_query(query, fetch=True)

    def get_late_fee_settings(self):
        """Get current late fee settings"""
        query = "SELECT * FROM late_fee_settings WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
        result = self.execute_query(query, fetch=True)
        return result[0] if result else None

    def get_employee_unpaid_fees(self, employee_id):
        """Get all unpaid late records for a specific employee"""
        query = """
            SELECT id, date, minutes_late, late_fee_amount, status
            FROM attendance 
            WHERE employee_id = %s 
            AND late_fee_amount > 0 
            AND (late_fee_paid = 0 OR late_fee_paid IS NULL)
            ORDER BY date DESC
        """
        return self.execute_query(query, (employee_id,), fetch=True)

    def process_payment(self, attendance_id, employee_id, amount):
        """Record a payment and mark attendance as paid"""
        try:
            # 1. Record the payment
            payment_query = """
                INSERT INTO late_fee_payments 
                (attendance_id, employee_id, amount_paid, payment_date) 
                VALUES (%s, %s, %s, NOW())
            """
            self.execute_query(payment_query, (attendance_id, employee_id, amount))

            # 2. Mark the attendance record as 'paid'
            update_query = "UPDATE attendance SET late_fee_paid = 1 WHERE id = %s"
            self.execute_query(update_query, (attendance_id,))
            
            return True
        except Exception as e:
            print(f"Payment Error: {e}")
            return False

    # ==================== END LATE FEE METHODS ====================