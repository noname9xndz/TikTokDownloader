# DouK-Downloader — Hướng Dẫn Cài Đặt & Sử Dụng

> Tải video/ảnh/nhạc/livestream từ **Douyin** và **TikTok**.
> Hỗ trợ 3 chế độ: **Terminal (CLI)**, **Desktop GUI**, và **Web API**.

---

## Mục lục

1. [Yêu cầu hệ thống](#1-yêu-cầu-hệ-thống)
2. [Clone & Cài đặt](#2-clone--cài-đặt)
3. [Cấu hình ban đầu](#3-cấu-hình-ban-đầu)
4. [Chạy ứng dụng](#4-chạy-ứng-dụng)
5. [Cách sử dụng từng chế độ](#5-cách-sử-dụng-từng-chế-độ)
6. [Đóng gói .exe (PyInstaller)](#6-đóng-gói-exe-pyinstaller)
7. [Cấu trúc thư mục](#7-cấu-trúc-thư-mục)
8. [FAQ & Xử lý lỗi](#8-faq--xử-lý-lỗi)

---

## 1. Yêu cầu hệ thống

| Thành phần | Yêu cầu |
|------------|---------|
| **Python** | `3.12.x` (bắt buộc — không hỗ trợ 3.11 hoặc 3.13) |
| **OS** | Windows 10/11 (đã test), macOS/Linux (cần thêm test) |
| **RAM** | ≥ 4GB |
| **FFmpeg** | Khuyến nghị — cần cho merge video+audio chất lượng cao |
| **Git** | Để clone repository |

### Cài FFmpeg (tùy chọn nhưng khuyến nghị)

```bash
# Windows (dùng winget)
winget install Gyan.FFmpeg

# Hoặc tải từ https://ffmpeg.org/download.html
# Giải nén → thêm thư mục bin/ vào PATH
```

Kiểm tra:
```bash
ffmpeg -version
```

---

## 2. Clone & Cài đặt

### Bước 1: Clone repository

```bash
git clone https://github.com/JoeanAmier/TikTokDownloader.git
cd TikTokDownloader
```

### Bước 2: Tạo virtual environment

```bash
# Dùng uv (nhanh hơn pip)
pip install uv
uv venv --python 3.12
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

# Hoặc dùng Python trực tiếp
python -m venv .venv
.venv\Scripts\activate
```

### Bước 3: Cài dependencies

```bash
# Cách 1: dùng uv (khuyến nghị — nhanh nhất)
uv pip install -r requirements.txt
uv pip install customtkinter Pillow   # Cho GUI

# Cách 2: dùng pip
pip install -r requirements.txt
pip install customtkinter Pillow

# Cách 3: từ pyproject.toml (cài tất cả)
uv pip install -e .
# hoặc
pip install -e .
```

### Bước 4: Cài dev dependencies (nếu cần chạy test)

```bash
uv pip install pytest
# hoặc
pip install pytest
```

### Kiểm tra cài đặt thành công

```bash
python -c "import customtkinter; print('CTk OK')"
python -c "from src.application import TikTokDownloader; print('Backend OK')"
```

---

## 3. Cấu hình ban đầu

### File `settings.json`

- **Tự động tạo** khi chạy app lần đầu tiên
- Nằm trong **thư mục gốc** của project
- Có thể chỉnh sửa bằng text editor hoặc qua GUI Settings

Cấu trúc cơ bản:

```jsonc
{
    // === Cookie (quan trọng nhất!) ===
    "douyin_cookie": "",          // Cookie Douyin — cần để tải video
    "tiktok_cookie": "",          // Cookie TikTok
    
    // === Thư mục lưu file ===
    "root": "",                   // Thư mục gốc lưu file (để trống = thư mục mặc định)
    "folder_name": "Download",    // Tên thư mục con
    
    // === Proxy (nếu cần) ===
    "douyin_proxy": "",           // Proxy HTTP cho Douyin  (ví dụ: http://127.0.0.1:7890)
    "tiktok_proxy": "",           // Proxy HTTP cho TikTok
    
    // === Định dạng ===
    "storage_format": "xlsx",     // Lưu metadata: "xlsx" hoặc "csv"
    "name_format": "create_time type nickname desc",  // Template tên file
    "date_format": "%Y-%m-%d %H:%M:%S",              // Định dạng ngày tháng
    
    // === Download options ===
    "download_type": "video",     // Loại tải: "video", "image", "all"
    "music": false,               // Tải nhạc nền?
    "cover": false,               // Tải ảnh bìa?
    "dynamic_cover": false,       // Tải ảnh bìa động?
    
    // === Nâng cao ===
    "max_retry": 5,               // Số lần thử lại khi lỗi
    "max_pages": 0,               // Số trang tối đa (0 = tất cả)
    "chunk_size": 1048576,        // Kích thước chunk download (bytes)
    "timeout": 10                 // Timeout request (giây)
}
```

> **⚠️ Quan trọng:** Cookie là bắt buộc để tải video từ Douyin/TikTok!

### Cách lấy Cookie

#### Cách 1: Copy từ trình duyệt (CLI mode)

1. Mở trình duyệt → Đăng nhập Douyin/TikTok
2. Nhấn `F12` → Tab `Network` → Bấm vào bất kỳ request
3. Copy toàn bộ giá trị `Cookie` ở Headers
4. Paste vào app khi được hỏi (hoặc dán vào `settings.json`)

#### Cách 2: Tự động lấy từ browser (GUI mode)

- Mở GUI → Tab **Settings** → Section **Cookie Management**
- Chọn browser (Chrome/Edge/Firefox) → Nhấn **Import from Browser**
- App sẽ tự động lấy cookie qua thư viện `rookiepy`

---

## 4. Chạy ứng dụng

### Chế độ 1: Terminal (CLI) — Chế độ gốc

```bash
python main.py
```

Hiện menu tương tác:
```
1. 复制粘贴写入 Douyin Cookie (Copy paste Douyin Cookie)
2. 从浏览器获取 Douyin Cookie  (Auto-import Douyin Cookie)
3. 复制粘贴写入 TikTok Cookie
4. 从浏览器获取 TikTok Cookie
5. 终端交互模式 (Terminal Interactive — download mode)
6. 后台监测模式 (Monitor clipboard mode)
7. Web API 接口模式 (Start Web API server)
...
```

### Chế độ 2: Desktop GUI — Giao diện đồ họa

```bash
python main.py --gui
```

Hoặc chạy trực tiếp module:
```bash
python -m src.gui_edition.gui_main
```

GUI sẽ mở cửa sổ 800×600 với:
- **Download** tab — 7 sub-tabs: Account, Link, Mix, Live, Collection, Data, Search
- **Settings** tab — Cookie, thư mục, proxy, format, nâng cao
- **Monitor** tab — Tự động phát hiện link từ clipboard

### Chế độ 3: Web API Server

```bash
# Chọn option 7 trong CLI menu, hoặc
# sẽ chạy uvicorn server tại http://localhost:8000
```

API docs tự động tại: `http://localhost:8000/docs`

---

## 5. Cách sử dụng từng chế độ

### 5.1 Download qua Link (phổ biến nhất)

**CLI:**
```
Chọn option 5 → Chọn "Link Download" → Paste link video
```

**GUI:**
1. Mở GUI → Tab **Download** → Sub-tab **Link**
2. Paste link video vào ô input (hỗ trợ nhiều link, mỗi link 1 dòng)
3. Chọn platform: Douyin hoặc TikTok
4. Nhấn **Start Download**

Ví dụ link:
```
https://www.douyin.com/video/7123456789012345678
https://v.douyin.com/abc123/
https://www.tiktok.com/@user/video/7123456789012345678
```

### 5.2 Download toàn bộ tài khoản

**GUI:** Tab **Download** → Sub-tab **Account** → Paste URL profile

### 5.3 Monitor clipboard

**GUI:** Tab **Monitor** → Nhấn **Start Monitoring**

App sẽ tự động phát hiện khi bạn copy link Douyin/TikTok và tải ngay.

### 5.4 Search & Download

**GUI:** Tab **Download** → Sub-tab **Search** → Nhập từ khóa

Hỗ trợ 4 kênh: General, Video, User, Live.

---

## 6. Đóng gói .exe (PyInstaller)

### Cài PyInstaller

```bash
pip install pyinstaller
```

### Build

```bash
pyinstaller gui.spec
```

### Output

```
dist/
└── DouK-Downloader-GUI/
    ├── DouK-Downloader-GUI.exe    ← Chạy file này
    ├── customtkinter/
    ├── static/
    └── ... (DLLs, Python runtime)
```

> **Lưu ý:**
> - Build tạo thư mục `dist/DouK-Downloader-GUI/` (one-dir mode)
> - File `.exe` không chạy solo — cần cả thư mục đi kèm
> - Để chia sẻ: nén toàn bộ thư mục `DouK-Downloader-GUI/` thành `.zip`

---

## 7. Cấu trúc thư mục

```
TikTokDownloader/
├── main.py                  # Entry point chính (CLI + --gui)
├── gui_launcher.py          # Entry point cho PyInstaller
├── gui.spec                 # PyInstaller build spec
├── pyproject.toml           # Project metadata + dependencies
├── requirements.txt         # Lock file (uv generated)
├── settings.json            # ⚙️ Auto-generated khi chạy lần đầu
├── DouK-Downloader.db       # 📦 SQLite DB (auto-generated)
│
├── src/
│   ├── application/         # TikTokDownloader class + terminal menu
│   ├── config/              # Settings, Parameter — đọc/ghi settings.json
│   ├── interface/           # TikTok API clients (Douyin + TikTok)
│   ├── extract/             # Data extractors
│   ├── downloader/          # Download engine
│   ├── manager/             # Database + record manager
│   ├── module/              # Cookie management
│   ├── translation/         # i18n (Chinese ↔ English)
│   ├── link/                # URL resolver
│   ├── encrypt/             # API encryption
│   ├── storage/             # CSV/XLSX writer
│   ├── record/              # Download history
│   ├── tools/               # Utility functions
│   ├── custom/              # Constants
│   ├── gui_edition/         # ✅ Desktop GUI (CustomTkinter)
│   ├── cli_edition/         # CLI utilities
│   └── testers/             # Test helpers
│
├── static/
│   ├── images/              # Icons, logos
│   └── js/                  # Web UI assets (legacy)
│
└── tests/
    ├── test_gui_smoke.py    # 38 smoke tests cho GUI
    └── test_gui_launch.py   # Manual launch test
```

---

## 8. FAQ & Xử lý lỗi

### Q: "ModuleNotFoundError: No module named 'customtkinter'"

```bash
pip install customtkinter Pillow
```

### Q: "Python version error" hoặc "requires-python >=3.12,<3.13"

Project yêu cầu **Python 3.12.x** chính xác. Kiểm tra:
```bash
python --version
# Phải là 3.12.x
```

Nếu có nhiều Python version, dùng:
```bash
py -3.12 -m venv .venv
```

### Q: "Cookie hết hạn" / Video không tải được

- Cookie có thời hạn (thường 1-7 ngày)
- Cần lấy lại cookie mới → Settings → Import from Browser
- Hoặc paste cookie mới vào `settings.json`

### Q: "FFmpeg not found" / Video không có tiếng

- Cài FFmpeg (xem [Bước 1](#cài-ffmpeg-tùy-chọn-nhưng-khuyến-nghị))
- Hoặc chỉ định path FFmpeg trong Settings → Advanced → FFmpeg Path

### Q: Proxy / VPN cho TikTok

TikTok cần proxy nếu bạn ở Việt Nam/Trung Quốc:
```jsonc
// settings.json
{
    "tiktok_proxy": "http://127.0.0.1:7890"
}
```
Hoặc set trong GUI → Settings → Proxy.

### Q: Chạy test

```bash
# Smoke tests (không cần display)
python -m pytest tests/test_gui_smoke.py -v

# Launch test (cần display — tự đóng sau 10s)  
python -m pytest tests/test_gui_launch.py -v
```

### Q: Encoding error trên Windows CMD

```bash
# Set UTF-8 trước khi chạy
chcp 65001
python main.py
```

---

## Tóm tắt các câu lệnh chính

```bash
# === Setup ===
git clone https://github.com/JoeanAmier/TikTokDownloader.git
cd TikTokDownloader
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install customtkinter Pillow

# === Chạy ===
python main.py              # CLI mode
python main.py --gui        # GUI mode

# === Build .exe ===
pip install pyinstaller
pyinstaller gui.spec

# === Test ===
pip install pytest
python -m pytest tests/test_gui_smoke.py -v
```
