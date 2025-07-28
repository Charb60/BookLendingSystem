import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_URL = "http://localhost:3000"

def open_admin(root):
    admin_window = tk.Toplevel(root)
    admin_window.title("Admin Panel")
    admin_window.geometry("1000x700")

    def fetch_books():
        try:
            response = requests.get(f"{API_URL}/all_books")
            return response.json()
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถโหลดข้อมูล: {e}")
            return []

    # def refresh_tree():
    #     for i in tree.get_children():
    #         tree.delete(i)
    #     for book in fetch_books():
    #         status = "พร้อมยืม" if book["available"] else "ถูกยืมไปแล้ว"
    #         tree.insert("", "end", values=(book["id"], book["title"], status))
    def refresh_tree():
        for i in tree.get_children():
            tree.delete(i)
        for book in fetch_books():
            status = "พร้อมยืม" if book["available"] else "ถูกยืมไปแล้ว"
            tag = "available" if book["available"] else "borrowed"
            tree.insert("", "end", values=(book["id"], book["title"], status), tags=(tag,))

    def add_book():
        title = entry_title.get()
        if not title:
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกชื่อหนังสือ")
            return
        try:
            requests.post(f"{API_URL}/add_books", json={"title": title})
            entry_title.delete(0, tk.END)
            refresh_tree()
            messagebox.showinfo("สำเร็จ", "เพิ่มหนังสือเรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("Error", f"เพิ่มหนังสือล้มเหลว: {e}")

    def delete_book():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกหนังสือที่จะลบ")
            return
        book_id = tree.item(selected)["values"][0]
        try:
            requests.delete(f"{API_URL}/delete_book/{book_id}")
            refresh_tree()
            messagebox.showinfo("สำเร็จ", "ลบหนังสือเรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("Error", f"ลบหนังสือล้มเหลว: {e}")

    def update_book():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกหนังสือที่จะแก้ไข")
            return
        book_id = tree.item(selected)["values"][0]
        new_title = entry_title.get()
        if not new_title:
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกชื่อหนังสือใหม่")
            return
        try:
            requests.put(f"{API_URL}/update_book/{book_id}", json={"title": new_title})
            refresh_tree()
            messagebox.showinfo("สำเร็จ", "แก้ไขหนังสือเรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("Error", f"แก้ไขหนังสือล้มเหลว: {e}")

    def show_borrow_records():
        try:
            response = requests.get(f"{API_URL}/borrow_records")
            records = response.json()

            # สร้างหน้าต่างใหม่สำหรับแสดงข้อมูลการยืม-คืน
            borrow_window = tk.Toplevel(admin_window)
            borrow_window.title("ข้อมูลการยืม-คืนหนังสือ")
            borrow_window.geometry("800x500")

            # สร้างตารางแสดงข้อมูลการยืม-คืน
            columns = ("ชื่อหนังสือ", "ชื่อผู้ยืม", "วันที่ยืม", "วันที่คืน")
            tree_borrow = ttk.Treeview(borrow_window, columns=columns, show="headings", height=15)
            for col in columns:
                tree_borrow.heading(col, text=col)
        
        #เติมข้อมูลลงในตาราง
            for r in records:
                tree_borrow.insert("", "end", values=(
                    # r["id"],
                    # r["book_id"],
                    r["title"],
                    r["user"],
                    r["borrow_date"] or "-",
                    r["return_date"] or "-"
                ))

            tree_borrow.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("เกิดข้อผิดพลาด", str(e))



    # UI

    tk.Label(admin_window, text="ชื่อหนังสือ", font=("TH Sarabun New", 16)).pack(pady=5)
    entry_title = tk.Entry(admin_window, font=("TH Sarabun New", 16), width=40)
    entry_title.pack(pady=5)

    btn_frame = tk.Frame(admin_window)
    btn_frame.pack(pady=10)

    btn_frame = tk.Frame(admin_window)
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="เพิ่ม", font=("TH Sarabun New", 14), command=add_book, width=10).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="แก้ไข", font=("TH Sarabun New", 14), command=update_book, width=10).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="ลบ", font=("TH Sarabun New", 14), command=delete_book, width=10).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="แสดงข้อมูลการยืม-คืน", font=("TH Sarabun New", 14), command=show_borrow_records, width=15).grid(row=0, column=3, padx=5)

    #ตารางแสดงข้อมูลหนังสือ
    global tree
    tree = ttk.Treeview(admin_window, columns=("รหัสหนังสือ", "ชื่อหนังสือ", "สถานะ"), show="headings", height=10)
    tree.heading("รหัสหนังสือ", text="รหัสหนังสือ")
    tree.heading("ชื่อหนังสือ", text="ชื่อหนังสือ")
    tree.heading("สถานะ", text="สถานะ")
    tree.tag_configure("available", background="#b1f5b7")  # เขียวอ่อน
    tree.tag_configure("borrowed", background="#F5B7B1")   # ชมพูอ่อน

    tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
    # columns = ("รหัสหนังสือ", " รหัสหนังสือ", "User", "Borrow Date", "Return Date")
    # tree_borrow = ttk.Treeview(admin_window, columns=columns, show="headings", height=10)
    # for col in columns:
    #     tree_borrow.heading(col, text=col)
    # tree_borrow.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)


    refresh_tree()
