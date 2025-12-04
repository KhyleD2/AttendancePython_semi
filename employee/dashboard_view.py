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

        # KPI Cards Section (NEW)
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
        self.create_celebrations_card(right_frame)

    def create_kpi_cards(self, parent):
        """Create KPI cards section at the top - like admin dashboard"""
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

    def get_monthly_statistics(self):
        """Get statistics for current month"""
        try:
            year = self.current_date.year
            month = self.current_date.month
            
            # Present days
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
            
            # Late days
            late_query = """
                SELECT COUNT(*) as count
                FROM attendance
                WHERE employee_id = %s
                AND YEAR(date) = %s
                AND MONTH(date) = %s
                AND status = 'late'
            """
            late_result = self.db.execute_query(late_query, (self.employee['id'], year, month), fetch=True)
            late = late_result[0]['count'] if late_result else 0
            
            # Leave days
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
            
            # Calculate absent (working days up to today - present - leave)
            today = date.today()
            days_in_month = min(today.day if today.month == month and today.year == year else calendar.monthrange(year, month)[1], calendar.monthrange(year, month)[1])
            
            # Get holidays count
            holiday_query = """
                SELECT COUNT(*) as count
                FROM holidays
                WHERE YEAR(holiday_date) = %s
                AND MONTH(holiday_date) = %s
                AND holiday_date <= %s
            """
            holiday_result = self.db.execute_query(holiday_query, (year, month, today), fetch=True)
            holidays = holiday_result[0]['count'] if holiday_result else 0
            
            working_days = days_in_month - holidays
            absent = max(0, working_days - present - leave)
            
            return {
                'present': present,
                'absent': absent,
                'leave': leave,
                'late': late
            }
        except Exception as e:
            print(f"Error getting monthly statistics: {e}")
            return {'present': 0, 'absent': 0, 'leave': 0, 'late': 0}

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
        
        # Get calendar data
        year = self.current_date.year
        month = self.current_date.month
        cal = calendar.monthcalendar(year, month)

        # Calendar rows
        for week in cal:
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
                    status = self.get_day_status(day_date, attendance_data, leave_data, holidays_data)
                    
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

    def get_day_status(self, day_date, attendance_data, leave_data, holidays_data):
        """Determine status for a specific day - FIXED TO SHOW 'On Leave'"""
        # Future dates - no status
        if day_date > date.today():
            return None
        
        # Check if it's a holiday
        if day_date in holidays_data:
            return ("Holiday", "#E0E7FF", "#3730A3")
        
        # Check if there's a leave request - SHOW "On Leave" instead of "Full Day"
        if day_date in leave_data:
            leave = leave_data[day_date]
            if leave['status'] == 'Approved':
                return ("On Leave", "#F3E8FF", "#6B21A8")  # Changed from "Full Day"
            elif leave['status'] == 'Pending':
                return ("Pending REQ", "#FEF3C7", "#92400E")
            elif leave['status'] == 'Rejected':
                return ("Rejected", "#FEE2E2", "#991B1B")
        
        # Check attendance
        if day_date in attendance_data:
            att = attendance_data[day_date]
            if att['status'] == 'present':
                return ("Present", "#DBEAFE", "#1E40AF")  # Changed from "Full Day"
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

        # Upcoming holidays card
        holidays_card = Frame(bottom_row, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        holidays_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        Label(
            holidays_card,
            text="Upcoming holidays",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=20, pady=(20, 15))

        # Get REAL holidays from database
        holidays = self.get_upcoming_holidays()
        
        if holidays:
            for holiday in holidays[:3]:  # Show max 3
                holiday_item = Frame(holidays_card, bg="white")
                holiday_item.pack(fill=tk.X, padx=20, pady=(0, 15))

                Label(
                    holiday_item,
                    text=holiday['name'],
                    font=("Segoe UI", 13, "bold"),
                    fg="#1F2937",
                    bg="white"
                ).pack(anchor=tk.W)

                Label(
                    holiday_item,
                    text=holiday['date_str'],
                    font=("Segoe UI", 10),
                    fg="#9CA3AF",
                    bg="white"
                ).pack(anchor=tk.W)
        else:
            Label(
                holidays_card,
                text="No upcoming holidays",
                font=("Segoe UI", 11),
                fg="#9CA3AF",
                bg="white"
            ).pack(padx=20, pady=10)

        # Working hours card - FIXED CALCULATION
        working_card = Frame(bottom_row, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        working_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 10))

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

        # Attendance summary card
        summary_card = Frame(bottom_row, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
        summary_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        Label(
            summary_card,
            text="Attendance summary",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=20, pady=(20, 15))

        # Get REAL attendance summary
        summary = self.get_attendance_summary()

        summary_items = [
            (str(summary['present']), "Present", "#10B981"),
            (str(summary['absent']), "Absent", "#EF4444"),
            (str(summary['leave']), "Leave", "#8B5CF6"),
            (str(summary['holidays']), "Holidays", "#F59E0B")
        ]

        items_grid = Frame(summary_card, bg="white")
        items_grid.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        for i, (count, label, color) in enumerate(summary_items):
            item_frame = Frame(items_grid, bg="white")
            if i < 2:
                item_frame.grid(row=0, column=i, padx=10, pady=10, sticky="w")
            else:
                item_frame.grid(row=1, column=i-2, padx=10, pady=10, sticky="w")

            count_label = Label(
                item_frame,
                text=count,
                font=("Segoe UI", 20, "bold"),
                fg="white",
                bg=color,
                width=3,
                height=1
            )
            count_label.pack()

            Label(
                item_frame,
                text=label,
                font=("Segoe UI", 11),
                fg="#6B7280",
                bg="white"
            ).pack(pady=(5, 0))

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
        """Calculate working hours for the current week - FIXED"""
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
            
            # Calculate absent (working days - present - leave)
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

        # Shift time from settings (can be made dynamic later)
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
            self.render()  # Refresh the view
        else:
            messagebox.showerror("Error", message)

    def clock_out(self):
        """Handle clock out"""
        success, message = self.db.clock_out(self.employee['id'])
        if success:
            messagebox.showinfo("Success", message)
            self.render()  # Refresh the view
        else:
            messagebox.showerror("Error", message)

    def create_announcements_card(self, parent):
        """Announcements card - showing work schedule"""
        card = Frame(parent, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=400)
        card.pack(fill=tk.X, pady=(0, 20))

        Label(
            card,
            text="Announcements",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(anchor=tk.W, padx=25, pady=(20, 15))

        # Get shift schedule from late_fee_settings
        schedule = self.get_work_schedule()

        announcements = [
            ("Work Schedule", f"Shift: {schedule['shift_start']} - {schedule['shift_end']}"),
            ("Grace Period", f"{schedule['grace_period']} minutes late allowed"),
        ]

        for title, detail in announcements:
            item = Frame(card, bg="#F9FAFB")
            item.pack(fill=tk.X, padx=25, pady=(0, 10))

            icon_label = Label(
                item,
                text="📢",
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
                text=title,
                font=("Segoe UI", 12, "bold"),
                fg="#1F2937",
                bg="#F9FAFB"
            ).pack(anchor=tk.W)

            Label(
                text_frame,
                text=detail,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="#F9FAFB"
            ).pack(anchor=tk.W)

        Frame(card, bg="white", height=20).pack()

    def get_work_schedule(self):
        """Get work schedule from late_fee_settings"""
        try:
            query = """
                SELECT standard_shift_start, grace_period_minutes
                FROM late_fee_settings
                WHERE is_active = 1
                ORDER BY id DESC
                LIMIT 1
            """
            result = self.db.execute_query(query, fetch=True)
            
            if result:
                shift_start = result[0]['standard_shift_start']
                grace_period = result[0]['grace_period_minutes']
                
                # Calculate shift end (assuming 8 hour shift)
                start_time = datetime.strptime(str(shift_start), "%H:%M:%S")
                end_time = start_time + timedelta(hours=8)
                
                return {
                    'shift_start': start_time.strftime("%I:%M %p"),
                    'shift_end': end_time.strftime("%I:%M %p"),
                    'grace_period': grace_period
                }
            else:
                return {
                    'shift_start': "9:00 AM",
                    'shift_end': "6:00 PM",
                    'grace_period': 10
                }
        except Exception as e:
            print(f"Error getting schedule: {e}")
            return {
                'shift_start': "9:00 AM",
                'shift_end': "6:00 PM",
                'grace_period': 10
            }

    def create_celebrations_card(self, parent):
        """Celebrations card - using demo data (can be made dynamic)"""
        card = Frame(parent, bg="white", highlightbackground="#E5E7EB", highlightthickness=1, width=400)
        card.pack(fill=tk.X, pady=(0, 20))

        header = Frame(card, bg="white")
        header.pack(fill=tk.X, padx=25, pady=(20, 15))

        Label(
            header,
            text="Celebrations",
            font=("Segoe UI", 18, "bold"),
            fg="#1F2937",
            bg="white"
        ).pack(side=tk.LEFT)

        celebrations = [
            ("Lydia Westervelt", "Birthday", "01", "Dec"),
            ("Ria Vetrovs", "Work Anniversary", "06", "Dec"),
            ("Kim Soo-hyun", "Marriage Anniversary", "08", "Dec")
        ]

        for name, event, day, month in celebrations:
            item = Frame(card, bg="white")
            item.pack(fill=tk.X, padx=25, pady=(0, 15))

            profile = Label(
                item,
                text="👤",
                font=("Segoe UI", 20),
                bg="#E5E7EB",
                width=2,
                height=1
            )
            profile.pack(side=tk.LEFT, padx=(0, 15))

            text_frame = Frame(item, bg="white")
            text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

            Label(
                text_frame,
                text=name,
                font=("Segoe UI", 12, "bold"),
                fg="#1F2937",
                bg="white"
            ).pack(anchor=tk.W)

            Label(
                text_frame,
                text=event,
                font=("Segoe UI", 10),
                fg="#6B7280",
                bg="white"
            ).pack(anchor=tk.W)

            date_badge = Frame(item, bg="#3B82F6")
            date_badge.pack(side=tk.RIGHT)

            Label(
                date_badge,
                text=day,
                font=("Segoe UI", 14, "bold"),
                fg="white",
                bg="#3B82F6",
                padx=10,
                pady=2
            ).pack()

            Label(
                date_badge,
                text=month,
                font=("Segoe UI", 9),
                fg="white",
                bg="#3B82F6",
                padx=10,
                pady=2
            ).pack()

        Frame(card, bg="white", height=20).pack()