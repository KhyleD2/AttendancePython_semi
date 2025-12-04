import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS

class EmployeeLateFeesView:
    def __init__(self, parent_frame, db, employee_data):
        self.parent_frame = parent_frame
        self.db = db
        # Handle different data structures safely
        if isinstance(employee_data, dict):
            self.employee_id = employee_data.get('employee_id') or employee_data.get('id')
        else:
            self.employee_id = employee_data
            
        print(f"DEBUG - Late Fees View for Employee ID: {self.employee_id}")
        self.render()

    def render(self):
        # Clear frame
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        # --- Header ---
        header = tk.Frame(self.parent_frame, bg="white", padx=20, pady=20)
        header.pack(fill=tk.X)
        
        tk.Label(header, text="My Late Fees", 
                font=("Segoe UI", 24, "bold"), 
                bg="white", fg=COLORS['primary']).pack(side=tk.LEFT)

        # --- Stats / Summary ---
        self.stats_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_main'])
        self.stats_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.total_label = tk.Label(self.stats_frame, text="Loading...", 
                                  font=("Segoe UI", 16, "bold"), 
                                  fg="#e74c3c", bg=COLORS['bg_main'])
        self.total_label.pack(side=tk.LEFT)

        # --- Table Section ---
        tk.Label(self.parent_frame, text="Unpaid Fees (Select a row to Pay)", 
                font=("Segoe UI", 12, "bold"), 
                bg=COLORS['bg_main'], fg=COLORS['text_dark']).pack(anchor="w", padx=20, pady=(20,5))

        table_container = tk.Frame(self.parent_frame, bg="white")
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        columns = ("id", "date", "minutes", "amount", "status")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", height=10)
        
        # Define Columns
        self.tree.heading("date", text="Date")
        self.tree.heading("minutes", text="Minutes Late")
        self.tree.heading("amount", text="Fee Amount")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("minutes", width=150, anchor="center")
        self.tree.column("amount", width=150, anchor="center")
        self.tree.column("status", width=150, anchor="center")

        # Scrollbar
        scroll = tk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # --- Pay Button ---
        btn_frame = tk.Frame(self.parent_frame, bg=COLORS['bg_main'], pady=20)
        btn_frame.pack(fill=tk.X, padx=20)

        pay_btn = tk.Button(btn_frame, text="💳 Pay Selected Fee", 
                          bg="#2ecc71", fg="white", 
                          font=("Segoe UI", 12, "bold"),
                          relief=tk.FLAT, cursor="hand2",
                          command=self.pay_selected_fee, 
                          padx=20, pady=10)
        pay_btn.pack(side=tk.RIGHT)

        self.load_data()

    def load_data(self):
        """Load unpaid late fees from database"""
        # Clear table
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            print(f"DEBUG - Fetching unpaid fees for employee_id: {self.employee_id}")
            
            # Fetch Unpaid Fees from Database
            unpaid_fees = self.db.get_employee_unpaid_fees(self.employee_id)
            
            print(f"DEBUG - Found {len(unpaid_fees) if unpaid_fees else 0} unpaid fees")
            
            total_due = 0
            
            if unpaid_fees and len(unpaid_fees) > 0:
                for fee in unpaid_fees:
                    print(f"DEBUG - Processing fee: {fee}")
                    print(f"DEBUG - Fee type: {type(fee)}")
                    
                    # ✅ Handle both dictionary and tuple formats
                    if isinstance(fee, dict):
                        # Dictionary format
                        fee_id = fee['id']
                        date_val = fee['date']
                        minutes = fee['minutes_late'] if fee['minutes_late'] else 0
                        amount = float(fee['late_fee_amount']) if fee['late_fee_amount'] else 0.0
                        status = fee.get('status', 'late')
                    else:
                        # Tuple format
                        fee_id = fee[0]
                        date_val = fee[1]
                        minutes = fee[2] if fee[2] else 0
                        amount = float(fee[3]) if fee[3] else 0.0
                        status = fee[4] if len(fee) > 4 else 'late'
                    
                    # Format date
                    if hasattr(date_val, 'strftime'):
                        date_str = date_val.strftime('%Y-%m-%d')
                    else:
                        date_str = str(date_val)
                    
                    total_due += amount
                    
                    self.tree.insert("", tk.END, values=(
                        fee_id, 
                        date_str, 
                        f"{minutes} mins", 
                        f"₱{amount:.2f}", 
                        status.upper()
                    ))
                
                # Update Total Label
                self.total_label.config(
                    text=f"Total Amount Due: ₱{total_due:.2f}",
                    fg="#e74c3c"
                )
            else:
                # No unpaid fees
                self.total_label.config(
                    text="No unpaid late fees! 🎉",
                    fg="#2ecc71"
                )
                
        except Exception as e:
            print(f"ERROR loading fees: {e}")
            import traceback
            traceback.print_exc()
            self.total_label.config(
                text=f"Error loading fees: {str(e)}",
                fg="#e74c3c"
            )

    def pay_selected_fee(self):
        """Process payment for selected fee"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a fee to pay.")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        
        attendance_id = values[0]
        amount_str = str(values[3]).replace('₱', '').replace(',', '')
        amount = float(amount_str)

        if messagebox.askyesno("Confirm Payment", f"Are you sure you want to pay ₱{amount:.2f}?"):
            try:
                # Process Payment in Database
                if self.db.process_payment(attendance_id, self.employee_id, amount):
                    messagebox.showinfo("Success", "Payment Successful!")
                    self.load_data()
                else:
                    messagebox.showerror("Error", "Payment Failed. Please try again.")
            except Exception as e:
                print(f"Payment error: {e}")
                messagebox.showerror("Error", f"Payment Failed: {str(e)}")