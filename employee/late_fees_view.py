import tkinter as tk
from tkinter import ttk, messagebox
from config import COLORS

class EmployeeLateFeesView:
    def __init__(self, parent_frame, db, employee_data):
        self.parent_frame = parent_frame
        self.db = db
        if isinstance(employee_data, dict):
            self.employee_id = employee_data.get('employee_id') or employee_data.get('id')
        else:
            self.employee_id = employee_data
            
        print(f"DEBUG - Late Fees View for Employee ID: {self.employee_id}")
        self.render()

    def render(self):
        for widget in self.parent_frame.winfo_children():
            widget.destroy()

        self.parent_frame.configure(bg="#F5F7FA")

        # Header
        header = tk.Frame(self.parent_frame, bg="#F5F7FA")
        header.pack(fill=tk.X, padx=30, pady=(20, 15))
        
        tk.Label(header, text="Late Fee Management", 
                font=("Arial", 20, "bold"), 
                fg="#1F2937", bg="#F5F7FA").pack(side=tk.LEFT)
        
        refresh_btn = tk.Button(header, text="Refresh", 
                 bg="white", fg="#6B7280", font=("Arial", 10),
                 relief=tk.FLAT, padx=15, pady=8, cursor="hand2",
                 command=self.load_data,
                 highlightbackground="#E5E7EB", highlightthickness=1)
        refresh_btn.pack(side=tk.RIGHT)
        refresh_btn.bind("<Enter>", lambda e: refresh_btn.config(bg="#F9FAFB"))
        refresh_btn.bind("<Leave>", lambda e: refresh_btn.config(bg="white"))

        # Summary Cards
        self.create_summary_cards()

        # Main Content
        content_frame = tk.Frame(self.parent_frame, bg="#F5F7FA")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=(0, 20))

        self.create_unpaid_fees_table(content_frame)
        self.load_data()

    def create_summary_cards(self):
        """Create minimal summary cards"""
        cards_container = tk.Frame(self.parent_frame, bg="#F5F7FA")
        cards_container.pack(fill=tk.X, padx=30, pady=(0, 20))
        
        # Total Unpaid Card
        unpaid_card = tk.Frame(cards_container, bg="white", relief=tk.FLAT,
                              highlightbackground="#E5E7EB", highlightthickness=1)
        unpaid_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        accent = tk.Frame(unpaid_card, bg="#EF4444", width=4)
        accent.place(relx=0, rely=0, relheight=1, anchor="nw")
        
        card_content = tk.Frame(unpaid_card, bg="white")
        card_content.pack(fill=tk.BOTH, expand=True, padx=(15, 15), pady=15)
        
        tk.Label(card_content, text="TOTAL OUTSTANDING",
                font=("Arial", 9, "bold"), bg="white",
                fg="#9CA3AF").pack(anchor="w")
        
        self.unpaid_amount_label = tk.Label(card_content, text="₱0.00",
                font=("Arial", 28, "bold"), bg="white",
                fg="#1F2937")
        self.unpaid_amount_label.pack(anchor="w", pady=(5, 0))
        
        tk.Label(card_content, text="Amount to be settled",
                font=("Arial", 9), bg="white",
                fg="#6B7280").pack(anchor="w")
        
        # Late Arrivals Card
        instances_card = tk.Frame(cards_container, bg="white", relief=tk.FLAT,
                                 highlightbackground="#E5E7EB", highlightthickness=1)
        instances_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        accent2 = tk.Frame(instances_card, bg="#F59E0B", width=4)
        accent2.place(relx=0, rely=0, relheight=1, anchor="nw")
        
        card_content2 = tk.Frame(instances_card, bg="white")
        card_content2.pack(fill=tk.BOTH, expand=True, padx=(15, 15), pady=15)
        
        tk.Label(card_content2, text="LATE ARRIVALS",
                font=("Arial", 9, "bold"), bg="white",
                fg="#9CA3AF").pack(anchor="w")
        
        self.instances_label = tk.Label(card_content2, text="0",
                font=("Arial", 28, "bold"), bg="white",
                fg="#1F2937")
        self.instances_label.pack(anchor="w", pady=(5, 0))
        
        tk.Label(card_content2, text="Unpaid instances",
                font=("Arial", 9), bg="white",
                fg="#6B7280").pack(anchor="w")

    def create_unpaid_fees_table(self, parent):
        """Create unpaid fees table"""
        table_card = tk.Frame(parent, bg="white", relief=tk.FLAT,
                             highlightbackground="#E5E7EB", highlightthickness=1)
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = tk.Frame(table_card, bg="white")
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 0))
        
        left_header = tk.Frame(header_frame, bg="white")
        left_header.pack(side=tk.LEFT)
        
        tk.Label(left_header, text="Outstanding Fees",
                font=("Arial", 16, "bold"), bg="white",
                fg="#1F2937").pack(side=tk.LEFT)
        
        self.status_badge = tk.Label(left_header, text="0 pending",
                font=("Arial", 9, "bold"), bg="#FEF3C7",
                fg="#92400E", padx=10, pady=3)
        self.status_badge.pack(side=tk.LEFT, padx=(12, 0))
        
        # Action buttons
        btn_container = tk.Frame(header_frame, bg="white")
        btn_container.pack(side=tk.RIGHT)
        
        pay_all_btn = tk.Button(btn_container, text="Pay All", 
                               bg="#3B82F6", fg="white", 
                               font=("Arial", 10, "bold"),
                               relief=tk.FLAT, cursor="hand2",
                               command=self.pay_all_fees, 
                               padx=15, pady=8)
        pay_all_btn.pack(side=tk.LEFT, padx=(0, 8))
        pay_all_btn.bind("<Enter>", lambda e: pay_all_btn.config(bg="#2563EB"))
        pay_all_btn.bind("<Leave>", lambda e: pay_all_btn.config(bg="#3B82F6"))
        
        pay_btn = tk.Button(btn_container, text="Pay Selected", 
                          bg="#10B981", fg="white", 
                          font=("Arial", 10, "bold"),
                          relief=tk.FLAT, cursor="hand2",
                          command=self.pay_selected_fee, 
                          padx=15, pady=8)
        pay_btn.pack(side=tk.LEFT)
        pay_btn.bind("<Enter>", lambda e: pay_btn.config(bg="#059669"))
        pay_btn.bind("<Leave>", lambda e: pay_btn.config(bg="#10B981"))

        separator = tk.Frame(table_card, bg="#E5E7EB", height=1)
        separator.pack(fill=tk.X, padx=20, pady=12)

        # Table
        table_container = tk.Frame(table_card, bg="white")
        table_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))

        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Modern.Treeview",
                       background="white",
                       foreground="#1F2937",
                       fieldbackground="white",
                       borderwidth=0,
                       rowheight=40,
                       font=("Arial", 10))
        
        style.configure("Modern.Treeview.Heading",
                       background="#F9FAFB",
                       foreground="#6B7280",
                       borderwidth=0,
                       relief="flat",
                       font=("Arial", 10, "bold"))
        
        style.map("Modern.Treeview",
                 background=[('selected', '#DBEAFE')],
                 foreground=[('selected', '#1F2937')])
        
        style.layout("Modern.Treeview", [('Modern.Treeview.treearea', {'sticky': 'nswe'})])

        columns = ("id", "date", "time_in", "minutes", "amount")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", 
                                height=10, style="Modern.Treeview")
        
        headers = {
            "id": "ID",
            "date": "Date",
            "time_in": "Clock In",
            "minutes": "Minutes Late",
            "amount": "Fee Amount"
        }
        
        for col, title in headers.items():
            self.tree.heading(col, text=title)
        
        self.tree.column("id", width=0, stretch=False)
        self.tree.column("date", width=150, anchor="center")
        self.tree.column("time_in", width=150, anchor="center")
        self.tree.column("minutes", width=150, anchor="center")
        self.tree.column("amount", width=150, anchor="center")

        scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.tag_configure('evenrow', background='#F9FAFB')
        self.tree.tag_configure('oddrow', background='white')
        
        # Empty state
        self.empty_frame = tk.Frame(table_container, bg="white")
        
        tk.Label(self.empty_frame, text="All Caught Up!",
                font=("Arial", 16, "bold"), bg="white",
                fg="#1F2937").pack(pady=(30, 5))
        tk.Label(self.empty_frame, text="You have no outstanding late fees",
                font=("Arial", 11), bg="white",
                fg="#6B7280").pack(pady=(0, 30))
        
        self.tree.bind('<Double-1>', lambda e: self.pay_selected_fee())

    def show_payment_form(self, fee_id, date, amount, is_pay_all=False, total_fees=None):
        """Show payment form dialog"""
        dialog = tk.Toplevel(self.parent_frame)
        dialog.title("Payment Form")
        dialog.geometry("450x520")
        dialog.configure(bg="white")
        dialog.resizable(False, False)
        dialog.transient(self.parent_frame)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (dialog.winfo_screenheight() // 2) - (520 // 2)
        dialog.geometry(f"450x520+{x}+{y}")
        
        # Header
        header = tk.Frame(dialog, bg="#3B82F6", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="Payment Form",
                font=("Arial", 18, "bold"), bg="#3B82F6",
                fg="white").pack(pady=20)
        
        # Content
        content = tk.Frame(dialog, bg="white")
        content.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Payment details
        details_frame = tk.Frame(content, bg="#F9FAFB", 
                                highlightbackground="#E5E7EB", highlightthickness=1)
        details_frame.pack(fill=tk.X, pady=(0, 20))
        
        details_inner = tk.Frame(details_frame, bg="#F9FAFB")
        details_inner.pack(padx=15, pady=15)
        
        if is_pay_all:
            tk.Label(details_inner, text=f"Number of Fees: {total_fees}",
                    font=("Arial", 10), bg="#F9FAFB",
                    fg="#374151").pack(anchor="w", pady=2)
        else:
            tk.Label(details_inner, text=f"Date: {date}",
                    font=("Arial", 10), bg="#F9FAFB",
                    fg="#374151").pack(anchor="w", pady=2)
        
        tk.Label(details_inner, text=f"Total Amount: ₱{amount:.2f}",
                font=("Arial", 12, "bold"), bg="#F9FAFB",
                fg="#1F2937").pack(anchor="w", pady=(5, 2))
        
        # Payment Method
        tk.Label(content, text="Payment Method",
                font=("Arial", 11, "bold"), bg="white",
                fg="#1F2937").pack(anchor="w", pady=(0, 8))
        
        payment_method_var = tk.StringVar(value="Cash")
        
        method_frame = tk.Frame(content, bg="white")
        method_frame.pack(fill=tk.X, pady=(0, 20))
        
        cash_radio = tk.Radiobutton(method_frame, text="Cash", 
                                   variable=payment_method_var, value="Cash",
                                   font=("Arial", 10), bg="white",
                                   activebackground="white")
        cash_radio.pack(side=tk.LEFT, padx=(0, 20))
        
        gcash_radio = tk.Radiobutton(method_frame, text="GCash", 
                                    variable=payment_method_var, value="GCash",
                                    font=("Arial", 10), bg="white",
                                    activebackground="white")
        gcash_radio.pack(side=tk.LEFT)
        
        # Amount Paid
        tk.Label(content, text="Amount Paid",
                font=("Arial", 11, "bold"), bg="white",
                fg="#1F2937").pack(anchor="w", pady=(0, 8))
        
        amount_frame = tk.Frame(content, bg="white")
        amount_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(amount_frame, text="₱", font=("Arial", 14),
                bg="white", fg="#6B7280").pack(side=tk.LEFT, padx=(0, 5))
        
        amount_entry = tk.Entry(amount_frame, font=("Arial", 12),
                               bg="#F9FAFB", relief=tk.FLAT,
                               highlightbackground="#E5E7EB",
                               highlightthickness=1)
        amount_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        amount_entry.insert(0, f"{amount:.2f}")
        
        # Change display
        change_label = tk.Label(content, text="Change: ₱0.00",
                               font=("Arial", 11, "bold"), bg="white",
                               fg="#059669")
        change_label.pack(anchor="w", pady=(5, 0))
        
        # Error label
        error_label = tk.Label(content, text="",
                              font=("Arial", 9), bg="white",
                              fg="#EF4444")
        error_label.pack(anchor="w", pady=(5, 15))
        
        def calculate_change(*args):
            """Calculate change in real-time"""
            try:
                paid = float(amount_entry.get())
                if paid < 0:
                    error_label.config(text="Amount cannot be negative")
                    change_label.config(text="Change: ₱0.00", fg="#EF4444")
                    return False
                elif paid < amount:
                    error_label.config(text="Insufficient payment amount")
                    change_label.config(text="Change: ₱0.00", fg="#EF4444")
                    return False
                else:
                    change = paid - amount
                    error_label.config(text="")
                    change_label.config(text=f"Change: ₱{change:.2f}", fg="#059669")
                    return True
            except ValueError:
                error_label.config(text="Please enter a valid amount")
                change_label.config(text="Change: ₱0.00", fg="#EF4444")
                return False
        
        amount_entry.bind('<KeyRelease>', calculate_change)
        
        # Buttons
        btn_frame = tk.Frame(content, bg="white")
        btn_frame.pack(fill=tk.X, pady=(15, 0))
        
        def process_payment():
            if not calculate_change():
                messagebox.showerror("Invalid Payment", 
                                   "Please check your payment amount.",
                                   parent=dialog)
                return
            
            paid_amount = float(amount_entry.get())
            change = paid_amount - amount
            method = payment_method_var.get()
            
            try:
               if is_pay_all:
                # Process all fees
                success_count = 0
                for item in self.tree.get_children():
                    values = self.tree.item(item)['values']
                    item_fee_id = values[0]
                    amount_str = str(values[4]).replace('₱', '').replace(',', '')
                    fee_amount = float(amount_str)
                    if self.db.process_payment(item_fee_id, self.employee_id, paid_amount):  # ✅ Changed fee_amount to paid_amount
                        success_count += 1
                    
                    if success_count > 0:
                        msg = f"Payment Successful!\n\n"
                        msg += f"Payment Method: {method}\n"
                        msg += f"Total Paid: ₱{paid_amount:.2f}\n"
                        msg += f"Amount Due: ₱{amount:.2f}\n"
                        msg += f"Change: ₱{change:.2f}\n"
                        msg += f"Fees Paid: {success_count}"
                        
                        messagebox.showinfo("Success", msg, parent=dialog)
                        dialog.destroy()
                        self.load_data()
               else:
                    if self.db.process_payment(fee_id, self.employee_id, paid_amount):  # ✅ Changed amount to paid_amount
                        msg = f"Payment Successful!\n\n"
                        msg += f"Payment Method: {method}\n"
                        msg += f"Amount Paid: ₱{paid_amount:.2f}\n"
                        msg += f"Amount Due: ₱{amount:.2f}\n"
                        msg += f"Change: ₱{change:.2f}"
                        
                        messagebox.showinfo("Success", msg, parent=dialog)
                        dialog.destroy()
                        self.load_data()
                    else:
                        messagebox.showerror("Error", 
                                           "Payment processing failed.",
                                           parent=dialog)
            except Exception as e:
                messagebox.showerror("Error", 
                                   f"Payment failed:\n{str(e)}",
                                   parent=dialog)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel",
                             bg="white", fg="#6B7280",
                             font=("Arial", 10, "bold"),
                             relief=tk.FLAT, cursor="hand2",
                             command=dialog.destroy,
                             highlightbackground="#E5E7EB",
                             highlightthickness=1,
                             padx=20, pady=10)
        cancel_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        confirm_btn = tk.Button(btn_frame, text="Confirm Payment",
                              bg="#10B981", fg="white",
                              font=("Arial", 10, "bold"),
                              relief=tk.FLAT, cursor="hand2",
                              command=process_payment,
                              padx=20, pady=10)
        confirm_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(5, 0))
        confirm_btn.bind("<Enter>", lambda e: confirm_btn.config(bg="#059669"))
        confirm_btn.bind("<Leave>", lambda e: confirm_btn.config(bg="#10B981"))

    def load_data(self):
        """Load unpaid late fees"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            unpaid_fees = self.db.get_employee_unpaid_fees(self.employee_id)
            
            print(f"\n=== DEBUG Late Fees ===")
            print(f"Employee ID: {self.employee_id}")
            print(f"Unpaid fees count: {len(unpaid_fees) if unpaid_fees else 0}")
            if unpaid_fees and len(unpaid_fees) > 0:
                print(f"First fee structure: {unpaid_fees[0]}")
                if isinstance(unpaid_fees[0], dict):
                    print(f"Available keys: {unpaid_fees[0].keys()}")
            print("="*50 + "\n")
            
            total_unpaid = 0
            unpaid_count = 0
            
            if unpaid_fees and len(unpaid_fees) > 0:
                self.empty_frame.pack_forget()
                
                for idx, fee in enumerate(unpaid_fees):
                    if isinstance(fee, dict):
                        fee_id = fee['id']
                        date_val = fee['date']
                        # Try multiple possible column names for clock_in time
                        time_in = (fee.get('time_in') or 
                                  fee.get('clock_in') or 
                                  fee.get('time') or 
                                  fee.get('clock_in_time'))
                        minutes = fee.get('minutes_late', 0) or 0
                        amount = float(fee.get('late_fee_amount', 0) or 0)
                        
                        print(f"Fee {idx}: time_in value = {time_in}, type = {type(time_in)}")
                    else:
                        fee_id = fee[0]
                        date_val = fee[1]
                        time_in = fee[2] if len(fee) > 2 else None
                        minutes = fee[3] if len(fee) > 3 and fee[3] else 0
                        amount = float(fee[4]) if len(fee) > 4 and fee[4] else 0.0
                        
                        print(f"Fee {idx}: time_in value = {time_in}, type = {type(time_in)}")
                    
                    if hasattr(date_val, 'strftime'):
                        date_str = date_val.strftime('%b %d, %Y')
                    else:
                        date_str = str(date_val)
                    
                    # Enhanced time_in display handling
                    time_str = 'N/A'
                    if time_in:
                        if hasattr(time_in, 'strftime'):
                            # It's a datetime or time object
                            time_str = time_in.strftime('%I:%M %p')
                        elif isinstance(time_in, str) and time_in != 'N/A':
                            try:
                                # Try parsing as HH:MM:SS
                                from datetime import datetime
                                if ':' in time_in:
                                    time_parts = time_in.split(':')
                                    if len(time_parts) >= 2:
                                        hour = int(time_parts[0])
                                        minute = int(time_parts[1])
                                        time_obj = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M")
                                        time_str = time_obj.strftime('%I:%M %p')
                                    else:
                                        time_str = time_in
                                else:
                                    time_str = time_in
                            except Exception as e:
                                print(f"Error parsing time: {e}")
                                time_str = time_in
                        elif time_in != 'N/A':
                            time_str = str(time_in)
                    
                    print(f"Final time_str: {time_str}")
                    
                    total_unpaid += amount
                    unpaid_count += 1
                    
                    tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
                    
                    self.tree.insert("", tk.END, values=(
                        fee_id, 
                        date_str,
                        time_str,
                        f"{minutes} min" if minutes == 1 else f"{minutes} mins", 
                        f"₱{amount:.2f}"
                    ), tags=(tag,))
            else:
                self.tree.pack_forget()
                self.empty_frame.pack(fill=tk.BOTH, expand=True)
            
            self.unpaid_amount_label.config(text=f"₱{total_unpaid:,.2f}")
            self.instances_label.config(text=str(unpaid_count))
            
            if unpaid_count == 0:
                self.status_badge.config(text="All clear", bg="#D1FAE5", fg="#065F46")
            else:
                self.status_badge.config(text=f"{unpaid_count} pending", 
                                        bg="#FEF3C7", fg="#92400E")
                
        except Exception as e:
            print(f"ERROR loading fees: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"Failed to load late fees:\n{str(e)}")

    def pay_selected_fee(self):
        """Show payment form for selected fee"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", 
                                 "Please select a late fee to pay.")
            return

        item = self.tree.item(selected[0])
        values = item['values']
        
        fee_id = values[0]
        date = values[1]
        amount_str = str(values[4]).replace('₱', '').replace(',', '')
        amount = float(amount_str)
        
        self.show_payment_form(fee_id, date, amount)

    def pay_all_fees(self):
        """Show payment form for all fees"""
        if not self.tree.get_children():
            messagebox.showinfo("No Fees", "You have no outstanding late fees.")
            return
        
        total = 0
        fee_count = 0
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            amount_str = str(values[4]).replace('₱', '').replace(',', '')
            total += float(amount_str)
            fee_count += 1
        
        self.show_payment_form(None, None, total, is_pay_all=True, total_fees=fee_count)