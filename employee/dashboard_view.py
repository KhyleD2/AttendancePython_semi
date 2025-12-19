import tkinter as tk
from tkinter import Canvas, Frame, Label, Button, messagebox
from datetime import datetime, timedelta, date
import calendar

class DashboardView:
    def __init__(self, parent_frame, db, employee):
        self.parent_frame = parent_frame
        self.db = db
        self.employee = employee
        self.current_date = datetime.now()
        self.render()
    
    def render(self):
        # Clear the parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
            
        # Main background
        self.parent_frame.configure(bg="#F5F7FA")

        # Create main container
        main_container = Frame(self.parent_frame, bg="#F5F7FA")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = Label(
            main_container,
            text="My Dashboard",
            font=("Segoe UI", 28, "bold"),
            fg="#1F2937",
            bg="#F5F7FA"
        )
        title_label.pack(anchor=tk.W, padx=40, pady=(30, 20))

        # KPI Cards Section
        self.create_kpi_cards(main_container)

        # Content frame
        content_frame = Frame(main_container, bg="#F5F7FA")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=(20, 30))

        # Main grid layout
        left_frame = Frame(content_frame, bg="#F5F7FA")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))

        right_frame = Frame(content_frame, bg="#F5F7FA")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(15, 0))
        right_frame.config(width=400)

        # Create components with REAL DATA
        self.create_calendar_card(left_frame)
        self.create_bottom_cards(left_frame)
        
        self.create_clock_card(right_frame)
        self.create_announcements_card(right_frame)

    def create_kpi_cards(self, parent):
        """Create KPI cards section at the top"""
        kpi_container = Frame(parent, bg="#F5F7FA")
        kpi_container.pack(fill=tk.X, padx=40, pady=(0, 20))

        # Get monthly statistics
        stats = self.get_monthly_statistics()

        cards_data = [
            ("Days Present", stats['present'], "#2ecc71", "✔"),
            ("Days Absent", stats['absent'], "#e74c3c", "✖"),
            ("Days on Leave", stats['leave'], "#f39c12", "📋"),
            ("Total Late Days", stats['late'], "#e67e22", "⏰")
        ]

        for i, (title, value, color, icon) in enumerate(cards_data):
            self.create_stat_card(kpi_container, i, title, value, color, icon)

    def create_stat_card(self, parent, col_index, title, value, color, icon):
        """Create individual stat card"""
        card = Frame(parent, bg="white", padx=20, pady=20)
        card.grid(row=0, column=col_index, sticky="ew", padx=10)
        parent.columnconfigure(col_index, weight=1)
        
        # Colored strip on left
        strip = Frame(card, bg=color, width=6)
        strip.place(relx=0, rely=0, relheight=1, anchor="nw")
        
        content = Frame(card, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=(10, 0))
        
        header_row = Frame(content, bg="white")
        header_row.pack(fill=tk.X)
        
        Label(
            header_row, 
            text=title.upper(), 
            font=("Segoe UI", 9, "bold"), 
            fg="#95a5a6", 
            bg="white"
        ).pack(side=tk.LEFT)
        
        Label(
            header_row, 
            text=icon, 
            font=("Segoe UI", 20), 
            fg=color, 
            bg="white"
        ).pack(side=tk.RIGHT)
        
        Label(
            content, 
            text=str(value), 
            font=("Segoe UI", 32, "bold"), 
            fg="#2c3e50", 
            bg="white"
        ).pack(anchor="e", pady=(5, 0))

    def get_employee_hire_date(self):
        """Get employee's hire date from database"""
        try:
            query = """
                SELECT hire_date
                FROM employees
                WHERE id = %s
            """
            result = self.db.execute_query(query, (self.employee['id'],), fetch=True)
            if result and result[0]['hire_date']:
                return result[0]['hire_date']
            return None
        except Exception as e:
            print(f"Error fetching hire date: {e}")
            return None

    def get_monthly_statistics(self):
        """Get statistics for current month - FIXED to count missing records as absent"""
        try:
            year = self.current_date.year
            month = self.current_date.month
            
            # Get employee hire date
            hire_date = self.get_employee_hire_date()
            
            # If viewing a month before hire date, return all zeros
            if hire_date:
                hire_date_obj = hire_date if isinstance(hire_date, date) else hire_date.date()
                viewing_date = date(year, month, 1)
                
                # If entire month is before hire month, return zeros
                if (viewing_date.year < hire_date_obj.year) or \
                (viewing_date.year == hire_date_obj.year and viewing_date.month < hire_date_obj.month):
                    return {'present': 0, 'absent': 0, 'leave': 0, 'late': 0}
            
            # If viewing future month, return zeros
            today = date.today()
            if year > today.year or (year == today.year and month > today.month):
                return {'present': 0, 'absent': 0, 'leave': 0, 'late': 0}
            
            # Determine date range
            start_date = date(year, month, 1)
            if year == today.year and month == today.month:
                end_date = today
            else:
                last_day = calendar.monthrange(year, month)[1]
                end_date = date(year, month, last_day)
            
            # IMPORTANT: Adjust start date if hired mid-month
            if hire_date:
                hire_date_obj = hire_date if isinstance(hire_date, date) else hire_date.date()
                # If hire date is in this month and after the start, use hire date as start
                if hire_date_obj.year == year and hire_date_obj.month == month and hire_date_obj > start_date:
                    start_date = hire_date_obj
            
            # Count PRESENT days
            present_query = """
                SELECT COUNT(DISTINCT DATE(date)) as count
                FROM attendance
                WHERE employee_id = %s
                AND DATE(date) >= %s
                AND DATE(date) <= %s
                AND status = 'present'
            """
            present_result = self.db.execute_query(
                present_query, 
                (self.employee['id'], start_date, end_date), 
                fetch=True
            )
            present = present_result[0]['count'] if present_result else 0
            
            # Count LATE days
            late_query = """
                SELECT COUNT(DISTINCT DATE(date)) as count
                FROM attendance
                WHERE employee_id = %s
                AND DATE(date) >= %s
                AND DATE(date) <= %s
                AND status = 'late'
            """
            late_result = self.db.execute_query(
                late_query, 
                (self.employee['id'], start_date, end_date), 
                fetch=True
            )
            late = late_result[0]['count'] if late_result else 0
            
            # Count ABSENT days from database records
            absent_records_query = """
                SELECT COUNT(DISTINCT DATE(date)) as count
                FROM attendance
                WHERE employee_id = %s
                AND DATE(date) >= %s
                AND DATE(date) <= %s
                AND status = 'absent'
            """
            absent_records_result = self.db.execute_query(
                absent_records_query, 
                (self.employee['id'], start_date, end_date), 
                fetch=True
            )
            absent_records = absent_records_result[0]['count'] if absent_records_result else 0
            
            # Count APPROVED leaves
            leave_query = """
                SELECT COUNT(DISTINCT leave_date) as count
                FROM leave_requests
                WHERE employee_id = %s
                AND leave_date >= %s
                AND leave_date <= %s
                AND status = 'Approved'
            """
            leave_result = self.db.execute_query(
                leave_query, 
                (self.employee['id'], start_date, end_date), 
                fetch=True
            )
            leave = leave_result[0]['count'] if leave_result else 0
            
            # Count Sundays in the date range
            sundays = 0
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() == 6:  # Sunday
                    sundays += 1
                current_date += timedelta(days=1)
            
            # Count holidays in the date range
            holiday_query = """
                SELECT COUNT(*) as count
                FROM holidays
                WHERE holiday_date >= %s
                AND holiday_date <= %s
            """
            holiday_result = self.db.execute_query(
                holiday_query, 
                (start_date, end_date), 
                fetch=True
            )
            holidays = holiday_result[0]['count'] if holiday_result else 0
            
            # Calculate totals
            total_days = (end_date - start_date).days + 1
            working_days = total_days - sundays - holidays
            
            # Calculate absent: Working days - (Present + Late + Leave + Absent records)
            # If there are no records for a working day, it counts as absent
            accounted_days = present + late + leave + absent_records
            calculated_absent = max(0, working_days - present - late - leave)
            
            # Use the MAXIMUM of absent records vs calculated absent
            # This handles both cases:
            # 1. Days with explicit 'absent' status in DB
            # 2. Days with no records at all (missing = absent)
            absent = max(absent_records, calculated_absent)
            
            print(f"\n{'='*60}")
            print(f"Monthly Statistics for {year}-{month} (Employee ID: {self.employee['id']})")
            print(f"{'='*60}")
            print(f"Date range: {start_date} to {end_date}")
            print(f"Total days in range: {total_days}")
            print(f"Sundays: {sundays}, Holidays: {holidays}")
            print(f"Working days: {working_days}")
            print(f"")
            print(f"Present: {present}")
            print(f"Late: {late}")
            print(f"Absent records in DB: {absent_records}")
            print(f"Leave: {leave}")
            print(f"Accounted days: {accounted_days}")
            print(f"")
            print(f"Calculated absent (missing records): {calculated_absent}")
            print(f"FINAL Absent (max of both): {absent}")
            print(f"{'='*60}\n")
            
            return {
                'present': present + late,  # Total days present (including late)
                'absent': absent,           # Calculated or from DB, whichever is higher
                'leave': leave,
                'late': late
            }
            
        except Exception as e:
            print(f"Error getting monthly statistics: {e}")
            import traceback
            traceback.print_exc()
            return {'present': 0, 'absent': 0, 'leave': 0, 'late': 0}

    def get_holidays_for_month(self):
        """Get holidays for current month - WITH DEBUG"""
        try:
            year = self.current_date.year
            month = self.current_date.month
            
            query = """
                SELECT holiday_date, name
                FROM holidays
                WHERE YEAR(holiday_date) = %s 
                AND MONTH(holiday_date) = %s
            """
            result = self.db.execute_query(query, (year, month), fetch=True)
            
            print(f"\n🔍 DEBUG: Fetching holidays for {year}-{month}")
            print(f"Query result: {result}")
            
            holiday_dict = {}
            if result:
                for row in result:
                    holiday_date = row['holiday_date']
                    # Ensure it's a date object
                    if isinstance(holiday_date, str):
                        from datetime import datetime
                        holiday_date = datetime.strptime(holiday_date, "%Y-%m-%d").date()
                    elif hasattr(holiday_date, 'date'):
                        holiday_date = holiday_date.date()
                    
                    holiday_dict[holiday_date] = row
                    print(f"  ✅ Added holiday: {holiday_date} - {row['name']}")
            else:
                print(f"  ❌ No holidays found")
            
            print(f"Final holiday_dict: {holiday_dict}")
            print("="*50 + "\n")
            
            return holiday_dict
        except Exception as e:
            print(f"❌ Error fetching holidays: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def create_calendar_card(self, parent):
        """Calendar card with REAL attendance data from database"""
        card = Frame(parent, bg="white", relief=tk.FLAT, bd=0)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        card.config(highlightbackground="#E5E7EB", highlightthickness=1)

        # Header with month/year navigation
        header_frame = Frame(card, bg="white")
        header_frame.pack(fill=tk.X, padx=25, pady=(20, 15))

        month_year = self.current_date.strftime("%B %Y")
        
        # Navigation arrows
        nav_frame = Frame(header_frame, bg="white")
        nav_frame.pack(side=tk.LEFT)
        
        prev_btn = Label(nav_frame, text="<", font=("Segoe UI", 14), fg="#6B7280", bg="white", cursor="hand2")
        prev_btn.pack(side=tk.LEFT, padx=5)
        prev_btn.bind("<Button-1>", lambda e: self.change_month(-1))
        
        Label(nav_frame, text=month_year, font=("Segoe UI", 16, "bold"), fg="#1F2937", bg="white").pack(side=tk.LEFT, padx=10)
        
        next_btn = Label(nav_frame, text=">", font=("Segoe UI", 14), fg="#6B7280", bg="white", cursor="hand2")
        next_btn.pack(side=tk.LEFT, padx=5)
        next_btn.bind("<Button-1>", lambda e: self.change_month(1))

        # Calendar grid
        cal_container = Frame(card, bg="white")
        cal_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=(0, 20))

        # Days of week header
        days_header = Frame(cal_container, bg="#3B82F6", height=40)
        days_header.pack(fill=tk.X)

        days = ["Sun", "Mon", "Tue", "Wed", "Thur", "Fri", "Sat"]
        for day in days:
            Label(
                days_header,
                text=day,
                font=("Segoe UI", 11, "bold"),
                fg="white",
                bg="#3B82F6",
                width=10
            ).pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=1)

        # Get REAL attendance data from database
        attendance_data = self.get_attendance_for_month()
        leave_data = self.get_leaves_for_month()
        holidays_data = self.get_holidays_for_month()
        hire_date = self.get_employee_hire_date()
        
        # Get calendar data - SET FIRST DAY TO SUNDAY
        year = self.current_date.year
        month = self.current_date.month
        
        # Create calendar with Sunday as first day
        cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
        month_days = cal.monthdayscalendar(year, month)

        # Calendar rows
        for week in month_days:
            week_frame = Frame(cal_container, bg="white")
            week_frame.pack(fill=tk.X)

            for day in week:
                day_cell = Frame(week_frame, bg="white", relief=tk.FLAT, bd=1, 
                               highlightbackground="#E5E7EB", highlightthickness=1)
                day_cell.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=0, pady=0)

                if day == 0:
                    Label(day_cell, text="", bg="white", height=4).pack()
                else:
                    cell_content = Frame(day_cell, bg="white")
                    cell_content.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

                    # Day number
                    Label(
                        cell_content,
                        text=str(day),
                        font=("Segoe UI", 12, "bold"),
                        fg="#1F2937",
                        bg="white"
                    ).pack(anchor=tk.NW)

                    # Determine status for this day
                    day_date = date(year, month, day)
                    status = self.get_day_status(day_date, attendance_data, leave_data, holidays_data, hire_date)
                    
                    if status:
                        status_text, status_bg, status_fg = status
                        
                        status_label = Label(
                            cell_content,
                            text=status_text,
                            font=("Segoe UI", 8),
                            fg=status_fg,
                            bg=status_bg,
                            padx=4,
                            pady=2
                        )
                        status_label.pack(anchor=tk.CENTER, pady=(5, 0))

                    # Highlight today
                    if day == datetime.now().day and month == datetime.now().month and year == datetime.now().year:
                        day_cell.config(highlightbackground="#3B82F6", highlightthickness=2)

    def get_attendance_for_month(self):
        """Get attendance records for current month"""
        try:
            year = self.current_date.year
            month = self.current_date.month
            
            query = """
                SELECT DATE(date) as date, status, clock_in, clock_out
                FROM attendance
                WHERE employee_id = %s 
                AND YEAR(date) = %s 
                AND MONTH(date) = %s
            """
            result = self.db.execute_query(query, (self.employee['id'], year, month), fetch=True)
            
            # Convert to dictionary for easy lookup
            attendance_dict = {}
            if result:
                for row in result:
                    attendance_dict[row['date']] = row
            
            return attendance_dict
        except Exception as e:
            print(f"Error fetching attendance: {e}")
            return {}

    def get_leaves_for_month(self):
        """Get approved leaves for current month"""
        try:
            year = self.current_date.year
            month = self.current_date.month
            
            query = """
                SELECT leave_date, leave_type, status
                FROM leave_requests
                WHERE employee_id = %s 
                AND YEAR(leave_date) = %s 
                AND MONTH(leave_date) = %s
            """
            result = self.db.execute_query(query, (self.employee['id'], year, month), fetch=True)
            
            leave_dict = {}
            if result:
                for row in result:
                    leave_dict[row['leave_date']] = row
            
            return leave_dict
        except Exception as e:
            print(f"Error fetching leaves: {e}")
            return {}

    def get_holidays_for_month(self):
        """Get holidays for current month"""
        try:
            year = self.current_date.year
            month = self.current_date.month
            
            query = """
                SELECT holiday_date, name
                FROM holidays
                WHERE YEAR(holiday_date) = %s 
                AND MONTH(holiday_date) = %s
            """
            result = self.db.execute_query(query, (year, month), fetch=True)
            
            holiday_dict = {}
            if result:
                for row in result:
                    holiday_dict[row['holiday_date']] = row
            
            return holiday_dict
        except Exception as e:
            print(f"Error fetching holidays: {e}")
            return {}

    def get_day_status(self, day_date, attendance_data, leave_data, holidays_data, hire_date):
        """Determine status for a specific day - FIXED to show future holidays"""
        
        # Check if employee was hired yet
        if hire_date:
            hire_date_obj = hire_date if isinstance(hire_date, date) else hire_date.date()
            if day_date < hire_date_obj:
                return None  # Don't show any status before hire date
        
        # Check if it's Sunday (0=Mon, 1=Tue... 6=Sun)
        if day_date.weekday() == 6:  # Sunday
            return ("Rest Day", "#F3F4F6", "#6B7280")
        
        # *** FIX: Check holidays FIRST - even for future dates ***
        if day_date in holidays_data:
            holiday_name = holidays_data[day_date]['name']
            print(f"✅ Holiday found: {day_date} - {holiday_name}")
            return ("Holiday", "#E0E7FF", "#3730A3")
        
        # NOW check if it's a future date (after checking holidays)
        if day_date > date.today():
            return None
        
        # Check if there's a leave request
        if day_date in leave_data:
            leave = leave_data[day_date]
            if leave['status'] == 'Approved':
                return ("On Leave", "#F3E8FF", "#6B21A8")
            elif leave['status'] == 'Pending':
                return ("Pending REQ", "#FEF3C7", "#92400E")
            elif leave['status'] == 'Rejected':
                return ("Rejected", "#FEE2E2", "#991B1B")
        
        # Check attendance
        if day_date in attendance_data:
            att = attendance_data[day_date]
            if att['status'] == 'present':
                return ("Present", "#DBEAFE", "#1E40AF")
            elif att['status'] == 'late':
                return ("Late", "#FEF3C7", "#92400E")
            elif att['status'] == 'absent':
                return ("Absent", "#FEE2E2", "#991B1B")
        else:
            # No attendance record for past date = Absent
            return ("Absent", "#FEE2E2", "#991B1B")
        
        return None

    def change_month(self, delta):
        """Navigate to previous/next month"""
        current_month = self.current_date.month
        current_year = self.current_date.year
        
        new_month = current_month + delta
        new_year = current_year
        
        if new_month > 12:
            new_month = 1
            new_year += 1
        elif new_month < 1:
            new_month = 12
            new_year -= 1
        
        self.current_date = self.current_date.replace(year=new_year, month=new_month, day=1)
        self.render()

    def create_bottom_cards(self, parent):
        """Create bottom row cards with REAL data"""
        bottom_row = Frame(parent, bg="#F5F7FA")
        bottom_row.pack(fill=tk.X)

        # Working hours card
        working_card = Frame(bottom_row, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        working_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Get REAL working hours
        working_hours = self.get_weekly_working_hours()

        header = Frame(working_card, bg="white")
        header.pack(fill=tk.X, padx=20, pady=(20, 15))

        Label(
            header,
            text="Working hours",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(side=tk.LEFT)

        Label(
            header,
            text=f"{working_hours['total']:.1f} hrs",
            font=("Segoe UI", 14),
            fg="#6B7280",
            bg="white"
        ).pack(side=tk.RIGHT)

        # Bar chart
        chart_frame = Frame(working_card, bg="white")
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        bars_frame = Frame(chart_frame, bg="white", height=120)
        bars_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 10))
        bars_frame.pack_propagate(False)

        max_hours = max([h for h in working_hours['daily'].values()] + [8])
        
        for day_name, hours in working_hours['daily'].items():
            bar_container = Frame(bars_frame, bg="white")
            bar_container.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

            if hours > 0:
                bar_height = int((hours / max_hours) * 100)
                color = "#10B981" if hours >= 7 else "#FBBF24" if hours >= 4 else "#9CA3AF"
                
                spacer = Frame(bar_container, bg="white", height=100-bar_height)
                spacer.pack(side=tk.TOP)
                
                bar = Frame(bar_container, bg=color, width=40, height=bar_height)
                bar.pack()

        # Day labels
        labels_frame = Frame(chart_frame, bg="white")
        labels_frame.pack(fill=tk.X)

        for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
            Label(
                labels_frame,
                text=day,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="white"
            ).pack(side=tk.LEFT, expand=True)

    def get_upcoming_holidays(self):
        """Get upcoming holidays from database"""
        try:
            query = """
                SELECT name, holiday_date,
                       DATE_FORMAT(holiday_date, '%b %d, %W') as date_str
                FROM holidays
                WHERE holiday_date >= CURDATE()
                ORDER BY holiday_date ASC
                LIMIT 5
            """
            return self.db.execute_query(query, fetch=True) or []
        except:
            return []

    def get_weekly_working_hours(self):
        """Calculate working hours for the current week"""
        try:
            today = date.today()
            # Start from Sunday of current week
            week_start = today - timedelta(days=today.weekday() + 1 if today.weekday() != 6 else 0)
            
            query = """
                SELECT DATE(date) as date, clock_in, clock_out,
                       DAYNAME(date) as day_name
                FROM attendance
                WHERE employee_id = %s
                AND date >= %s
                AND date <= %s
                AND clock_out IS NOT NULL
            """
            result = self.db.execute_query(query, (self.employee['id'], week_start, today), fetch=True)
            
            daily_hours = {"Sun": 0, "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0}
            total = 0
            
            if result:
                for row in result:
                    if row['clock_in'] and row['clock_out']:
                        hours = (row['clock_out'] - row['clock_in']).total_seconds() / 3600
                        day_name = row['date'].strftime("%a")
                        daily_hours[day_name] = hours
                        total += hours
            
            return {'daily': daily_hours, 'total': total}
        except Exception as e:
            print(f"Error calculating working hours: {e}")
            return {'daily': {"Sun": 0, "Mon": 0, "Tue": 0, "Wed": 0, "Thu": 0, "Fri": 0, "Sat": 0}, 'total': 0}

    def get_attendance_summary(self):
        """Get attendance summary for current month"""
        try:
            year = self.current_date.year
            month = self.current_date.month
            
            # Count present days
            present_query = """
                SELECT COUNT(*) as count
                FROM attendance
                WHERE employee_id = %s
                AND YEAR(date) = %s
                AND MONTH(date) = %s
                AND status IN ('present', 'late')
            """
            present_result = self.db.execute_query(present_query, (self.employee['id'], year, month), fetch=True)
            present = present_result[0]['count'] if present_result else 0
            
            # Count leaves
            leave_query = """
                SELECT COUNT(*) as count
                FROM leave_requests
                WHERE employee_id = %s
                AND YEAR(leave_date) = %s
                AND MONTH(leave_date) = %s
                AND status = 'Approved'
            """
            leave_result = self.db.execute_query(leave_query, (self.employee['id'], year, month), fetch=True)
            leave = leave_result[0]['count'] if leave_result else 0
            
            # Count holidays
            today = date.today()
            holiday_query = """
                SELECT COUNT(*) as count
                FROM holidays
                WHERE YEAR(holiday_date) = %s
                AND MONTH(holiday_date) = %s
                AND holiday_date <= %s
            """
            holiday_result = self.db.execute_query(holiday_query, (year, month, today), fetch=True)
            holidays = holiday_result[0]['count'] if holiday_result else 0
            
            # Calculate absent
            days_in_month = min(today.day if today.month == month and today.year == year else calendar.monthrange(year, month)[1], calendar.monthrange(year, month)[1])
            working_days = days_in_month - holidays
            absent = max(0, working_days - present - leave)
            
            return {
                'present': present,
                'absent': absent,
                'leave': leave,
                'holidays': holidays
            }
        except Exception as e:
            print(f"Error getting attendance summary: {e}")
            return {'present': 0, 'absent': 0, 'leave': 0, 'holidays': 0}

    def create_clock_card(self, parent):
        """Clock in/out card with REAL functionality"""
        card = Frame(parent, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=400)
        card.pack(fill=tk.X, pady=(0, 20))
        card.pack_propagate(False)

        # Check today's attendance status
        attendance_status = self.db.get_today_attendance_status(self.employee['id'])
        
        is_clocked_in = attendance_status and attendance_status['clock_out'] is None
        
        Label(
            card,
            text="Let's get to work" if not is_clocked_in else "You're clocked in!",
            font=("Segoe UI", 20, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=25, pady=(20, 15))

        # Date and time
        now = datetime.now()
        Label(
            card,
            text=now.strftime("%a, %b %d, %Y"),
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.W, padx=25)

        Label(
            card,
            text=now.strftime("%I:%M:%S %p"),
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.W, padx=25, pady=(5, 15))

        # Shift time
        Label(
            card,
            text="Shift  9:00am - 6:00pm",
            font=("Segoe UI", 10),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.CENTER, pady=(5, 15))

        # Clock button
        if is_clocked_in:
            btn_text = "Clock Out"
            btn_color = "#EF4444"
            btn_hover = "#DC2626"
            command = self.clock_out
        else:
            btn_text = "Clock In"
            btn_color = "#10B981"
            btn_hover = "#059669"
            command = self.clock_in

        clock_btn = Button(
            card,
            text=btn_text,
            font=("Segoe UI", 13, "bold"),
            bg=btn_color,
            fg="white",
            activebackground=btn_hover,
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            pady=15,
            command=command
        )
        clock_btn.pack(fill=tk.X, padx=25, pady=(0, 20))

    def clock_in(self):
        """Handle clock in"""
        success, message, late_info = self.db.clock_in_with_late_fee(self.employee['id'])
        if success:
            if late_info and late_info.get('is_late'):
                msg = f"{message}\n\nYou are {late_info['minutes_late']} minutes late.\nLate fee: ₱{late_info['fee_amount']:.2f}"
                messagebox.showwarning("Clock In - Late", msg)
            else:
                messagebox.showinfo("Success", message)
            self.render()
        else:
            messagebox.showerror("Error", message)

    def clock_out(self):
        """Handle clock out"""
        success, message = self.db.clock_out(self.employee['id'])
        if success:
            messagebox.showinfo("Success", message)
            self.render()
        else:
            messagebox.showerror("Error", message)

    def create_announcements_card(self, parent):
        """Upcoming Holidays card"""
        card = Frame(parent, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=400)
        card.pack(fill=tk.X, pady=(0, 20))

        Label(
            card,
            text="Upcoming Holidays",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=25, pady=(20, 15))

        # Get REAL holidays from database
        holidays = self.get_upcoming_holidays()

        if holidays:
            for holiday in holidays[:4]:  # Show max 4
                item = Frame(card, bg="#F9FAFB")
                item.pack(fill=tk.X, padx=25, pady=(0, 10))

                icon_label = Label(
                    item,
                    text="🎉",
                    font=("Segoe UI", 20),
                    bg="#3B82F6",
                    fg="white",
                    width=2,
                    height=1
                )
                icon_label.pack(side=tk.LEFT, padx=(10, 15), pady=10)

                text_frame = Frame(item, bg="#F9FAFB")
                text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, pady=10)

                Label(
                    text_frame,
                    text=holiday['name'],
                    font=("Segoe UI", 12, "bold"),
                    fg="#1F2937",
                    bg="#F9FAFB"
                ).pack(anchor=tk.W)

                Label(
                    text_frame,
                    text=holiday['date_str'],
                    font=("Segoe UI", 10),
                    fg="#6B7280",
                    bg="#F9FAFB"
                ).pack(anchor=tk.W)
        else:
            Label(
                card,
                text="No upcoming holidays",
                font=("Segoe UI", 11),
                fg="#9CA3AF",
                bg="white"
            ).pack(padx=25, pady=10)

        Frame(card, bg="white", height=20).pack()