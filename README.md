# 🌙 PDF Dark Mode Converter
https://khaled-0110-pdf-darkener-app-fgdx5e.streamlit.app/
A Streamlit web application that converts PDFs with white backgrounds and dark text into **dark mode PDFs** for improved eye comfort.
The app works with both **text-based and scanned PDFs** by converting pages to images and applying smart image processing techniques.

---

## ✨ Features

* 🌙 Convert PDFs to dark mode (black background, light text)
* 📄 Supports **text-based and scanned PDFs**
* 🧠 Automatic background detection
* 📦 **Batch PDF upload**
* 🎛 Adjustable contrast and brightness
* ⬇️ Download converted PDFs instantly
* ☁️ Deployable on **Streamlit Cloud**

---

## 🛠️ Tech Stack

* **Python**
* **Streamlit** – web interface
* **pdf2image** – PDF to image conversion
* **Pillow (PIL)** – image processing
* **NumPy & OpenCV** – background detection
* **Poppler** – system dependency for PDF rendering

---

## 🚀 How It Works

1. User uploads one or more PDFs
2. Each page is converted to an image
3. The app detects whether the page background is mostly white
4. A smart dark-mode filter is applied
5. Processed pages are rebuilt into a new PDF
6. User downloads the dark-mode PDF

---

## 📁 Project Structure

```
pdf-dark-mode/
│
├── app.py
├── requirements.txt
├── packages.txt
└── README.md
```

---

## ⚙️ Installation (Local)

### 1️⃣ Clone the repository

```bash
git clone https://github.com/your-username/pdf-dark-mode.git
cd pdf-dark-mode
```

---

### 2️⃣ Create and activate a virtual environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Python dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Install Poppler (Windows)

* Download Poppler for Windows
* Extract it to:

  ```
  C:\poppler
  ```
* Add this to your system PATH:

  ```
  C:\poppler\Library\bin
  ```

Verify installation:

```bash
pdftoppm -h
```

---

### 5️⃣ Run the app

```bash
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

This project is **Streamlit Cloud ready**.

* `requirements.txt` → Python dependencies
* `packages.txt` → System dependencies (`poppler-utils`)

Steps:

1. Push project to GitHub
2. Create a new app on Streamlit Cloud
3. Select the repository
4. Deploy 🚀

---

## 🧪 Notes & Limitations

* The app uses **image-based processing**, not OCR
* Very complex PDFs may take longer to process
* Layout is preserved, but file size may increase slightly

---

## 🔮 Future Improvements

* Page preview before download
* Dark gray background option
* ZIP download for batch processing
* Performance optimization for large PDFs

---

## 📜 License

This project is open-source and available for educational and personal use.

---

## 🙌 Author

**Khaled Nasser**
Business Information Systems Student
Aspiring Data / AI Engineer
