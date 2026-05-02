const express = require("express");
// const mysql = require("mysql2");
const mysql = require("mysql2/promise");
const cors = require("cors");
const multer = require("multer");
const path = require("path");

const app = express();
app.use(express.json());
app.use(cors());
//mysql2
// const db = mysql.createConnection({
//     host: "localhost",
//     user: "root",
//     password: "root",
//     database: "bookdb",
//     port: 8889  // MAMP ใช้พอร์ต 8889 สำหรับ MySQL
// });

//promise
let db;

async function connectDB() {
  try {
    db = await mysql.createConnection({
      host: "localhost",
      user: "root",
      password: "root",
      database: "bookdb",
      port: 8889
    });
    console.log("✅ Connected to MySQL (MAMP)");
  } catch (err) {
    console.error("❌ Database connection failed:", err);
  }
}

connectDB();

// เชื่อมต่อฐานข้อมูล
// db.connect(err => {
//     if (err) {
//         console.error("❌ Database connection failed:", err);
//         return;
//     }
//     console.log("✅ Connected to MySQL (MAMP)");
// });

// API สำหรับยืมหนังสือ
app.post("/borrow", async (req, res) => {
    const { book_id, user } = req.body;
    try {
        // อัปเดตสถานะหนังสือ
        await db.execute("UPDATE books SET available = FALSE WHERE id = ?", [book_id]);

        // บันทึกประวัติการยืม
        const borrow_date = new Date();
        await db.execute(
            "INSERT INTO borrow_records (book_id, user, borrow_date, return_date) VALUES (?, ?, ?, NULL)",
            [book_id, user, borrow_date]
        );

        res.json({ message: "✅ ยืมหนังสือสำเร็จ!" });
    } catch (err) {
        res.status(500).json({ message: "❌ Error borrowing book", error: err.message });
    }
});


// API สำหรับคืนหนังสือ
app.post("/return", async (req, res) => {
    const { book_id } = req.body;
    try {
        // อัปเดตสถานะหนังสือ
        await db.execute("UPDATE books SET available = TRUE WHERE id = ?", [book_id]);

        // อัปเดตวันคืนในประวัติ (เฉพาะรายการล่าสุดที่ยังไม่คืน)
        const return_date = new Date();
        await db.execute(
            "UPDATE borrow_records SET return_date = ? WHERE book_id = ? AND return_date IS NULL ORDER BY id DESC LIMIT 1",
            [return_date, book_id]
        );

        res.json({ message: "✅ คืนหนังสือสำเร็จ!" });
    } catch (err) {
        res.status(500).json({ message: "❌ Error returning book", error: err.message });
    }
});

//GET all databook 
app.get('/all_books', async (req, res) => {
  try {
    const [rows] = await db.query('SELECT * FROM books ORDER BY id ASC');//เรียงน้อยไปมาก
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});
// GET data with title 
app.get('/search', async (req, res) => {
  const title = req.query.title;
  try {
    const [rows] = await db.execute("SELECT * FROM books WHERE title LIKE ?", [`%${title}%`]);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ message: "เกิดข้อผิดพลาด", error: err.message });
  }
});

// GET - อ่านข้อมูลการยืม,คืนทั้งหมด
app.get('/borrow_records', async (req, res) => {
  try {
    const [rows] = await db.execute(`
      SELECT br.id, b.title, br.user, br.borrow_date, br.return_date
      FROM borrow_records br
      JOIN books b ON br.book_id = b.id
      ORDER BY br.id DESC
    `);
    res.json(rows);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

   
// POST add book
app.post('/add_books', async (req, res) => {
  const { title } = req.body;
  try {
    await db.execute("INSERT INTO books (title, available) VALUES (?, true)", [title]);
    res.json({ message: "เพิ่มหนังสือเรียบร้อยแล้ว" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


// PUT update book
app.put('/update_book/:id', async (req, res) => {
  const { title } = req.body;
  const { id } = req.params;
  try {
    await db.execute("UPDATE books SET title = ? WHERE id = ?", [title, id]);
    res.json({ message: "แก้ไขหนังสือเรียบร้อยแล้ว" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// DELETE book
app.delete('/delete_book/:id', async (req, res) => {
  const { id } = req.params;
  try {
    await db.execute("DELETE FROM books WHERE id = ?", [id]);
    res.json({ message: "ลบหนังสือเรียบร้อยแล้ว" });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});


//   // DELETE - ลบข้อมูลการยืม,คืน
// app.delete('/delete_book/:id', async (req, res) => {
//   const { id } = req.params;
//   try {
//     await db.execute("DELETE FROM books WHERE id = ?", [id]);
//     res.json({ message: "ลบหนังสือเรียบร้อยแล้ว" });
//   } catch (err) {
//     res.status(500).json({ error: err.message });
//   }
// });
  

// API for uploading images
app.post("/upload_image", upload.single("image"), (req, res) => {
  try {
    res.json({ message: "✅ อัปโหลดรูปภาพสำเร็จ!", filePath: req.file.path });
  } catch (err) {
    res.status(500).json({ message: "❌ อัปโหลดรูปภาพล้มเหลว", error: err.message });
  }
});

// เปิดเซิร์ฟเวอร์ที่พอร์ต 3000
app.listen(3000, () => {
    console.log("🚀 Server is running on http://localhost:3000");
});
