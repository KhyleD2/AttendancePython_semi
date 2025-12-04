"""
Late Fee Calculator Module
Handles all late fee calculations and related operations
"""
from datetime import datetime, time, timedelta
from decimal import Decimal

class LateFeeCalculator:
    def __init__(self, db):
        """Initialize with database connection"""
        self.db = db
    
    def get_late_fee_settings(self):
        """Retrieve current late fee settings"""
        # FIXED: Use is_active = 1 instead of TRUE for MySQL compatibility
        query = "SELECT * FROM late_fee_settings WHERE is_active = 1 ORDER BY id DESC LIMIT 1"
        result = self.db.execute_query(query, fetch=True)
        return result[0] if result else None
    
    def calculate_minutes_late(self, clock_in_time, settings=None):
        """
        Calculate how many minutes late an employee is
        
        Args:
            clock_in_time: datetime object of when employee clocked in
            settings: late fee settings (optional, will fetch if not provided)
        
        Returns:
            int: minutes late (0 if not late)
        """
        if settings is None:
            settings = self.get_late_fee_settings()
        
        if not settings:
            print("DEBUG - No settings found!")
            return 0
        
        # Get standard start time
        standard_start_time = settings['standard_shift_start']
        
        print(f"DEBUG - Standard start time: {standard_start_time}, type: {type(standard_start_time)}")
        print(f"DEBUG - Clock in time: {clock_in_time}")
        
        # FIXED: Handle timedelta (MySQL TIME columns return as timedelta)
        if isinstance(standard_start_time, timedelta):
            total_seconds = int(standard_start_time.total_seconds())
            hour_24 = total_seconds // 3600
            minute = (total_seconds % 3600) // 60
            standard_time = time(hour_24, minute)
            standard_datetime = datetime.combine(clock_in_time.date(), standard_time)
        elif isinstance(standard_start_time, time):
            standard_datetime = datetime.combine(clock_in_time.date(), standard_start_time)
        elif isinstance(standard_start_time, str):
            # Parse string time like "08:00:00"
            time_parts = standard_start_time.split(':')
            standard_time = time(int(time_parts[0]), int(time_parts[1]))
            standard_datetime = datetime.combine(clock_in_time.date(), standard_time)
        else:
            standard_datetime = standard_start_time
        
        print(f"DEBUG - Standard datetime: {standard_datetime}")
        
        # Calculate difference
        if clock_in_time > standard_datetime:
            time_diff = clock_in_time - standard_datetime
            minutes_late = int(time_diff.total_seconds() / 60)
            
            print(f"DEBUG - Raw minutes late: {minutes_late}")
            
            # Apply grace period
            grace_period = settings.get('grace_period_minutes', 0)
            print(f"DEBUG - Grace period: {grace_period}")
            
            if minutes_late <= grace_period:
                print(f"DEBUG - Within grace period, returning 0")
                return 0
            
            result = minutes_late - grace_period
            print(f"DEBUG - Final minutes late (after grace): {result}")
            return result
        
        print(f"DEBUG - Not late, clock in time <= standard time")
        return 0
    
    def calculate_late_fee(self, minutes_late, settings=None):
        """
        Calculate the late fee amount based on minutes late
        
        Args:
            minutes_late: int, number of minutes late
            settings: late fee settings (optional)
        
        Returns:
            Decimal: late fee amount
        """
        if minutes_late <= 0:
            return Decimal('0.00')
        
        if settings is None:
            settings = self.get_late_fee_settings()
        
        if not settings:
            return Decimal('0.00')
        
        fee_type = settings.get('fee_type', 'fixed')
        
        print(f"DEBUG - Calculating fee: {minutes_late} mins, type: {fee_type}")
        
        if fee_type == 'fixed':
            fee = Decimal(str(settings.get('fixed_fee_amount', 50.00)))
            print(f"DEBUG - Fixed fee: {fee}")
            return fee
        
        elif fee_type == 'per_minute':
            per_minute = Decimal(str(settings.get('per_minute_fee', 5.00)))
            fee = per_minute * Decimal(minutes_late)
            print(f"DEBUG - Per minute fee: {fee}")
            return fee
        
        elif fee_type == 'tiered':
            return self._calculate_tiered_fee(minutes_late)
        
        return Decimal('0.00')
    
    def _calculate_tiered_fee(self, minutes_late):
        """Calculate fee based on tiered structure"""
        # Default tiered structure if no custom tiers are defined
        if minutes_late <= 10:
            return Decimal('0.00')
        elif minutes_late <= 30:
            return Decimal('25.00')
        elif minutes_late <= 60:
            return Decimal('50.00')
        elif minutes_late <= 120:
            return Decimal('100.00')
        else:
            return Decimal('200.00')
    
    def process_late_attendance(self, attendance_id, employee_id, clock_in_time):
        """
        Process late attendance: calculate and save late fee
        
        Args:
            attendance_id: ID of the attendance record
            employee_id: ID of the employee
            clock_in_time: datetime when employee clocked in
        
        Returns:
            dict: {'success': bool, 'minutes_late': int, 'late_fee': Decimal, 'message': str}
        """
        try:
            print(f"\n=== Processing Late Attendance ===")
            print(f"Attendance ID: {attendance_id}")
            print(f"Employee ID: {employee_id}")
            print(f"Clock in time: {clock_in_time}")
            
            settings = self.get_late_fee_settings()
            
            if not settings:
                print("ERROR - Late fee settings not configured")
                return {
                    'success': False,
                    'minutes_late': 0,
                    'late_fee': Decimal('0.00'),
                    'message': 'Late fee settings not configured'
                }
            
            print(f"Settings loaded: {settings}")
            
            # Calculate minutes late
            minutes_late = self.calculate_minutes_late(clock_in_time, settings)
            print(f"Minutes late calculated: {minutes_late}")
            
            # Calculate fee
            late_fee = self.calculate_late_fee(minutes_late, settings)
            print(f"Late fee calculated: {late_fee}")
            
            # Update attendance record
            if minutes_late > 0:
                query = """UPDATE attendance 
                           SET minutes_late = %s, 
                               late_fee_amount = %s,
                               status = 'late'
                           WHERE id = %s"""
                result = self.db.execute_query(query, (minutes_late, float(late_fee), attendance_id))
                print(f"Update result: {result}")
                
                return {
                    'success': True,
                    'minutes_late': minutes_late,
                    'late_fee': late_fee,
                    'message': f'Late by {minutes_late} minutes. Fee: ₱{late_fee:.2f}'
                }
            else:
                print("Employee is on time")
                return {
                    'success': True,
                    'minutes_late': 0,
                    'late_fee': Decimal('0.00'),
                    'message': 'On time'
                }
                
        except Exception as e:
            print(f"ERROR processing late attendance: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'minutes_late': 0,
                'late_fee': Decimal('0.00'),
                'message': f'Error: {str(e)}'
            }
    
    def get_employee_late_fee_summary(self, employee_id):
        """Get summary of late fees for an employee"""
        query = """SELECT 
                    COUNT(CASE WHEN late_fee_amount > 0 THEN 1 END) as total_late_instances,
                    SUM(late_fee_amount) as total_late_fees,
                    SUM(CASE WHEN late_fee_paid = 1 THEN late_fee_amount ELSE 0 END) as total_paid,
                    SUM(CASE WHEN late_fee_paid = 0 THEN late_fee_amount ELSE 0 END) as total_unpaid
                   FROM attendance 
                   WHERE employee_id = %s"""
        result = self.db.execute_query(query, (employee_id,), fetch=True)
        
        if result:
            row = result[0]
            # Handle both dict and tuple results
            if isinstance(row, dict):
                return {
                    'total_late_instances': row['total_late_instances'] or 0,
                    'total_late_fees': float(row['total_late_fees'] or 0),
                    'total_paid': float(row['total_paid'] or 0),
                    'total_unpaid': float(row['total_unpaid'] or 0)
                }
            elif isinstance(row, tuple):
                return {
                    'total_late_instances': row[0] or 0,
                    'total_late_fees': float(row[1] or 0),
                    'total_paid': float(row[2] or 0),
                    'total_unpaid': float(row[3] or 0)
                }
        return None
    
    def mark_late_fee_paid(self, attendance_id, payment_method='Cash', notes=''):
        """Mark a late fee as paid"""
        try:
            # Get attendance details
            query = "SELECT employee_id, late_fee_amount FROM attendance WHERE id = %s"
            result = self.db.execute_query(query, (attendance_id,), fetch=True)
            
            if not result:
                return False
            
            row = result[0]
            if isinstance(row, dict):
                emp_id = row['employee_id']
                amount = row['late_fee_amount']
            elif isinstance(row, tuple):
                emp_id = row[0]
                amount = row[1]
            else:
                return False
            
            # Update attendance
            update_query = "UPDATE attendance SET late_fee_paid = 1 WHERE id = %s"
            self.db.execute_query(update_query, (attendance_id,))
            
            # Record payment
            payment_query = """INSERT INTO late_fee_payments 
                              (attendance_id, employee_id, amount_paid, payment_date, payment_method, notes, created_at)
                              VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            self.db.execute_query(payment_query, (
                attendance_id, emp_id, amount, datetime.now().date(),
                payment_method, notes, datetime.now()
            ))
            
            return True
        except Exception as e:
            print(f"Error marking late fee as paid: {e}")
            return False