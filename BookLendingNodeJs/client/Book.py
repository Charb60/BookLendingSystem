import tkinter as tk
from tkinter import ttk  
import requests
from admin_panel import open_admin
from PIL import Image, ImageTk
from io import BytesIO

API_URL = "http://localhost:3000"

def login_before_admin():
    login_window = tk.Toplevel(root)
    login_window.title("เข้าสู่ระบบ Admin")
    login_window.geometry("300x200")
    login_window.grab_set()  # บังคับให้ล็อก focus ที่ popup นี้

    tk.Label(login_window, text="ชื่อผู้ใช้:", font=("TH Sarabun New", 14)).pack(pady=5)
    entry_user = tk.Entry(login_window, font=("TH Sarabun New", 14))
    entry_user.pack(pady=5)

    tk.Label(login_window, text="รหัสผ่าน:", font=("TH Sarabun New", 14)).pack(pady=5)
    entry_pass = tk.Entry(login_window, font=("TH Sarabun New", 14), show="*")
    entry_pass.pack(pady=5)

    def check_login():
        username = entry_user.get()
        password = entry_pass.get()
        if username == "admin" and password == "1234":
            login_window.destroy()
            open_admin(root)  #เปิดหน้าต่าง admin ถ้า login สำเร็จ
        else:
            tk.messagebox.showerror("ข้อผิดพลาด", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง")

    tk.Button(login_window, text="เข้าสู่ระบบ", command=check_login, font=("TH Sarabun New", 14)).pack(pady=10)



#แสดงข้อมูลหนังสือ
# def show_books():
#     try:
#         response = requests.get(f"{API_URL}/all_books")
#         # response = requests.get(f"{API_URL}/books")

#         books = response.json()
#         for i in tree.get_children():
#             tree.delete(i)
#         for book in books:
#             status = "พร้อมให้ยืม" if book['available'] else "ถูกยืมไปแล้ว"
#             tree.insert("", "end", values=(book['id'], book['title'], status))
#         lbl_status.config(text="รายการหนังสือทั้งหมด")
#     except Exception as e:
#         lbl_status.config(text=f"เกิดข้อผิดพลาด: {e}")

def show_books():
    try:
        response = requests.get(f"{API_URL}/all_books")
        books = response.json()

        for i in tree.get_children():
            tree.delete(i)

        for book in books:
            status = "พร้อมให้ยืม" if book['available'] else "ถูกยืมไปแล้ว"
            tag = "available" if book['available'] else "borrowed"
            tree.insert("", "end", values=(book['id'], book['title'], status), tags=(tag,))

        lbl_status.config(text="รายการหนังสือทั้งหมด")

    except Exception as e:
        lbl_status.config(text=f"เกิดข้อผิดพลาด: {e}")


# #ค้นหาหนังสือ
# def search_books():
#     keyword = entry_search.get()
#     try:
#         response = requests.get(f"{API_URL}/search", params={"title": keyword})
#         books = response.json()
#         for i in tree.get_children():
#             tree.delete(i)
#         for book in books:
#             status = "พร้อมให้ยืม" if book['available'] else "ถูกยืมไปแล้ว"
#             tree.insert("", "end", values=(book['id'], book['title'], status))
#         lbl_status.config(text=f"ผลการค้นหา: '{keyword}'")
#     except Exception as e:
#         lbl_status.config(text=f"เกิดข้อผิดพลาด: {e}")
#ค้นหาหนังสือ
def search_books():
    keyword = entry_search.get()
    try:
        response = requests.get(f"{API_URL}/search", params={"title": keyword})
        books = response.json()
        for i in tree.get_children():
            tree.delete(i)
        for book in books:
            status = "พร้อมให้ยืม" if book['available'] else "ถูกยืมไปแล้ว"
            tag = "available" if book['available'] else "borrowed"
            tree.insert("", "end", values=(book['id'], book['title'], status), tags=(tag,))
        lbl_status.config(text=f"ผลการค้นหา: '{keyword}'")
    except Exception as e:
        lbl_status.config(text=f"เกิดข้อผิดพลาด: {e}")


#การยืม
def borrow_book():
    book_id = entry_book_id.get()
    user = entry_user.get()
    response = requests.post(f"{API_URL}/borrow", json={"book_id": book_id, "user": user})
    lbl_status.config(text=response.json()["message"])
#การคืน
def return_book():
    book_id = entry_book_id.get()
    response = requests.post(f"{API_URL}/return", json={"book_id": book_id})
    lbl_status.config(text=response.json()["message"])

#โชว์รูปภาพหนังสือเมื่อดับเบิ้ลคลิกที่รายการในตาราง
def show_book_image(event):
    selected_item = tree.focus()
    if not selected_item:
        return

    book_id = tree.item(selected_item)['values'][0]
    try:
        response = requests.get(f"{API_URL}/book_image/{book_id}")
        if response.status_code == 200:
            image_data = response.content

            # Create a new window to display the image
            image_window = tk.Toplevel(root)
            image_window.title("Book Image")

            # Convert image data to a format tkinter can use
            image = Image.open(BytesIO(image_data))
            photo = ImageTk.PhotoImage(image)

            label = tk.Label(image_window, image=photo)
            label.image = photo  
            label.pack()
        else:
            tk.messagebox.showerror("Error", "ไม่สามารถโหลดรูปภาพได้")
    except Exception as e:
        tk.messagebox.showerror("Error", f"เกิดข้อผิดพลาด: {e}")


root = tk.Tk()
root.title("ระบบยืม-คืนหนังสือ")

#ค่าแถว column UI 
root.state("zoomed")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
for i in range(4):
    root.grid_columnconfigure(i, weight=1)

#ช่องกรอกข้อมูลยืม,คืนidหนังสือ
tk.Label(root, text="รหัสหนังสือ:", font = ("TH Saraban New",20)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
entry_book_id = tk.Entry(root,font = ("TH Saraban New",20))
entry_book_id.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

#ช่องกรอกข้อมูลชื่อผู้ยืม,คืนหนังสือ
tk.Label(root, text="ชื่อผู้ยืม:",font = ("TH Saraban New",20)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
entry_user = tk.Entry(root,font = ("TH Saraban New",20))
entry_user.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

#ปุ่มยืม
btn_borrow = tk.Button(root, text="ยืมหนังสือ", command=borrow_book,font = ("TH Saraban New",14, "bold"),bg="#b1f5b7")
btn_borrow.grid(row=2, column=0,  padx=10, pady=5, sticky="nsew")
#ปุ่มคืน
btn_return = tk.Button(root, text="คืนหนังสือ", command=return_book,font = ("TH Saraban New",14, "bold"),bg="#F5B7B1")
btn_return.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

#แถบแสดงสถานะ
lbl_status = tk.Label(root, text="" ,fg="blue" ,anchor="center" ,font = ("TH Saraban New",20))
lbl_status.grid(row=5, columnspan=2, padx=10, pady=10, sticky="nsew")

#ช่องค้นหาหนังสือ 
tk.Label(root, text="ค้นหาหนังสือ:", font=("TH Saraban New", 14, "bold")).grid(row=3, column=0, padx=10, pady=10, sticky="e")
entry_search = tk.Entry(root, font=("TH Saraban New", 14))
entry_search.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

#ปุ่มค้นหาอยู่ขวาสุดในแถวเดียวกัน 
btn_search = tk.Button(root, text="ค้นหา", command=search_books, font=("TH Saraban New", 20))
btn_search.grid(row=3, column=2, padx=10, pady=10, sticky="nsew")

#สร้าง style สำหรับ Treeview
style = ttk.Style()
style.configure("Treeview", font=("TH Sarabun New", 15), rowheight=30)  
style.configure("Treeview.Heading", font=("TH Sarabun New", 15, "bold")) 

#ตารางแสดงข้อมูลหนังสือ
tree = ttk.Treeview(root, columns=("รหัสหนังสือ", "ชื่อหนังสือ", "สถานะ"), show="headings", height=10)
tree.heading("รหัสหนังสือ", text="รหัสหนังสือ")
tree.heading("ชื่อหนังสือ", text="ชื่อหนังสือ")
tree.heading("สถานะ", text="สถานะ")
#กำหนดสีพื้นหลังของแต่ละแท็ก
tree.tag_configure("available", background="#b1f5b7")   #สีเขียวอ่อน = พร้อมให้ยืม
tree.tag_configure("borrowed", background="#F5B7B1")    #สีชมพูอ่อน = ถูกยืม

#ดูรูปภาพหนังสือเมื่อดับเบิ้ลคลิกที่รายการในตาราง
tree.bind("<Double-1>", show_book_image)  

tree.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")



btn_admin = tk.Button(root, text="ไปยังหน้าผู้ดูแลระบบ", command=login_before_admin, font=("TH Saraban New", 14))
btn_admin.grid(row=6, column=2, padx=10, pady=20, sticky="se")


show_books()
root.mainloop()