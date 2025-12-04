import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS
from datetime import time, timedelta

class SettingsView:
    def __init__(self, parent_frame, db):
        self.parent_frame = parent_frame
        self.db = db
        self.entries = {}
        self.ensure_settings_exist()  # NEW: Make sure settings row exists
        self.render()
    
    def ensure_settings_exist(self):
        """Ensure at least one settings row exists in the database"""
        try:
            # Check if any settings exist
            check_query = "SELECT COUNT(*) FROM late_fee_settings WHERE is_active = 1"
            result = self.db.execute_query(check_query, fetch=True)
            
            # Handle both tuple and dict results
            if isinstance(result[0], dict):
                count = result[0].get('COUNT(*)', 0) if result and result[0] else 0
            elif isinstance(result[0], tuple):
                count = result[0][0] if result and result[0] else 0
            else:
                count = 0
            
            if count == 0:
                # Insert default settings if none exist
                insert_query = """
                    INSERT INTO late_fee_settings 
                    (standard_shift_start, grace_period_minutes, fee_type, 
                     fixed_fee_amount, per_minute_fee, is_active, created_at, updated_at)
                    VALUES ('08:00:00', 10, 'fixed', 50.00, 5.00, 1, NOW(), NOW())
                """
                self.db.execute_query(insert_query)
                print("✓ Default settings created in database")
        except Exception as e:
            print(f"Error ensuring settings exist: {e}")
    
    def render(self):
        # Clear existing widgets
        for widget in self.parent_frame.winfo_children():
            widget.destroy()
        
        # --- Background ---
        self.parent_frame.configure(bg=COLORS['bg_main'])
        
        # --- Header ---
        header_frame = tk.Frame(self.parent_frame, bg="#072446")
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(header_frame, text="⚙ Late Fee Settings", 
                 font=("Segoe UI", 26, "bold"), 
                 fg="white", bg="#072446").pack(side=tk.LEFT, padx=40, pady=20)
        
        # --- Main Container with Scrollbar ---
        main_container = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=(0, 20))
        
        # Canvas for scrolling
        canvas = tk.Canvas(main_container, bg=COLORS['bg_main'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['bg_main'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # --- Settings Card ---
        card = tk.Frame(scrollable_frame, bg="white", padx=60, pady=40)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Load current settings
        self.load_current_settings()
        
        # --- Time Settings Section ---
        self.create_section_header(card, "⏰ Time Settings", 0)
        
        self.create_time_input_12hour(card, "Standard Clock-In Time", "shift_start", 1, 
                               "Time employees should clock in")
        
        self.create_input(card, "Grace Period (minutes)", "grace_period", 2,
                         "Minutes allowed before marking as late (e.g., 10)")
        
        # --- Late Fee Settings Section ---
        self.create_section_header(card, "💰 Late Fee Configuration", 3)
        
        # Fee Type Selection
        fee_type_frame = tk.Frame(card, bg="white")
        fee_type_frame.grid(row=4, column=0, columnspan=2, sticky="w", padx=15, pady=15)
        
        tk.Label(fee_type_frame, text="Fee Type:", 
                 font=("Segoe UI", 11, "bold"), 
                 fg=COLORS['text_dark'], bg="white").pack(side=tk.LEFT, padx=(0, 20))
        
        self.fee_type_var = tk.StringVar(value=self.current_settings.get('fee_type', 'fixed'))
        
        tk.Radiobutton(fee_type_frame, text="Fixed Amount", 
                      variable=self.fee_type_var, value='fixed',
                      font=("Segoe UI", 10), bg="white",
                      command=self.on_fee_type_change).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(fee_type_frame, text="Per Minute", 
                      variable=self.fee_type_var, value='per_minute',
                      font=("Segoe UI", 10), bg="white",
                      command=self.on_fee_type_change).pack(side=tk.LEFT, padx=10)
        
        tk.Radiobutton(fee_type_frame, text="Tiered", 
                      variable=self.fee_type_var, value='tiered',
                      font=("Segoe UI", 10), bg="white",
                      command=self.on_fee_type_change).pack(side=tk.LEFT, padx=10)
        
        # Fee Amount Inputs
        self.create_input(card, "Fixed Fee Amount (₱)", "fixed_fee", 5,
                         "Amount charged per late instance")
        
        self.create_input(card, "Per Minute Fee (₱)", "per_minute_fee", 6,
                         "Amount charged per minute late")
        
        # Tiered Info
        tiered_info_frame = tk.Frame(card, bg="#f7f9fa", padx=15, pady=15)
        tiered_info_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        
        tk.Label(tiered_info_frame, 
                text="ℹ️ Tiered Fee Structure:\n" +
                     "• 11-30 mins late: ₱25  • 31-60 mins late: ₱50\n" +
                     "• 1-2 hours late: ₱100  • 2+ hours late: ₱200",
                font=("Segoe UI", 9), fg="#555", bg="#f7f9fa", 
                justify=tk.LEFT).pack(anchor="w")
        
        # --- Action Buttons ---
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.grid(row=8, column=0, columnspan=2, pady=(30, 20), sticky="ew", padx=15)
        
        # Center the buttons
        btn_container = tk.Frame(btn_frame, bg="white")
        btn_container.pack(anchor="center")
        
        tk.Button(btn_container, text="Reset to Default", 
                 font=("Segoe UI", 12, "bold"),
                 bg="#6c757d", fg="white",
                 activebackground="#5a6268", activeforeground="white",
                 relief=tk.FLAT, cursor="hand2",
                 padx=30, pady=15,
                 command=self.reset_to_default).pack(side=tk.LEFT, padx=10)
        
        tk.Button(btn_container, text="💾 Save Settings", 
                 font=("Segoe UI", 12, "bold"),
                 bg="#10B981", fg="white",
                 activebackground="#059669", activeforeground="white",
                 relief=tk.FLAT, cursor="hand2",
                 padx=30, pady=15,
                 command=self.save_settings).pack(side=tk.LEFT, padx=10)
        
        # NOW populate fields after all widgets are created
        self.populate_fields()
        
        # Update input states based on fee type
        self.on_fee_type_change()
        
        # Scroll to top
        canvas.yview_moveto(0)
    
    def create_section_header(self, parent, text, row):
        tk.Label(parent, text=text,
                font=("Segoe UI", 14, "bold"),
                fg=COLORS['text_dark'], bg="white").grid(
                    row=row, column=0, columnspan=2, 
                    sticky="w", padx=15, pady=(20, 15))
    
    def create_input(self, parent, label_text, key, row, placeholder=""):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        
        # Label
        tk.Label(frame, text=label_text,
                font=("Segoe UI", 10, "bold"),
                fg="#1a1a1a", bg="white").pack(anchor="w", pady=(0, 8))
        
        # Input wrapper
        wrapper = tk.Frame(frame, bg="#F3F4F6", padx=12, pady=10)
        wrapper.pack(fill=tk.X)
        
        entry = tk.Entry(wrapper, font=("Segoe UI", 11), 
                        bg="#F3F4F6", bd=0)
        entry.pack(fill=tk.X)
        
        # Add placeholder if provided
        if placeholder:
            tk.Label(frame, text=placeholder, 
                    font=("Segoe UI", 9), 
                    fg="#999", bg="white").pack(anchor="w", pady=(3, 0))
        
        self.entries[key] = entry
    
    def create_time_input_12hour(self, parent, label_text, key, row, placeholder=""):
        frame = tk.Frame(parent, bg="white")
        frame.grid(row=row, column=0, columnspan=2, sticky="ew", padx=15, pady=10)
        
        # Label
        tk.Label(frame, text=label_text,
                font=("Segoe UI", 10, "bold"),
                fg="#1a1a1a", bg="white").pack(anchor="w", pady=(0, 8))
        
        # Time input wrapper
        time_wrapper = tk.Frame(frame, bg="#F3F4F6", padx=15, pady=12)
        time_wrapper.pack(fill=tk.X)
        
        # Time input frame
        time_frame = tk.Frame(time_wrapper, bg="#F3F4F6")
        time_frame.pack(anchor="w")
        
        # Hour dropdown (1-12)
        tk.Label(time_frame, text="Hour:", font=("Segoe UI", 10),
                bg="#F3F4F6", fg="#666").pack(side=tk.LEFT, padx=(0, 5))
        
        hour_var = tk.StringVar()
        hour_combo = ttk.Combobox(time_frame, textvariable=hour_var, 
                                  width=5, state="readonly",
                                  font=("Segoe UI", 11))
        hour_combo['values'] = [str(i) for i in range(1, 13)]
        hour_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # Minute dropdown (00-59)
        tk.Label(time_frame, text="Minute:", font=("Segoe UI", 10),
                bg="#F3F4F6", fg="#666").pack(side=tk.LEFT, padx=(0, 5))
        
        minute_var = tk.StringVar()
        minute_combo = ttk.Combobox(time_frame, textvariable=minute_var,
                                    width=5, state="readonly",
                                    font=("Segoe UI", 11))
        minute_combo['values'] = [f"{i:02d}" for i in range(0, 60, 5)]
        minute_combo.pack(side=tk.LEFT, padx=(0, 15))
        
        # AM/PM dropdown
        tk.Label(time_frame, text="Period:", font=("Segoe UI", 10),
                bg="#F3F4F6", fg="#666").pack(side=tk.LEFT, padx=(0, 5))
        
        period_var = tk.StringVar()
        period_combo = ttk.Combobox(time_frame, textvariable=period_var,
                                    width=5, state="readonly",
                                    font=("Segoe UI", 11))
        period_combo['values'] = ['AM', 'PM']
        period_combo.pack(side=tk.LEFT)
        
        # Store the variables
        self.entries[f"{key}_hour"] = hour_var
        self.entries[f"{key}_minute"] = minute_var
        self.entries[f"{key}_period"] = period_var
        
        if placeholder:
            tk.Label(frame, text=placeholder, 
                    font=("Segoe UI", 9), 
                    fg="#999", bg="white").pack(anchor="w", pady=(3, 0))
    
    def load_current_settings(self):
        """Load current settings from database"""
        # Use is_active = 1 for MySQL compatibility (tinyint)
        query = """SELECT id, standard_shift_start, grace_period_minutes, 
                          fee_type, fixed_fee_amount, per_minute_fee, 
                          is_active, created_at, updated_at
                   FROM late_fee_settings 
                   WHERE is_active = 1 
                   ORDER BY id DESC LIMIT 1"""
        result = self.db.execute_query(query, fetch=True)
        
        print(f"DEBUG - Load Settings Raw Result: {result}")  # Debug print
        
        if result and len(result) > 0:
            row = result[0]
            print(f"DEBUG - Row type: {type(row)}, Row content: {row}")  # Debug print
            
            # Handle both tuple and dict results
            if isinstance(row, dict):
                self.current_settings = row
            elif isinstance(row, tuple):
                # Map tuple to dict using column order from SELECT
                self.current_settings = {
                    'id': row[0],
                    'standard_shift_start': row[1],
                    'grace_period_minutes': row[2],
                    'fee_type': row[3],
                    'fixed_fee_amount': row[4],
                    'per_minute_fee': row[5],
                    'is_active': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                }
            else:
                self.current_settings = row
            
            print(f"DEBUG - Loaded settings: {self.current_settings}")  # Debug print
    
    def populate_fields(self):
        """Populate input fields with current settings - IMMEDIATE, NO DELAY"""
        # Parse shift start time
        shift_start = self.current_settings.get('standard_shift_start')
        
        print(f"DEBUG - Populating with shift_start: {shift_start}, type: {type(shift_start)}")  # Debug
        
        # Handle timedelta (MySQL TIME columns return as timedelta)
        if isinstance(shift_start, timedelta):
            total_seconds = int(shift_start.total_seconds())
            hour_24 = total_seconds // 3600
            minute = (total_seconds % 3600) // 60
        elif isinstance(shift_start, str):
            parts = shift_start.split(':')
            hour_24 = int(parts[0])
            minute = int(parts[1])
        elif isinstance(shift_start, time):
            hour_24 = shift_start.hour
            minute = shift_start.minute
        else:
            hour_24 = 8
            minute = 0
        
        # Convert to 12-hour format
        if hour_24 == 0:
            hour_12 = 12
            period = "AM"
        elif hour_24 < 12:
            hour_12 = hour_24
            period = "AM"
        elif hour_24 == 12:
            hour_12 = 12
            period = "PM"
        else:
            hour_12 = hour_24 - 12
            period = "PM"
        
        print(f"DEBUG - Setting time to: {hour_12}:{minute:02d} {period}")  # Debug
        
        # Set time values IMMEDIATELY
        self.entries['shift_start_hour'].set(str(hour_12))
        self.entries['shift_start_minute'].set(f"{minute:02d}")
        self.entries['shift_start_period'].set(period)
        
        # Set other values IMMEDIATELY
        self.entries['grace_period'].delete(0, tk.END)
        self.entries['grace_period'].insert(0, str(self.current_settings.get('grace_period_minutes', 10)))
        
        self.entries['fixed_fee'].delete(0, tk.END)
        self.entries['fixed_fee'].insert(0, str(self.current_settings.get('fixed_fee_amount', 50.00)))
        
        self.entries['per_minute_fee'].delete(0, tk.END)
        self.entries['per_minute_fee'].insert(0, str(self.current_settings.get('per_minute_fee', 5.00)))
    
    def on_fee_type_change(self):
        """Handle fee type change"""
        fee_type = self.fee_type_var.get()
        
        # Enable/disable inputs based on fee type
        if fee_type == 'fixed':
            self.entries['fixed_fee'].config(state='normal')
            self.entries['per_minute_fee'].config(state='disabled')
        elif fee_type == 'per_minute':
            self.entries['fixed_fee'].config(state='disabled')
            self.entries['per_minute_fee'].config(state='normal')
        else:  # tiered
            self.entries['fixed_fee'].config(state='disabled')
            self.entries['per_minute_fee'].config(state='disabled')
    
    def save_settings(self):
        """Save settings to database with confirmation"""
        try:
            # Get time values (these are StringVar objects)
            hour_12_str = self.entries['shift_start_hour'].get()
            minute_str = self.entries['shift_start_minute'].get()
            period = self.entries['shift_start_period'].get()
            
            if not hour_12_str or not minute_str or not period:
                messagebox.showerror("Error", "Please select all time fields (Hour, Minute, and AM/PM)")
                return
            
            hour_12 = int(hour_12_str)
            minute = int(minute_str)
            
            # Get other values (these are Entry widgets)
            grace_period_str = self.entries['grace_period'].get().strip()
            fixed_fee_str = self.entries['fixed_fee'].get().strip()
            per_minute_fee_str = self.entries['per_minute_fee'].get().strip()
            
            if not grace_period_str:
                messagebox.showerror("Error", "Please enter a grace period")
                return
            
            grace_period = int(grace_period_str)
            fixed_fee = float(fixed_fee_str) if fixed_fee_str else 0.0
            per_minute_fee = float(per_minute_fee_str) if per_minute_fee_str else 0.0
            fee_type = self.fee_type_var.get()
            
            # Validate grace period
            if grace_period < 0:
                messagebox.showerror("Error", "Grace period must be 0 or greater")
                return
            
            # Convert to 24-hour format
            if period == "AM":
                hour_24 = hour_12 if hour_12 != 12 else 0
            else:  # PM
                hour_24 = hour_12 if hour_12 == 12 else hour_12 + 12
            
            shift_time = f"{hour_24:02d}:{minute:02d}:00"
            
            print(f"DEBUG - Saving: {shift_time}, grace: {grace_period}, type: {fee_type}")  # Debug
            
            # Confirmation dialog
            time_str = f"{hour_12}:{minute:02d} {period}"
            confirm_msg = f"Save these settings?\n\n"
            confirm_msg += f"⏰ Clock-In Time: {time_str}\n"
            confirm_msg += f"⏱️ Grace Period: {grace_period} minutes\n"
            confirm_msg += f"💰 Fee Type: {fee_type.replace('_', ' ').title()}\n"
            
            if fee_type == 'fixed':
                confirm_msg += f"💵 Fixed Fee: ₱{fixed_fee:.2f}"
            elif fee_type == 'per_minute':
                confirm_msg += f"💵 Per Minute Fee: ₱{per_minute_fee:.2f}"
            else:
                confirm_msg += "💵 Using Tiered Fee Structure"
            
            if not messagebox.askyesno("Confirm Save", confirm_msg):
                return
            
            # Check if a row exists first
            check_query = "SELECT COUNT(*) as count FROM late_fee_settings WHERE is_active = 1"
            check_result = self.db.execute_query(check_query, fetch=True)
            
            # Handle both tuple and dict results for count check
            if isinstance(check_result[0], dict):
                row_exists = check_result[0]['count'] > 0 if check_result and check_result[0] else False
            elif isinstance(check_result[0], tuple):
                row_exists = check_result[0][0] > 0 if check_result and check_result[0] else False
            else:
                row_exists = False
            
            if row_exists:
                # Update existing row
                query = """UPDATE late_fee_settings 
                           SET standard_shift_start = %s,
                               grace_period_minutes = %s,
                               fee_type = %s,
                               fixed_fee_amount = %s,
                               per_minute_fee = %s,
                               updated_at = NOW()
                           WHERE is_active = 1"""
                
                result = self.db.execute_query(query, (
                    shift_time, grace_period, fee_type, 
                    fixed_fee, per_minute_fee
                ))
            else:
                # Insert new row if none exists
                query = """INSERT INTO late_fee_settings 
                           (standard_shift_start, grace_period_minutes, fee_type, 
                            fixed_fee_amount, per_minute_fee, is_active, created_at, updated_at)
                           VALUES (%s, %s, %s, %s, %s, 1, NOW(), NOW())"""
                
                result = self.db.execute_query(query, (
                    shift_time, grace_period, fee_type, 
                    fixed_fee, per_minute_fee
                ))
            
            print(f"DEBUG - Save result: {result}")  # Debug
            
            if result is not False:
                messagebox.showinfo("✓ Success", "Settings saved successfully!")
                # Reload from database and update fields WITHOUT re-rendering
                self.load_current_settings()
                self.populate_fields()
            else:
                messagebox.showerror("Error", "Failed to save settings")
                
        except ValueError as e:
            messagebox.showerror("Error", "Please enter valid numbers for grace period and fee amounts")
            print(f"DEBUG - ValueError: {e}")  # Debug
        except Exception as e:
            messagebox.showerror("Error", f"Error saving settings: {str(e)}")
            print(f"DEBUG - Exception: {e}")  # Debug
    
    def reset_to_default(self):
        """Reset settings to default values"""
        if messagebox.askyesno("Confirm Reset", 
                              "Are you sure you want to reset to default settings?\n\n" +
                              "Default:\n" +
                              "• Time: 8:00 AM\n" +
                              "• Grace Period: 10 minutes\n" +
                              "• Fee: ₱50.00 (Fixed)"):
            try:
                query = """UPDATE late_fee_settings 
                           SET standard_shift_start = '08:00:00',
                               grace_period_minutes = 10,
                               fee_type = 'fixed',
                               fixed_fee_amount = 50.00,
                               per_minute_fee = 5.00,
                               updated_at = NOW()
                           WHERE is_active = 1"""
                
                result = self.db.execute_query(query)
                
                if result is not False:
                    messagebox.showinfo("✓ Success", "Settings reset to default!")
                    self.fee_type_var.set('fixed')
                    # Re-render everything to ensure clean state
                    self.render()
                else:
                    messagebox.showerror("Error", "Failed to reset settings")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error resetting settings: {str(e)}")