import tkinter as tk
from tkinter import Canvas
import math
from datetime import datetime, timedelta
from config import COLORS

class ReportsView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.selected_departments = set()  # Track selected departments
        self.department_checkboxes = {}  # Store checkbox variables
        self.render()
    
    def get_all_departments(self):
        """Fetch unique departments from database"""
        try:
            # First check if employees table has data
            count_result = self.db.execute_query("SELECT COUNT(*) as count FROM employees", fetch=True)
            count = count_result[0]['count'] if count_result else 0
            print(f"Total employees in database: {count}")
            
            # Check departments
            query = "SELECT DISTINCT department FROM employees WHERE department IS NOT NULL AND department != '' ORDER BY department"
            result = self.db.execute_query(query, fetch=True)
            departments = [row['department'] for row in result] if result else []
            
            # If no departments in DB, return default list
            if not departments:
                print("WARNING: No departments found in database, using defaults")
                print("Make sure employees have department values assigned!")
                return ["IT", "HR", "Finance", "Sales", "Marketing", "Operations"]
            
            print(f"Found departments: {departments}")
            return departments
        except Exception as e:
            print(f"Error fetching departments: {e}")
            import traceback
            traceback.print_exc()
            return ["IT", "HR", "Finance", "Sales", "Marketing", "Operations"]
    
    def get_filtered_employees(self):
        """Get employees based on selected departments"""
        if self.selected_departments:
            placeholders = ','.join(['%s'] * len(self.selected_departments))
            query = f"SELECT * FROM employees WHERE department IN ({placeholders})"
            return self.db.execute_query(query, tuple(self.selected_departments), fetch=True)
        else:
            # Show all employees when no filter is selected
            return self.db.execute_query("SELECT * FROM employees", fetch=True)
    
    def get_attendance_stats(self):
        """Calculate attendance statistics for filtered departments"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Total employees
            if self.selected_departments:
                placeholders = ','.join(['%s'] * len(self.selected_departments))
                total_query = f"SELECT COUNT(*) as count FROM employees WHERE department IN ({placeholders})"
                total_result = self.db.execute_query(total_query, tuple(self.selected_departments), fetch=True)
            else:
                total_result = self.db.execute_query("SELECT COUNT(*) as count FROM employees", fetch=True)
            
            total_employees = total_result[0]['count'] if total_result else 0
            print(f"Total employees: {total_employees}")
            
            # Present today
            if self.selected_departments:
                placeholders = ','.join(['%s'] * len(self.selected_departments))
                present_query = f"""
                    SELECT COUNT(DISTINCT e.id) as count
                    FROM employees e 
                    INNER JOIN attendance a ON e.id = a.employee_id 
                    WHERE a.date = %s AND a.status = 'present' AND e.department IN ({placeholders})
                """
                params = [today] + list(self.selected_departments)
                present_result = self.db.execute_query(present_query, tuple(params), fetch=True)
            else:
                present_query = """
                    SELECT COUNT(DISTINCT e.id) as count
                    FROM employees e 
                    INNER JOIN attendance a ON e.id = a.employee_id 
                    WHERE a.date = %s AND a.status = 'present'
                """
                present_result = self.db.execute_query(present_query, (today,), fetch=True)
            
            present_today = present_result[0]['count'] if present_result else 0
            print(f"Present today: {present_today}")
            
            # Absent today
            absent_today = total_employees - present_today
            
            # Attendance rate
            attendance_rate = (present_today / total_employees * 100) if total_employees > 0 else 0
            
            return {
                'total': total_employees,
                'present': present_today,
                'absent': absent_today,
                'rate': f"{attendance_rate:.1f}%"
            }
        except Exception as e:
            print(f"Error in get_attendance_stats: {e}")
            import traceback
            traceback.print_exc()
            return {'total': 0, 'present': 0, 'absent': 0, 'rate': '0.0%'}
    
    def get_department_distribution(self):
        """Get employee count by department"""
        try:
            if self.selected_departments:
                placeholders = ','.join(['%s'] * len(self.selected_departments))
                query = f"SELECT department, COUNT(*) as count FROM employees WHERE department IN ({placeholders}) GROUP BY department"
                result = self.db.execute_query(query, tuple(self.selected_departments), fetch=True)
            else:
                query = "SELECT department, COUNT(*) as count FROM employees GROUP BY department"
                result = self.db.execute_query(query, fetch=True)
            
            if not result:
                return []
            
            # Assign colors
            colors = ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#06B6D4"]
            return [(row['department'], row['count'], colors[i % len(colors)]) for i, row in enumerate(result)]
        except Exception as e:
            print(f"Error in get_department_distribution: {e}")
            return []
    
    def get_weekly_attendance(self):
        """Get attendance for last 7 days"""
        try:
            days = []
            attendance = []
            
            for i in range(6, -1, -1):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                day_name = (datetime.now() - timedelta(days=i)).strftime('%a')
                
                if self.selected_departments:
                    placeholders = ','.join(['%s'] * len(self.selected_departments))
                    query = f"""
                        SELECT COUNT(DISTINCT e.id) as count
                        FROM employees e 
                        INNER JOIN attendance a ON e.id = a.employee_id 
                        WHERE a.date = %s AND a.status = 'present' AND e.department IN ({placeholders})
                    """
                    params = [date] + list(self.selected_departments)
                    result = self.db.execute_query(query, tuple(params), fetch=True)
                else:
                    query = """
                        SELECT COUNT(DISTINCT e.id) as count
                        FROM employees e 
                        INNER JOIN attendance a ON e.id = a.employee_id 
                        WHERE a.date = %s AND a.status = 'present'
                    """
                    result = self.db.execute_query(query, (date,), fetch=True)
                
                count = result[0]['count'] if result else 0
                
                days.append(day_name)
                attendance.append(count)
            
            return days, attendance
        except Exception as e:
            print(f"Error in get_weekly_attendance: {e}")
            return ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], [0, 0, 0, 0, 0, 0, 0]
    
    def get_monthly_trend(self):
        """Get attendance rate for last 4 months"""
        try:
            rates = []
            months = []
            
            # Get total employees for rate calculation
            if self.selected_departments:
                placeholders = ','.join(['%s'] * len(self.selected_departments))
                total_query = f"SELECT COUNT(*) as count FROM employees WHERE department IN ({placeholders})"
                total_result = self.db.execute_query(total_query, tuple(self.selected_departments), fetch=True)
            else:
                total_result = self.db.execute_query("SELECT COUNT(*) as count FROM employees", fetch=True)
            
            total_emp = total_result[0]['count'] if total_result else 0
            
            month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            for i in range(3, -1, -1):
                # Calculate the target month
                target_date = datetime.now() - timedelta(days=30*i)
                month_start = target_date.replace(day=1).strftime('%Y-%m-%d')
                
                # Calculate last day of month
                if target_date.month == 12:
                    month_end = target_date.replace(day=31).strftime('%Y-%m-%d')
                else:
                    next_month = target_date.replace(month=target_date.month + 1, day=1)
                    month_end = (next_month - timedelta(days=1)).strftime('%Y-%m-%d')
                
                if self.selected_departments:
                    placeholders = ','.join(['%s'] * len(self.selected_departments))
                    query = f"""
                        SELECT COUNT(*) as count
                        FROM attendance a 
                        INNER JOIN employees e ON e.id = a.employee_id 
                        WHERE a.date BETWEEN %s AND %s AND a.status = 'present' AND e.department IN ({placeholders})
                    """
                    params = [month_start, month_end] + list(self.selected_departments)
                    result = self.db.execute_query(query, tuple(params), fetch=True)
                else:
                    query = """
                        SELECT COUNT(*) as count
                        FROM attendance a 
                        INNER JOIN employees e ON e.id = a.employee_id 
                        WHERE a.date BETWEEN %s AND %s AND a.status = 'present'
                    """
                    result = self.db.execute_query(query, (month_start, month_end), fetch=True)
                
                present_count = result[0]['count'] if result else 0
                
                # Calculate working days in this month
                days_query = "SELECT COUNT(DISTINCT date) as count FROM attendance WHERE date BETWEEN %s AND %s"
                days_result = self.db.execute_query(days_query, (month_start, month_end), fetch=True)
                days_count = days_result[0]['count'] if days_result else 1
                
                rate = (present_count / (total_emp * days_count) * 100) if total_emp > 0 and days_count > 0 else 0
                
                # Get month name
                month_name = month_names[target_date.month - 1]
                months.append(month_name)
                rates.append(min(100, rate))
            
            return months, rates
        except Exception as e:
            print(f"Error in get_monthly_trend: {e}")
            import traceback
            traceback.print_exc()
            return ["Sep", "Oct", "Nov", "Dec"], [0, 0, 0, 0]
    
    def get_top_performers(self):
        """Get top 5 employees by attendance rate"""
        try:
            if self.selected_departments:
                placeholders = ','.join(['%s'] * len(self.selected_departments))
                query = f"""
                    SELECT e.first_name, e.last_name, e.department, 
                           ROUND(COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / COUNT(a.id), 1) as rate
                    FROM employees e
                    LEFT JOIN attendance a ON e.id = a.employee_id
                    WHERE e.department IN ({placeholders})
                    GROUP BY e.id, e.first_name, e.last_name, e.department
                    HAVING COUNT(a.id) > 0
                    ORDER BY rate DESC
                    LIMIT 5
                """
                result = self.db.execute_query(query, tuple(self.selected_departments), fetch=True)
            else:
                query = """
                    SELECT e.first_name, e.last_name, e.department, 
                           ROUND(COUNT(CASE WHEN a.status = 'present' THEN 1 END) * 100.0 / COUNT(a.id), 1) as rate
                    FROM employees e
                    LEFT JOIN attendance a ON e.id = a.employee_id
                    GROUP BY e.id, e.first_name, e.last_name, e.department
                    HAVING COUNT(a.id) > 0
                    ORDER BY rate DESC
                    LIMIT 5
                """
                result = self.db.execute_query(query, fetch=True)
            
            if not result:
                return []
            
            # Assign colors based on rate
            def get_color(rate):
                if rate >= 95:
                    return "#10B981"  # Green
                elif rate >= 85:
                    return "#3B82F6"  # Blue
                elif rate >= 75:
                    return "#F59E0B"  # Orange
                else:
                    return "#6B7280"  # Gray
            
            return [(f"{row['first_name']} {row['last_name']}", 
                    row['department'], 
                    f"{row['rate']:.1f}%",
                    get_color(row['rate'])) 
                    for row in result]
        except Exception as e:
            print(f"Error in get_top_performers: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def on_department_change(self):
        """Called when checkbox is toggled"""
        # Update selected departments
        self.selected_departments = {
            dept for dept, var in self.department_checkboxes.items() if var.get()
        }
        
        print(f"Selected departments: {self.selected_departments}")
        
        # Refresh the entire view
        self.refresh_view()
    
    def refresh_view(self):
        """Refresh all charts and statistics"""
        # Clear the parent frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # Re-render with updated data
        self.render()
    
    def render(self):
        # --- Background ---
        self.parent_frame.configure(bg="#F0F2F5")

        # --- Header with blue background ---
        header_frame = tk.Frame(self.parent_frame, bg="#4A90E2")
        header_frame.pack(fill=tk.X, pady=(0, 20), padx=0)

        tk.Label(
            header_frame,
            text="Reports & Analytics",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg="#4A90E2"
        ).pack(side=tk.LEFT, padx=40, pady=20)

        # --- Department Filter Section ---
        filter_frame = tk.Frame(self.parent_frame, bg="white")
        filter_frame.pack(fill=tk.X, padx=40, pady=(0, 20))

        tk.Label(
            filter_frame,
            text="Filter by Department:",
            font=("Segoe UI", 12, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(side=tk.LEFT, padx=20, pady=15)

        # Get all departments
        all_departments = self.get_all_departments()
        
        # Create checkboxes for each department
        checkbox_container = tk.Frame(filter_frame, bg="white")
        checkbox_container.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=15)

        for dept in all_departments:
            if dept not in self.department_checkboxes:
                var = tk.BooleanVar(value=dept in self.selected_departments)
                self.department_checkboxes[dept] = var
            else:
                var = self.department_checkboxes[dept]
            
            cb = tk.Checkbutton(
                checkbox_container,
                text=dept,
                variable=var,
                font=("Segoe UI", 10),
                bg="white",
                activebackground="white",
                command=self.on_department_change
            )
            cb.pack(side=tk.LEFT, padx=10)

        # Clear All / Select All buttons
        btn_frame = tk.Frame(filter_frame, bg="white")
        btn_frame.pack(side=tk.RIGHT, padx=20)

        tk.Button(
            btn_frame,
            text="Select All",
            font=("Segoe UI", 9),
            bg="#4A90E2",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.select_all_departments
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Clear All",
            font=("Segoe UI", 9),
            bg="#6B7280",
            fg="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.clear_all_departments
        ).pack(side=tk.LEFT, padx=5)

        # --- Scrollable container ---
        main_canvas = Canvas(self.parent_frame, bg="#F0F2F5", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.parent_frame, orient="vertical", command=main_canvas.yview)
        scrollable_frame = tk.Frame(main_canvas, bg="#F0F2F5")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )

        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=1400)
        main_canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=40)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        container = scrollable_frame

        # --- Get dynamic data ---
        stats = self.get_attendance_stats()

        # --- Stats Cards Row ---
        stats_row = tk.Frame(container, bg="#F0F2F5")
        stats_row.pack(fill=tk.X, pady=(0, 20))

        stats_data = [
            ("Total Employees", str(stats['total']), "#3B82F6"),
            ("Present Today", str(stats['present']), "#10B981"),
            ("Absent Today", str(stats['absent']), "#EF4444"),
            ("Attendance Rate", stats['rate'], "#8B5CF6")
        ]

        for i, (title, value, color) in enumerate(stats_data):
            self.create_stat_card(stats_row, title, value, color, i)

        # --- First Row: Donut Chart + Weekly Trend ---
        row1 = tk.Frame(container, bg="#F0F2F5")
        row1.pack(fill=tk.X, pady=(0, 20))

        # Department Distribution Donut Chart
        donut_card = tk.Frame(row1, bg="white")
        donut_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            donut_card,
            text="Department Distribution",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        dept_data = self.get_department_distribution()
        self.create_department_donut(donut_card, dept_data)

        # Weekly Attendance Trend Bar Chart
        weekly_card = tk.Frame(row1, bg="white")
        weekly_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            weekly_card,
            text="Weekly Attendance Trend",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        days, attendance = self.get_weekly_attendance()
        self.create_weekly_bar_chart(weekly_card, days, attendance)

        # --- Second Row: Monthly Line Chart + Top Performers ---
        row2 = tk.Frame(container, bg="#F0F2F5")
        row2.pack(fill=tk.X, pady=(0, 20))

        # Monthly Attendance Line Chart
        monthly_card = tk.Frame(row2, bg="white")
        monthly_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        tk.Label(
            monthly_card,
            text="Monthly Attendance Trend",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        months, rates = self.get_monthly_trend()
        self.create_monthly_line_chart(monthly_card, months, rates)

        # Top Performers
        top_card = tk.Frame(row2, bg="white")
        top_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        tk.Label(
            top_card,
            text="Top 5 Best Attendance",
            font=("Segoe UI", 16, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(pady=(20, 10))

        top_employees = self.get_top_performers()
        self.create_top_performers(top_card, top_employees)

    def select_all_departments(self):
        """Select all department checkboxes"""
        for var in self.department_checkboxes.values():
            var.set(True)
        self.on_department_change()
    
    def clear_all_departments(self):
        """Clear all department checkboxes"""
        for var in self.department_checkboxes.values():
            var.set(False)
        self.on_department_change()

    def create_stat_card(self, parent, title, value, color, index):
        card = tk.Frame(parent, bg="white", highlightthickness=0)
        card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0 if index == 0 else 10, 0))

        color_bar = tk.Frame(card, bg=color, width=4)
        color_bar.pack(side=tk.LEFT, fill=tk.Y)

        content = tk.Frame(card, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(
            content,
            text=title,
            font=("Segoe UI", 11),
            fg="#6B7280",
            bg="white"
        ).pack(anchor=tk.W)

        tk.Label(
            content,
            text=value,
            font=("Segoe UI", 28, "bold"),
            fg="#1a1a1a",
            bg="white"
        ).pack(anchor=tk.W, pady=(5, 0))

    def create_department_donut(self, parent, departments):
        if not departments:
            tk.Label(
                parent,
                text="No data available",
                font=("Segoe UI", 12),
                fg="#6B7280",
                bg="white"
            ).pack(pady=50)
            return

        chart_frame = tk.Frame(parent, bg="white")
        chart_frame.pack(pady=20)

        total = sum(count for _, count, _ in departments)

        # Canvas for donut
        canvas = Canvas(chart_frame, width=300, height=300, bg="white", highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=30)

        center_x, center_y = 150, 150
        radius = 110
        inner_radius = 70

        # Draw donut segments
        start_angle = 0
        for dept, count, color in departments:
            extent = (count / total) * 360
            self.draw_donut_arc(canvas, center_x, center_y, radius, inner_radius, 
                               start_angle, extent, color)
            start_angle += extent

        # Center text
        canvas.create_text(
            center_x, center_y - 10,
            text=str(total),
            font=("Segoe UI", 32, "bold"),
            fill="#1a1a1a"
        )
        canvas.create_text(
            center_x, center_y + 20,
            text="Employees",
            font=("Segoe UI", 12),
            fill="#6B7280"
        )

        # Legend
        legend_frame = tk.Frame(chart_frame, bg="white")
        legend_frame.pack(side=tk.LEFT, padx=20, pady=20)

        for dept, count, color in departments:
            item_frame = tk.Frame(legend_frame, bg="white")
            item_frame.pack(anchor=tk.W, pady=8)

            # Color box
            color_box = tk.Frame(item_frame, bg=color, width=16, height=16)
            color_box.pack(side=tk.LEFT, padx=(0, 10))

            # Department name and count
            tk.Label(
                item_frame,
                text=f"{dept}",
                font=("Segoe UI", 11, "bold"),
                fg="#1a1a1a",
                bg="white"
            ).pack(side=tk.LEFT)

            tk.Label(
                item_frame,
                text=f"({count})",
                font=("Segoe UI", 11),
                fg="#6B7280",
                bg="white"
            ).pack(side=tk.LEFT, padx=(5, 0))

    def create_weekly_bar_chart(self, parent, days, attendance):
        canvas = Canvas(parent, width=600, height=340, bg="white", highlightthickness=0)
        canvas.pack(pady=20, padx=30)

        # Chart dimensions
        margin_left = 60
        margin_right = 40
        margin_top = 40
        margin_bottom = 60
        chart_width = 600 - margin_left - margin_right
        chart_height = 240
        max_value = max(attendance) + 5 if attendance and max(attendance) > 0 else 10
        bar_width = (chart_width / len(days)) * 0.7

        # Draw grid lines
        for i in range(5):
            y = margin_top + (chart_height / 4) * i
            canvas.create_line(
                margin_left, y, 
                margin_left + chart_width, y,
                fill="#E5E7EB", width=1, dash=(2, 2)
            )
            # Y-axis labels
            value = int(max_value - (max_value / 4) * i)
            canvas.create_text(
                margin_left - 10, y,
                text=str(value),
                font=("Segoe UI", 9),
                fill="#6B7280",
                anchor="e"
            )

        # Draw bars with gradient effect
        for i, (day, value) in enumerate(zip(days, attendance)):
            x_center = margin_left + (i + 0.5) * (chart_width / len(days))
            x = x_center - bar_width / 2
            bar_height = (value / max_value) * chart_height if max_value > 0 else 0
            y = margin_top + chart_height - bar_height

            # Shadow effect
            canvas.create_rectangle(
                x + 2, y + 2, x + bar_width + 2, margin_top + chart_height + 2,
                fill="#D1D5DB", outline=""
            )

            # Main bar with gradient colors
            colors = ["#60A5FA", "#3B82F6", "#2563EB", "#1D4ED8"]
            bar_color = colors[i % len(colors)]
            
            canvas.create_rectangle(
                x, y, x + bar_width, margin_top + chart_height,
                fill=bar_color, outline="", width=0
            )

            # Highlight effect on top
            canvas.create_rectangle(
                x, y, x + bar_width, y + 3,
                fill="#93C5FD", outline=""
            )

            # Value on top with background
            text_y = y - 15 if y > 50 else y + 15
            canvas.create_rectangle(
                x_center - 15, text_y - 8,
                x_center + 15, text_y + 8,
                fill="#1E3A8A", outline=""
            )
            canvas.create_text(
                x_center, text_y,
                text=str(value),
                font=("Segoe UI", 10, "bold"),
                fill="white"
            )

            # Day label
            canvas.create_text(
                x_center, margin_top + chart_height + 20,
                text=day,
                font=("Segoe UI", 11, "bold"),
                fill="#374151"
            )

        # Y-axis label
        canvas.create_text(
            20, margin_top + chart_height / 2,
            text="Employees",
            font=("Segoe UI", 10, "bold"),
            fill="#6B7280",
            angle=90
        )

    def create_monthly_line_chart(self, parent, months, rates):
        canvas = Canvas(parent, width=600, height=340, bg="white", highlightthickness=0)
        canvas.pack(pady=20, padx=30)

        # Chart dimensions
        margin_left = 60
        margin_right = 40
        margin_top = 40
        margin_bottom = 60
        chart_width = 600 - margin_left - margin_right
        chart_height = 240

        # Draw grid lines
        for i in range(5):
            y = margin_top + (chart_height / 4) * i
            canvas.create_line(
                margin_left, y,
                margin_left + chart_width, y,
                fill="#E5E7EB", width=1, dash=(2, 2)
            )
            # Y-axis labels (percentage)
            value = 100 - (25 * i)
            canvas.create_text(
                margin_left - 10, y,
                text=f"{value}%",
                font=("Segoe UI", 9),
                fill="#6B7280",
                anchor="e"
            )

        # Calculate points
        points = []
        for i, rate in enumerate(rates):
            x = margin_left + (i / (len(rates) - 1)) * chart_width if len(rates) > 1 else margin_left + chart_width / 2
            y = margin_top + chart_height - (rate / 100) * chart_height
            points.append((x, y))

        # Draw gradient area under line
        if len(points) > 1:
            area_points = [(points[0][0], margin_top + chart_height)]
            area_points.extend(points)
            area_points.append((points[-1][0], margin_top + chart_height))
            
            flat_area = [coord for point in area_points for coord in point]
            canvas.create_polygon(
                flat_area,
                fill="#D1FAE5",
                outline="",
                smooth=True
            )

        # Draw line with shadow
        if len(points) > 1:
            for i in range(len(points) - 1):
                # Shadow
                canvas.create_line(
                    points[i][0] + 2, points[i][1] + 2,
                    points[i+1][0] + 2, points[i+1][1] + 2,
                    fill="#9CA3AF", width=3, smooth=True
                )
                # Main line
                canvas.create_line(
                    points[i][0], points[i][1],
                    points[i+1][0], points[i+1][1],
                    fill="#10B981", width=4, smooth=True
                )

        # Draw points, labels, and trend indicators
        for i, (point, rate, month) in enumerate(zip(points, rates, months)):
            # Outer glow circle
            canvas.create_oval(
                point[0]-10, point[1]-10,
                point[0]+10, point[1]+10,
                fill="#D1FAE5", outline=""
            )
            
            # Main circle
            canvas.create_oval(
                point[0]-7, point[1]-7,
                point[0]+7, point[1]+7,
                fill="#10B981", outline="white", width=3
            )

            # Rate value with background
            text_y = point[1] - 25
            canvas.create_rectangle(
                point[0] - 25, text_y - 10,
                point[0] + 25, text_y + 10,
                fill="#059669", outline=""
            )
            canvas.create_text(
                point[0], text_y,
                text=f"{rate:.0f}%",
                font=("Segoe UI", 11, "bold"),
                fill="white"
            )

            # Trend indicator (if not first point)
            if i > 0:
                prev_rate = rates[i-1]
                if rate > prev_rate:
                    # Up arrow
                    canvas.create_text(
                        point[0], text_y + 20,
                        text="↑",
                        font=("Segoe UI", 14, "bold"),
                        fill="#10B981"
                    )
                elif rate < prev_rate:
                    # Down arrow
                    canvas.create_text(
                        point[0], text_y + 20,
                        text="↓",
                        font=("Segoe UI", 14, "bold"),
                        fill="#EF4444"
                    )

            # Month label
            canvas.create_text(
                point[0], margin_top + chart_height + 20,
                text=month,
                font=("Segoe UI", 11, "bold"),
                fill="#374151"
            )

        # Y-axis label
        canvas.create_text(
            20, margin_top + chart_height / 2,
            text="Attendance %",
            font=("Segoe UI", 10, "bold"),
            fill="#6B7280",
            angle=90
        )

    def create_top_performers(self, parent, employees):
        if not employees:
            tk.Label(
                parent,
                text="No data available",
                font=("Segoe UI", 12),
                fg="#6B7280",
                bg="white"
            ).pack(pady=50)
            return

        list_frame = tk.Frame(parent, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        for i, employee_data in enumerate(employees, 1):
            name, dept, rate, color = employee_data
            
            row = tk.Frame(list_frame, bg="white", highlightbackground="#E5E7EB", highlightthickness=1)
            row.pack(fill=tk.X, pady=6, ipady=3)

            # Left section: Rank badge
            rank_frame = tk.Frame(row, bg="white")
            rank_frame.pack(side=tk.LEFT, padx=15)
            
            # Rank circle with gradient effect
            rank_canvas = Canvas(rank_frame, width=40, height=40, bg="white", highlightthickness=0)
            rank_canvas.pack()
            
            # Outer circle (shadow)
            rank_canvas.create_oval(2, 2, 38, 38, fill="#D1D5DB", outline="")
            # Inner circle with color
            rank_canvas.create_oval(0, 0, 36, 36, fill=color, outline="")
            # Rank number
            rank_canvas.create_text(
                18, 18,
                text=f"{i}",
                font=("Segoe UI", 16, "bold"),
                fill="white"
            )

            # Middle section: Employee info
            info_frame = tk.Frame(row, bg="white")
            info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

            # Name with icon
            name_container = tk.Frame(info_frame, bg="white")
            name_container.pack(anchor=tk.W)
            
            tk.Label(
                name_container,
                text="👤",
                font=("Segoe UI", 12),
                bg="white"
            ).pack(side=tk.LEFT, padx=(0, 5))
            
            tk.Label(
                name_container,
                text=name,
                font=("Segoe UI", 12, "bold"),
                fg="#1F2937",
                bg="white"
            ).pack(side=tk.LEFT)

            # Department only
            dept_container = tk.Frame(info_frame, bg="white")
            dept_container.pack(anchor=tk.W, pady=(2, 0))
            
            tk.Label(
                dept_container,
                text=f"📊 {dept}",
                font=("Segoe UI", 9),
                fg="#6B7280",
                bg="white"
            ).pack(side=tk.LEFT)

            # Right section: Rate badge with progress bar
            right_frame = tk.Frame(row, bg="white")
            right_frame.pack(side=tk.RIGHT, padx=15)

            # Rate badge
            badge = tk.Frame(right_frame, bg=color)
            badge.pack(anchor=tk.E)

            tk.Label(
                badge,
                text=rate,
                font=("Segoe UI", 14, "bold"),
                fg="white",
                bg=color
            ).pack(padx=15, pady=10)

            # Mini progress bar
            progress_canvas = Canvas(right_frame, width=100, height=6, bg="white", highlightthickness=0)
            progress_canvas.pack(pady=(3, 0))
            
            # Background bar
            progress_canvas.create_rectangle(0, 0, 100, 6, fill="#E5E7EB", outline="")
            # Progress bar
            rate_value = float(rate.replace('%', ''))
            progress_width = rate_value
            progress_canvas.create_rectangle(0, 0, progress_width, 6, fill=color, outline="")

    def draw_donut_arc(self, canvas, center_x, center_y, radius, inner_radius, start_angle, extent, color):
        if extent <= 0:
            return

        start_rad = math.radians(start_angle - 90)
        end_rad = math.radians(start_angle + extent - 90)

        points = []
        steps = max(2, int(extent / 2))
        
        for i in range(steps + 1):
            angle = start_rad + (end_rad - start_rad) * i / steps
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((x, y))

        for i in range(steps, -1, -1):
            angle = start_rad + (end_rad - start_rad) * i / steps
            x = center_x + inner_radius * math.cos(angle)
            y = center_y + inner_radius * math.sin(angle)
            points.append((x, y))

        flat_points = [coord for point in points for coord in point]
        canvas.create_polygon(flat_points, fill=color, outline=color, smooth=True)