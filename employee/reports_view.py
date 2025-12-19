import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import COLORS
from datetime import datetime, timedelta, date
from collections import defaultdict
import calendar
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

class ReportsView:
    def __init__(self, parent_frame, db, employee):
        self.parent_frame = parent_frame
        self.db = db
        self.employee = employee
        self.current_filter = "All Time"
        
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        self.render()
    
    def calculate_kpis(self):
        """Calculate KPI metrics"""
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT DATE(date) as date, status FROM attendance 
                WHERE employee_id = %s
            """, (self.employee['id'],))
            logs = cursor.fetchall()
            
            cursor.execute("""
                SELECT * FROM leave_requests 
                WHERE employee_id = %s AND status = 'approved'
            """, (self.employee['id'],))
            approved_leaves = cursor.fetchall()
            
            cursor.execute("""
                SELECT hire_date FROM employees WHERE id = %s
            """, (self.employee['id'],))
            employee_data = cursor.fetchone()
            cursor.close()
            
            present_days = sum(1 for log in logs if log['status'].lower().strip() == 'present')
            late_days = sum(1 for log in logs if log['status'].lower().strip() == 'late')
            leave_days = len(approved_leaves)
            
            today = date.today()
            
            if employee_data and employee_data['hire_date']:
                hire_date = employee_data['hire_date']
                if isinstance(hire_date, str):
                    employee_start_date = datetime.strptime(hire_date, "%Y-%m-%d").date()
                else:
                    employee_start_date = hire_date.date() if hasattr(hire_date, 'date') else hire_date
            else:
                employee_start_date = today
            
            current_date = employee_start_date
            working_days = 0
            
            while current_date <= today:
                if current_date.weekday() == 6:
                    current_date += timedelta(days=1)
                    continue
                
                cursor = self.db.connection.cursor(dictionary=True)
                cursor.execute("""
                    SELECT COUNT(*) as count FROM holidays
                    WHERE holiday_date = %s
                """, (current_date,))
                is_holiday = cursor.fetchone()['count'] > 0
                cursor.close()
                
                if not is_holiday:
                    working_days += 1
                
                current_date += timedelta(days=1)
            
            absent_days = max(0, working_days - present_days - late_days - leave_days)
            attendance_rate = ((present_days + late_days) / working_days * 100) if working_days > 0 else 0
            
            return {
                'present': present_days,
                'late': late_days,
                'absent': absent_days,
                'leave': leave_days,
                'rate': attendance_rate
            }
        except Exception as e:
            print(f"Error calculating KPIs: {e}")
            import traceback
            traceback.print_exc()
            return {'present': 0, 'late': 0, 'absent': 0, 'leave': 0, 'rate': 0}
    
    def get_week_label(self, date_obj):
        """Get week label in format 'Nov 24 - 30'"""
        start_of_week = date_obj - timedelta(days=date_obj.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        if start_of_week.month == end_of_week.month:
            return f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%d')}"
        else:
            return f"{start_of_week.strftime('%b %d')} - {end_of_week.strftime('%b %d')}"
    
    def get_month_label(self, date_obj):
        """Get month label in format 'November 2025'"""
        return date_obj.strftime('%B %Y')
    
    def get_weekly_attendance(self):
        """Get attendance data for the last 4 weeks"""
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT DATE(date) as date, status
                FROM attendance
                WHERE employee_id = %s
                ORDER BY date DESC
            """, (self.employee['id'],))
            logs = cursor.fetchall()
            cursor.close()
            
            weekly_data = defaultdict(lambda: {'present': 0, 'late': 0})
            
            for log in logs:
                date_obj = log['date']
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
                
                week_label = self.get_week_label(date_obj)
                
                if log['status'] == 'present':
                    weekly_data[week_label]['present'] += 1
                elif log['status'] == 'late':
                    weekly_data[week_label]['late'] += 1
            
            if weekly_data:
                sorted_weeks = sorted(weekly_data.keys(), 
                    key=lambda x: datetime.strptime(x.split(' - ')[0] + ' 2025', '%b %d %Y'))[-4:]
                return {week: weekly_data[week] for week in sorted_weeks}
            return {}
        except Exception as e:
            print(f"Error getting weekly attendance: {e}")
            import traceback
            traceback.print_exc()
            return {}

    def get_filter_options(self):
        """Get list of available months and weeks for filtering"""
        try:
            cursor = self.db.connection.cursor(dictionary=True)
            
            # Get employee hire date
            cursor.execute("""
                SELECT hire_date FROM employees WHERE id = %s
            """, (self.employee['id'],))
            employee_data = cursor.fetchone()
            
            # Get all attendance dates
            cursor.execute("""
                SELECT DISTINCT DATE(date) as date
                FROM attendance
                WHERE employee_id = %s
                ORDER BY date DESC
            """, (self.employee['id'],))
            logs = cursor.fetchall()
            cursor.close()
            
            months = set()
            weeks = set()
            
            # Add months and weeks from attendance logs
            for log in logs:
                date_obj = log['date']
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
                
                month_label = self.get_month_label(date_obj)
                months.add(month_label)
                
                week_label = self.get_week_label(date_obj)
                weeks.add(week_label)
            
            # Also add all months from hire date to today
            if employee_data and employee_data['hire_date']:
                hire_date = employee_data['hire_date']
                if isinstance(hire_date, str):
                    start_date = datetime.strptime(hire_date, "%Y-%m-%d").date()
                else:
                    start_date = hire_date.date() if hasattr(hire_date, 'date') else hire_date
                
                current_month = start_date.replace(day=1)
                today = date.today()
                
                while current_month <= today:
                    month_label = self.get_month_label(current_month)
                    months.add(month_label)
                    
                    # Move to next month
                    if current_month.month == 12:
                        current_month = current_month.replace(year=current_month.year + 1, month=1)
                    else:
                        current_month = current_month.replace(month=current_month.month + 1)
            
            sorted_months = sorted(list(months), 
                key=lambda x: datetime.strptime(x, '%B %Y'), reverse=True)
            sorted_weeks = sorted(list(weeks), 
                key=lambda x: datetime.strptime(x.split(' - ')[0] + ' 2025', '%b %d %Y'), reverse=True)
            
            return ["All Time"] + sorted_months + sorted_weeks
        except Exception as e:
            print(f"Error getting filter options: {e}")
            import traceback
            traceback.print_exc()
            return ["All Time"]

    def filter_logs_by_period(self, logs, period_label):
        """Filter logs by selected period"""
        if period_label == "All Time":
            return logs
        
        try:
            filtered = []
            for log in logs:
                date_obj = log['date']
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, "%Y-%m-%d").date()
                
                # Check if it's a month filter
                try:
                    filter_date = datetime.strptime(period_label, '%B %Y')
                    if date_obj.month == filter_date.month and date_obj.year == filter_date.year:
                        filtered.append(log)
                except:
                    # It's a week filter
                    log_week = self.get_week_label(date_obj)
                    if log_week == period_label:
                        filtered.append(log)
            
            return filtered
        except Exception as e:
            print(f"Error filtering logs: {e}")
            return logs
    
    def generate_absent_records(self, existing_logs, period_label, employee_data):
        """Generate absent records for working days without attendance"""
        try:
            # Determine the date range based on period
            try:
                filter_date = datetime.strptime(period_label, '%B %Y')
                # It's a month filter
                start_date = filter_date.replace(day=1).date()
                # Get last day of month
                if start_date.month == 12:
                    end_date = start_date.replace(year=start_date.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    end_date = start_date.replace(month=start_date.month + 1, day=1) - timedelta(days=1)
            except:
                # It's a week filter - parse week range
                parts = period_label.split(' - ')
                start_str = parts[0] + ' 2025'
                start_date = datetime.strptime(start_str, '%b %d %Y').date()
                end_date = start_date + timedelta(days=6)
            
            # Get employee hire date
            if employee_data and employee_data['hire_date']:
                hire_date = employee_data['hire_date']
                if isinstance(hire_date, str):
                    hire_date = datetime.strptime(hire_date, "%Y-%m-%d").date()
                else:
                    hire_date = hire_date.date() if hasattr(hire_date, 'date') else hire_date
                
                # Adjust start date to not be before hire date
                if start_date < hire_date:
                    start_date = hire_date
            
            # Don't show future dates
            today = date.today()
            if end_date > today:
                end_date = today
            
            # Create a set of dates that have attendance records
            attendance_dates = set()
            for log in existing_logs:
                log_date = log['date']
                if isinstance(log_date, str):
                    log_date = datetime.strptime(log_date, "%Y-%m-%d").date()
                attendance_dates.add(log_date)
            
            # Get approved leave dates - Try different column name variations
            cursor = self.db.connection.cursor(dictionary=True)
            
            # First, check what columns exist in leave_requests table
            try:
                cursor.execute("DESCRIBE leave_requests")
                columns_info = cursor.fetchall()
                column_names = [col['Field'] for col in columns_info]
                
                # Determine the correct column names
                start_col = None
                end_col = None
                
                for col in column_names:
                    if 'start' in col.lower():
                        start_col = col
                    if 'end' in col.lower():
                        end_col = col
                
                if start_col and end_col:
                    cursor.execute(f"""
                        SELECT {start_col}, {end_col} FROM leave_requests 
                        WHERE employee_id = %s AND status = 'approved'
                    """, (self.employee['id'],))
                    leave_requests = cursor.fetchall()
                    
                    leave_dates = set()
                    for leave in leave_requests:
                        leave_start = leave[start_col]
                        leave_end = leave[end_col]
                        
                        if isinstance(leave_start, str):
                            leave_start = datetime.strptime(leave_start, "%Y-%m-%d").date()
                        elif hasattr(leave_start, 'date'):
                            leave_start = leave_start.date()
                            
                        if isinstance(leave_end, str):
                            leave_end = datetime.strptime(leave_end, "%Y-%m-%d").date()
                        elif hasattr(leave_end, 'date'):
                            leave_end = leave_end.date()
                        
                        current = leave_start
                        while current <= leave_end:
                            leave_dates.add(current)
                            current += timedelta(days=1)
                else:
                    leave_dates = set()
            except Exception as e:
                print(f"Error getting leave dates: {e}")
                leave_dates = set()
            
            # Generate absent records
            all_records = list(existing_logs)
            current_date = start_date
            
            while current_date <= end_date:
                # Skip Sundays
                if current_date.weekday() != 6:
                    # Check if it's a holiday
                    cursor.execute("""
                        SELECT COUNT(*) as count FROM holidays
                        WHERE holiday_date = %s
                    """, (current_date,))
                    is_holiday = cursor.fetchone()['count'] > 0
                    
                    # If not a holiday, not on leave, and no attendance record, mark as absent
                    if not is_holiday and current_date not in leave_dates and current_date not in attendance_dates:
                        all_records.append({
                            'date': current_date,
                            'clock_in': None,
                            'clock_out': None,
                            'status': 'absent'
                        })
                
                current_date += timedelta(days=1)
            
            cursor.close()
            
            # Sort by date descending
            all_records.sort(key=lambda x: x['date'], reverse=True)
            return all_records
            
        except Exception as e:
            print(f"Error generating absent records: {e}")
            import traceback
            traceback.print_exc()
            return existing_logs
    
    def generate_pdf_report(self):
        """Generate PDF report of attendance"""
        try:
            # Ask user where to save the PDF
            filename = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
                initialfile=f"Attendance_Report_{self.employee.get('full_name', self.employee.get('username', 'Employee'))}_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
            
            if not filename:
                return
            
            # Create PDF
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            elements.append(Paragraph(f"Attendance Report", title_style))
            elements.append(Spacer(1, 0.2*inch))
            
            # Employee Info
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#2c3e50'),
                spaceAfter=6
            )
            
            employee_name = self.employee.get('full_name') or self.employee.get('username') or 'N/A'
            employee_id = self.employee.get('id', 'N/A')
            
            elements.append(Paragraph(f"<b>Employee Name:</b> {employee_name}", info_style))
            elements.append(Paragraph(f"<b>Employee ID:</b> {employee_id}", info_style))
            elements.append(Paragraph(f"<b>Report Period:</b> {self.current_filter}", info_style))
            elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", info_style))
            elements.append(Spacer(1, 0.3*inch))
            
            # KPI Summary
            kpis = self.calculate_kpis()
            
            kpi_data = [
                ['Metric', 'Value'],
                ['Total Present', str(kpis['present'])],
                ['Total Late', str(kpis['late'])],
                ['Total Absent', str(kpis['absent'])],
                ['Total Leave', str(kpis['leave'])],
                ['Attendance Rate', f"{kpis['rate']:.1f}%"]
            ]
            
            kpi_table = Table(kpi_data, colWidths=[3*inch, 2*inch])
            kpi_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            elements.append(Paragraph("<b>Summary Statistics</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            elements.append(kpi_table)
            elements.append(Spacer(1, 0.3*inch))
            
            # Attendance History
            elements.append(Paragraph("<b>Attendance History</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.1*inch))
            
            # Get ALL data for PDF (ignore current filter for comprehensive report)
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT DATE(date) as date, clock_in, clock_out, status
                FROM attendance
                WHERE employee_id = %s
                ORDER BY date DESC
            """, (self.employee['id'],))
            logs = cursor.fetchall()
            
            cursor.execute("""
                SELECT hire_date FROM employees WHERE id = %s
            """, (self.employee['id'],))
            employee_data = cursor.fetchone()
            
            # Get all months from hire date to now for comprehensive absent records
            if employee_data and employee_data['hire_date']:
                hire_date = employee_data['hire_date']
                if isinstance(hire_date, str):
                    start_date = datetime.strptime(hire_date, "%Y-%m-%d").date()
                else:
                    start_date = hire_date.date() if hasattr(hire_date, 'date') else hire_date
                
                # Generate comprehensive attendance including all absences
                all_records = []
                current_date = start_date
                today = date.today()
                
                # Create a set of dates with attendance
                attendance_dates = set()
                for log in logs:
                    log_date = log['date']
                    if isinstance(log_date, str):
                        log_date = datetime.strptime(log_date, "%Y-%m-%d").date()
                    attendance_dates.add(log_date)
                
                # Get leave dates
                try:
                    cursor.execute("DESCRIBE leave_requests")
                    columns_info = cursor.fetchall()
                    column_names = [col['Field'] for col in columns_info]
                    
                    start_col = None
                    end_col = None
                    for col in column_names:
                        if 'start' in col.lower():
                            start_col = col
                        if 'end' in col.lower():
                            end_col = col
                    
                    leave_dates = set()
                    if start_col and end_col:
                        cursor.execute(f"""
                            SELECT {start_col}, {end_col} FROM leave_requests 
                            WHERE employee_id = %s AND status = 'approved'
                        """, (self.employee['id'],))
                        leave_requests = cursor.fetchall()
                        
                        for leave in leave_requests:
                            leave_start = leave[start_col]
                            leave_end = leave[end_col]
                            
                            if isinstance(leave_start, str):
                                leave_start = datetime.strptime(leave_start, "%Y-%m-%d").date()
                            elif hasattr(leave_start, 'date'):
                                leave_start = leave_start.date()
                                
                            if isinstance(leave_end, str):
                                leave_end = datetime.strptime(leave_end, "%Y-%m-%d").date()
                            elif hasattr(leave_end, 'date'):
                                leave_end = leave_end.date()
                            
                            current = leave_start
                            while current <= leave_end:
                                leave_dates.add(current)
                                current += timedelta(days=1)
                except:
                    leave_dates = set()
                
                # Add all attendance records
                all_records.extend(logs)
                
                # Generate absent records for all working days
                while current_date <= today:
                    if current_date.weekday() != 6:  # Not Sunday
                        # Check if holiday
                        cursor.execute("""
                            SELECT COUNT(*) as count FROM holidays
                            WHERE holiday_date = %s
                        """, (current_date,))
                        is_holiday = cursor.fetchone()['count'] > 0
                        
                        if not is_holiday and current_date not in leave_dates and current_date not in attendance_dates:
                            all_records.append({
                                'date': current_date,
                                'clock_in': None,
                                'clock_out': None,
                                'status': 'absent'
                            })
                    
                    current_date += timedelta(days=1)
                
                # Sort by date descending
                all_records.sort(key=lambda x: x['date'], reverse=True)
            else:
                all_records = logs
            
            cursor.close()
            
            # Create attendance table
            attendance_data = [['Date', 'Clock In', 'Clock Out', 'Status']]
            
            for log in all_records:
                if log['clock_in']:
                    if isinstance(log['clock_in'], str):
                        clock_in = datetime.strptime(log['clock_in'], "%H:%M:%S").strftime("%I:%M %p")
                    else:
                        clock_in = log['clock_in'].strftime("%I:%M %p") if log['clock_in'] else "N/A"
                else:
                    clock_in = "N/A"
                
                if log['clock_out']:
                    if isinstance(log['clock_out'], str):
                        clock_out = datetime.strptime(log['clock_out'], "%H:%M:%S").strftime("%I:%M %p")
                    else:
                        clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "N/A"
                else:
                    clock_out = "N/A"
                
                attendance_data.append([
                    str(log['date']),
                    clock_in,
                    clock_out,
                    log['status'].capitalize()
                ])
            
            attendance_table = Table(attendance_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            attendance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#2c3e50')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
            ]))
            
            elements.append(attendance_table)
            
            # Build PDF
            doc.build(elements)
            
            messagebox.showinfo("Success", f"PDF report generated successfully!\n\nSaved to: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate PDF report:\n{str(e)}")
            print(f"Error generating PDF: {e}")
            import traceback
            traceback.print_exc()
    
    def create_kpi_card(self, parent, title, value, accent_color):
        """Create a minimal KPI card with left-aligned number and color accent"""
        card = tk.Frame(parent, bg='white', highlightbackground='#e0e0e0', 
                       highlightthickness=1)
        
        # Color accent bar on the left
        accent_bar = tk.Frame(card, bg=accent_color, width=4)
        accent_bar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Content area
        content = tk.Frame(card, bg='white')
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Title
        tk.Label(content, text=title, font=("Arial", 10),
                fg='#7f8c8d', bg='white', anchor=tk.W).pack(fill=tk.X, pady=(0, 5))
        
        # Value
        value_text = f"{value:.1f}%" if title == "Attendance Rate" else str(value)
        tk.Label(content, text=value_text, font=("Arial", 32, "bold"),
                fg='#2c3e50', bg='white', anchor=tk.W).pack(fill=tk.X)
        
        return card
    
    def create_chart(self, parent, data):
        """Create a simple bar chart"""
        chart_frame = tk.Frame(parent, bg='white', highlightbackground='#e0e0e0',
                              highlightthickness=1)
        
        # Header
        header = tk.Frame(chart_frame, bg='white')
        header.pack(fill=tk.X, padx=20, pady=15)
        
        tk.Label(header, text="Weekly Attendance Trend", 
                font=("Arial", 16, "bold"),
                fg='#2c3e50', bg='white').pack(side=tk.LEFT)
        
        # Canvas
        canvas_container = tk.Frame(chart_frame, bg='white')
        canvas_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        canvas = tk.Canvas(canvas_container, width=600, height=350, 
                          bg='white', highlightthickness=0)
        canvas.pack()
        
        if not data:
            canvas.create_text(300, 175, text="No attendance data yet",
                             font=("Arial", 14), fill='#95a5a6')
            return chart_frame
        
        self.draw_chart(canvas, data)
        
        return chart_frame
    
    def draw_chart(self, canvas, data):
        """Draw simple bar chart"""
        margin_left = 60
        margin_right = 40
        margin_top = 40
        margin_bottom = 60
        chart_width = 600 - margin_left - margin_right
        chart_height = 350 - margin_top - margin_bottom
        
        weeks = list(data.keys())
        if not weeks:
            return
            
        max_value = max(sum(d.values()) for d in data.values()) or 1
        max_value = int(max_value) + 1
        
        # Grid lines
        num_lines = min(max_value, 5)
        for i in range(num_lines + 1):
            y = margin_top + chart_height - (chart_height / num_lines) * i
            value = int((max_value / num_lines) * i)
            
            canvas.create_line(margin_left, y, 600 - margin_right, y,
                             fill='#e0e0e0', width=1)
            
            canvas.create_text(margin_left - 10, y, text=str(value),
                             font=("Arial", 9), fill='#7f8c8d',
                             anchor=tk.E)
        
        # Bars
        bar_group_width = chart_width / len(weeks)
        bar_width = bar_group_width * 0.35
        bar_spacing = bar_group_width * 0.1
        
        colors = {
            'present': '#4CAF50',
            'late': '#FF9800'
        }
        
        for week_idx, week in enumerate(weeks):
            week_data = data[week]
            
            group_center = margin_left + (week_idx + 0.5) * bar_group_width
            
            bar_index = 0
            for status in ['present', 'late']:
                count = week_data.get(status, 0)
                
                if count > 0:
                    x_offset = (bar_index - 0.5) * (bar_width + bar_spacing)
                    x1 = group_center + x_offset
                    x2 = x1 + bar_width
                    
                    bar_height = (count / max_value) * chart_height
                    y1 = margin_top + chart_height - bar_height
                    y2 = margin_top + chart_height
                    
                    canvas.create_rectangle(x1, y1, x2, y2,
                                          fill=colors[status], outline='')
                    
                    canvas.create_text((x1 + x2) / 2, y1 - 10,
                                     text=str(count), font=("Arial", 10, "bold"),
                                     fill='#2c3e50')
                
                bar_index += 1
            
            # Week label
            label_lines = week.split(' - ')
            canvas.create_text(group_center, 
                             margin_top + chart_height + 20,
                             text=label_lines[0], font=("Arial", 9),
                             fill='#2c3e50')
            canvas.create_text(group_center, 
                             margin_top + chart_height + 35,
                             text="- " + label_lines[1], font=("Arial", 9),
                             fill='#7f8c8d')
        
        # Legend
        legend_x = margin_left
        legend_y = 15
        
        for idx, (status, color) in enumerate(colors.items()):
            x = legend_x + (idx * 100)
            
            canvas.create_rectangle(x, legend_y, x + 15, legend_y + 15,
                                  fill=color, outline='')
            
            canvas.create_text(x + 25, legend_y + 7,
                             text=status.capitalize(), 
                             font=("Arial", 10),
                             fill='#2c3e50', anchor=tk.W)
    
    def on_filter_change(self, event, tree, empty_label, employee_data):
        """Handle filter dropdown change"""
        selected_period = self.filter_var.get()
        self.current_filter = selected_period
        
        for item in tree.get_children():
            tree.delete(item)
        
        cursor = self.db.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT DATE(date) as date, clock_in, clock_out, status
            FROM attendance
            WHERE employee_id = %s
            ORDER BY date DESC
        """, (self.employee['id'],))
        logs = cursor.fetchall()
        cursor.close()
        
        filtered_logs = self.filter_logs_by_period(logs, selected_period)
        
        # Generate absent days if filtering by specific period (not "All Time")
        if selected_period != "All Time":
            all_records = self.generate_absent_records(filtered_logs, selected_period, employee_data)
        else:
            all_records = filtered_logs
        
        if all_records:
            # Hide empty label and show tree
            empty_label.pack_forget()
            tree.pack(fill=tk.BOTH, expand=True)
            
            for idx, log in enumerate(all_records):
                if log['clock_in']:
                    if isinstance(log['clock_in'], str):
                        clock_in = datetime.strptime(log['clock_in'], "%H:%M:%S").strftime("%I:%M %p")
                    else:
                        clock_in = log['clock_in'].strftime("%I:%M %p") if log['clock_in'] else "N/A"
                else:
                    clock_in = "N/A"
                
                if log['clock_out']:
                    if isinstance(log['clock_out'], str):
                        clock_out = datetime.strptime(log['clock_out'], "%H:%M:%S").strftime("%I:%M %p")
                    else:
                        clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "N/A"
                else:
                    clock_out = "N/A"
                
                tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                tree.insert("", tk.END, values=(
                    log['date'],
                    clock_in,
                    clock_out,
                    log['status'].capitalize()
                ), tags=(tag,))
        else:
            # Show empty label and hide tree
            tree.pack_forget()
            empty_label.pack(expand=True, pady=50)
    
    def render(self):
        try:
            # Header
            header_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
            header_frame.pack(fill=tk.X, pady=(0, 20))
            
            tk.Label(header_frame, text="My Attendance Reports", 
                    font=("Arial", 24, "bold"), 
                    fg=COLORS['text_dark'], 
                    bg=COLORS['bg_main']).pack(side=tk.LEFT)
            
            # Export PDF Button
            export_btn = tk.Button(header_frame, text="Export to PDF",
                                  font=("Arial", 11, "bold"),
                                  bg='#3498db', fg='white',
                                  padx=20, pady=8,
                                  relief=tk.FLAT,
                                  cursor='hand2',
                                  command=self.generate_pdf_report)
            export_btn.pack(side=tk.RIGHT)
            
            # KPI Cards
            kpis = self.calculate_kpis()
            kpi_container = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
            kpi_container.pack(fill=tk.X, pady=(0, 20))
            
            card_data = [
                ("Total Present", kpis['present'], '#4CAF50'),
                ("Total Late", kpis['late'], '#FF9800'),
                ("Total Absent", kpis['absent'], '#9C27B0'),
                ("Total Leave", kpis['leave'], '#E91E63'),
                ("Attendance Rate", kpis['rate'], '#2196F3')
            ]
            
            for i, (title, value, color) in enumerate(card_data):
                card = self.create_kpi_card(kpi_container, title, value, color)
                card.grid(row=0, column=i, padx=8, sticky="nsew")
                kpi_container.grid_columnconfigure(i, weight=1)
            
            kpi_container.grid_rowconfigure(0, minsize=100)
            
            # Content Container
            content_container = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
            content_container.pack(fill=tk.BOTH, expand=True)
            
            left_frame = tk.Frame(content_container, bg='white',
                                 highlightbackground='#e0e0e0', highlightthickness=1)
            left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
            
            right_frame = tk.Frame(content_container, bg='white')
            right_frame.grid(row=0, column=1, sticky="nsew")
            
            content_container.grid_columnconfigure(0, weight=1)
            content_container.grid_columnconfigure(1, weight=1)
            content_container.grid_rowconfigure(0, weight=1)
            
            # History Header
            history_header = tk.Frame(left_frame, bg='white')
            history_header.pack(fill=tk.X, padx=20, pady=15)
            
            tk.Label(history_header, text="Attendance History", 
                    font=("Arial", 16, "bold"),
                    fg='#2c3e50', bg='white').pack(side=tk.LEFT)
            
            filter_frame = tk.Frame(history_header, bg='white')
            filter_frame.pack(side=tk.RIGHT)
            
            tk.Label(filter_frame, text="Filter:", font=("Arial", 10),
                    fg='#7f8c8d', bg='white').pack(side=tk.LEFT, padx=(0, 10))
            
            self.filter_var = tk.StringVar(value="All Time")
            filter_options = self.get_filter_options()
            
            filter_dropdown = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                        values=filter_options, state='readonly',
                                        width=18, font=("Arial", 10))
            filter_dropdown.pack(side=tk.LEFT)
            
            # Table
            table_container = tk.Frame(left_frame, bg='white')
            table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
            
            columns = ("Date", "Clock In", "Clock Out", "Status")
            tree = ttk.Treeview(table_container, columns=columns, show="headings", height=15)
            
            style = ttk.Style()
            style.theme_use("clam")
            style.configure("Treeview", 
                        background='white',
                        foreground='#2c3e50',
                        fieldbackground='white',
                        rowheight=35,
                        font=("Arial", 10))
            style.configure("Treeview.Heading", 
                        background='#f8f9fa',
                        foreground='#2c3e50',
                        font=("Arial", 11, "bold"))
            style.map('Treeview', background=[('selected', '#E3F2FD')])
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, anchor=tk.CENTER)
            
            scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscroll=scrollbar.set)
            
            cursor = self.db.connection.cursor(dictionary=True)
            cursor.execute("""
                SELECT DATE(date) as date, clock_in, clock_out, status
                FROM attendance
                WHERE employee_id = %s
                ORDER BY date DESC
            """, (self.employee['id'],))
            logs = cursor.fetchall()
            
            # Get employee hire date for absent record generation
            cursor.execute("""
                SELECT hire_date FROM employees WHERE id = %s
            """, (self.employee['id'],))
            employee_data = cursor.fetchone()
            cursor.close()
            
            # Add empty state label (hidden by default)
            empty_label = tk.Label(table_container, 
                                  text="No attendance records for this period",
                                  font=("Arial", 12),
                                  fg='#95a5a6', bg='white')
            
            # For initial load, show all records (no absent generation for "All Time")
            all_records = logs
            
            if all_records:
                for idx, log in enumerate(all_records):
                    if log['clock_in']:
                        if isinstance(log['clock_in'], str):
                            clock_in = datetime.strptime(log['clock_in'], "%H:%M:%S").strftime("%I:%M %p")
                        else:
                            clock_in = log['clock_in'].strftime("%I:%M %p") if log['clock_in'] else "N/A"
                    else:
                        clock_in = "N/A"
                    
                    if log['clock_out']:
                        if isinstance(log['clock_out'], str):
                            clock_out = datetime.strptime(log['clock_out'], "%H:%M:%S").strftime("%I:%M %p")
                        else:
                            clock_out = log['clock_out'].strftime("%I:%M %p") if log['clock_out'] else "Active"
                    else:
                        clock_out = "Active"
                    
                    tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                    tree.insert("", tk.END, values=(
                        log['date'],
                        clock_in,
                        clock_out,
                        log['status'].capitalize()
                    ), tags=(tag,))
            else:
                # No records at all - show empty state
                scrollbar.pack_forget()
                tree.pack_forget()
                empty_label.pack(expand=True, pady=50)
            
            tree.tag_configure('evenrow', background='#f8f9fa')
            tree.tag_configure('oddrow', background='white')
            
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)
            
            # Pass employee_data to the filter change handler
            filter_dropdown.bind('<<ComboboxSelected>>', 
                               lambda e: self.on_filter_change(e, tree, empty_label, employee_data))
            
            # Weekly Chart
            weekly_data = self.get_weekly_attendance()
            chart = self.create_chart(right_frame, weekly_data)
            chart.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            print(f"Error rendering reports view: {e}")
            import traceback
            traceback.print_exc()