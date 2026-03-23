# TikTokDownloader — Session Context & Progress

> **Mục đích:** File này ghi lại toàn bộ những gì đã tìm hiểu và quyết định trong quá trình phát triển,
> để khi sang session mới vẫn có thể tiếp tục mà không mất ngữ cảnh.
>
> **Cập nhật lần cuối:** 2026-03-23 (Phase 1 GUI done)

---

## 1. Tổng Quan Đã Tìm Hiểu

### Project là gì?
- **Tên:** DouK-Downloader (tên cũ: TikTokDownloader)
- **Version:** 5.8 · **Python 3.12** · **License:** GPL-3.0
- **Tác giả gốc:** JoeanAmier
- **Chức năng:** Thu thập dữ liệu & tải video/ảnh từ **Douyin (抖音)** và **TikTok**
- **Tài liệu chi tiết:** xem `PROJECT_OVERVIEW.md`

### Kiến trúc chính
- **19 packages** trong `src/`:
  - `application/` — Entry point, 3 chế độ chạy
  - `interface/` — 21 API module (Douyin + TikTok endpoints)
  - `config/` — `parameter.py` (41KB) + `settings.py`
  - `encrypt/` — 8 thuật toán anti-bot (aBogus, xBogus, msToken…)
  - `extract/` — `extractor.py` (52KB) parser response data
  - `downloader/` — `download.py` (30KB) multi-thread download
  - `models/` — 12 Pydantic models
  - `storage/` — CSV, XLSX, SQLite, TXT output
  - `link/` — URL extraction & short URL resolver
  - `record/` — Logging system
  - `tools/` — 17 utility modules
  - `translation/` — i18n (zh_CN ↔ en_US)
  - `manager/` — Database + DownloadRecorder
  - `module/` — Cookie management
  - `custom/` — Constants
  - `gui_edition/` — 🟡 ĐANG PHÁT TRIỂN (CustomTkinter desktop app)
  - `tui_edition/` — ⛔ Stub classes rỗng
  - `cli_edition/` — CLI utilities
  - `testers/` — Testing utilities

### 3 chế độ chạy
1. **Terminal CLI** (`main_terminal.py`, 72KB) — đầy đủ nhất
2. **Web API** (`main_server.py`, 28KB) — FastAPI tại `0.0.0.0:5555`
3. **Clipboard Monitor** (`main_monitor.py`, 4KB) — chạy nền

### Stack công nghệ
- HTTPX (async HTTP), FastAPI + Uvicorn, Pydantic v2
- aiosqlite, aiofiles, openpyxl
- Rich (console), rookiepy (cookie), gmssl (SM3/SM4)
- lxml, emoji, pyperclip
- Docker, PyInstaller, uv, Ruff

---

## 2. Phân Tích Web UI / App UI

### Kết luận phân tích `gui_edition/`
- `gui_edition/` — **0% hoàn thành**, chỉ có `__init__.py` trống
- `tui_edition/` — **0% hoàn thành**, chỉ có `class App: pass` và `class Setting: pass`
- Menu "Web UI 模式" → trỏ đến `disable_function()` hiển thị "đang tái cấu trúc"
- `__web_ui_object` — đã bị xóa hoàn toàn, chỉ còn comment
- Không có HTML, CSS, JS frontend nào (ngoài file mã hóa anti-bot)
- Không có framework UI nào trong dependencies

### Web API hiện tại — Gap Analysis (`main_server.py`, 762 dòng)

**16 endpoints đã có:**
- `/douyin/detail`, `/douyin/account`, `/douyin/mix`, `/douyin/live` — lấy data Douyin
- `/douyin/comment`, `/douyin/reply` — bình luận Douyin
- `/douyin/share` — resolve short URL Douyin
- `/douyin/search/general|video|user|live` — 4 loại tìm kiếm Douyin
- `/tiktok/detail`, `/tiktok/account`, `/tiktok/mix`, `/tiktok/live`, `/tiktok/share` — TikTok
- `/settings` (GET/POST), `/token` (GET)

**Hạn chế quan trọng — API chỉ trả JSON, KHÔNG tải file:**

| Tính năng thiếu | Mức độ |
|---|---|
| Download file video/ảnh | 🔴 Rất cao — API chỉ trả URL, không trigger download |
| Download hàng loạt (batch) | 🔴 Rất cao |
| Thu livestream (ffmpeg) | 🔴 Cao |
| Cookie management qua UI | 🟡 Trung bình — `rookiepy` cần browser local |
| Clipboard monitor | 🟡 Trung bình — browser không hỗ trợ |
| Quản lý filesystem/thư mục lưu | 🟡 Trung bình |
| Hot/trending, user profile | 🟢 Thấp — thiếu endpoint |
| TikTok search, TikTok comment | 🟢 Thấp — chỉ có Douyin |

**Kết luận:** API hiện tại đạt ~50% — thu thập data tốt nhưng không tải file.

### So sánh hướng phát triển: Web UI vs Mobile App vs Desktop App

| Tiêu chí | 🌐 Web UI | 📱 Mobile App | 🖥️ Desktop App |
|---|---|---|---|
| **Tái sử dụng code** | ✅ Cao — FastAPI backend có sẵn | ⚠️ Chỉ dùng API, viết lại UI + logic | ✅ 100% Python logic |
| **Stack** | React/Vue + Vite | React Native / Flutter | CustomTkinter / PyQt6 |
| **Download files** | ✅ Server tải → browser download | ⚠️ iOS hạn chế, Android cần permission | ✅ Tải trực tiếp vào ổ cứng |
| **Cookie injection** | ✅ User paste cookie vào form | ❌ Khó — mobile browser không export | ✅ Full `rookiepy` + clipboard |
| **Anti-bot bypass** | ✅ Chạy trên server, giống CLI | ⚠️ Phải port aBogus/xBogus | ✅ Chạy local, giống CLI |
| **Effort phát triển** | ⚡ 2-4 tuần | 🔧 8-16 tuần | 🔧 4-8 tuần |
| **Phân phối** | ✅ Docker/localhost | ❌ App Store reject | ✅ `.exe` / `.dmg` self-distribute |
| **ffmpeg (livestream)** | ✅ Chạy trên server | ❌ Không thực tế | ✅ Chạy process local |
| **Clipboard monitor** | ⚠️ Hạn chế trong browser | ⚠️ Background hạn chế | ✅ Full access `pyperclip` |
| **Filesystem access** | ⚠️ Qua server, gián tiếp | ⚠️ Sandbox | ✅ Native, chọn thư mục thoải mái |
| **Cross-platform** | ✅ Tự động | ⚠️ iOS + Android riêng | ✅ PyInstaller Win/Mac/Linux |
| **UI quality** | ⭐⭐⭐ Đẹp nhất | ⭐⭐⭐ Native feel | ⭐⭐ Kém đẹp hơn web |

**Kết luận Mobile App:** **Không khả thi** — App Store reject, cookie khó, ffmpeg không chạy, effort x4-8.

### Desktop App — Phân tích chi tiết 3 hướng

| Hướng | Stack | Effort | Ưu điểm | Nhược điểm |
|---|---|---|---|---|
| **Electron/Tauri** | Web UI (React) + wrapper | 3-5 tuần | Đẹp, cross-platform, tái dùng Web UI | Electron 150MB, Tauri cần Rust |
| **Python native** | CustomTkinter / PyQt6 | 4-8 tuần | Pure Python, dùng lại toàn bộ logic | UI kém đẹp hơn web |
| **Web UI local** | FastAPI + React, localhost | 2-4 tuần | Đẹp nhất, nhẹ nhất | Mở browser, không native feel |

### Quyết định: Python Native GUI (CustomTkinter) ✅

**Lý do chọn:**
- Pure Python → không cần Node.js/Rust/web tooling
- Dùng lại 100% logic từ `main_terminal.py` (TikTok class)
- `customtkinter` cho UI hiện đại hơn tkinter thuần
- `pyproject.toml` đã có PyInstaller support → đóng gói `.exe` dễ
- Clipboard monitor (`pyperclip`) hoạt động native
- `rookiepy` cookie extraction hoạt động bình thường
- ffmpeg livestream recording hoạt động
- Filesystem access native — chọn thư mục thoải mái

**Kế hoạch tích hợp:**
- `gui_edition/` đã có sẵn (trống) → viết code vào đây
- Tạo `TikTokGUI` class kế thừa/wrap `TikTok` class từ `main_terminal.py`
- Dùng `asyncio` + threading để tránh block GUI thread
- Progress tracking qua callback thay vì Rich console

---

## 2.5 GUI Desktop — Tiến Độ Phát Triển

**Tài liệu cấu trúc:** `src/gui_edition/GUI_STRUCTURE.md`

### Files đã tạo (Phase 1 — Foundation)

| File | Vai trò |
|---|---|
| `gui_edition/__init__.py` | Package init, export `App` |
| `gui_edition/async_handler.py` | Background asyncio loop ↔ GUI thread bridge |
| `gui_edition/console_adapter.py` | `GUIConsole` thay thế `ColorfulConsole` cho GUI |
| `gui_edition/frames/__init__.py` | Frames package init |

### Dependencies thêm mới
- `customtkinter>=5.2.0` — Modern dark-mode Tkinter
- `Pillow>=10.0.0` — Image support cho logo/icon

---

## 2.6 Database Schema — `DouK-Downloader.db`

**Engine:** SQLite via `aiosqlite` · **File:** `src/manager/database.py` (145 dòng) · **Path:** `PROJECT_ROOT/DouK-Downloader.db`

**GUI dùng lại 100% — không cần thêm DB.**

| Table | Columns | Mục đích | GUI sử dụng |
|---|---|---|---|
| `config_data` | `NAME TEXT PK`, `VALUE INTEGER (0\|1)` | Cờ ON/OFF | SettingsFrame toggles |
| `option_data` | `NAME TEXT PK`, `VALUE TEXT` | Cài đặt text | SettingsFrame dropdowns |
| `download_data` | `ID TEXT PK` | ID đã tải (tránh trùng) | Backend tự check |
| `mapping_data` | `ID TEXT PK`, `NAME TEXT`, `MARK TEXT` | Map ID → nickname | Name format tự động |

**Defaults trong `config_data`:**

| NAME | VALUE | Ý nghĩa |
|---|---|---|
| `Record` | `1` | Ghi log download record (ON) |
| `Logger` | `0` | Ghi log file (OFF) |
| `Disclaimer` | `0` | Đã chấp nhận disclaimer (chưa) |

**Defaults trong `option_data`:**

| NAME | VALUE |
|---|---|
| `Language` | `zh_CN` |

**API chính:**
- `read_config_data()` / `update_config_data(name, value)` → toggle ON/OFF
- `read_option_data()` / `update_option_data(name, value)` → settings text
- `has_download_data(id)` / `write_download_data(id)` / `delete_download_data(ids)` → download tracking
- `read_mapping_data(id)` / `update_mapping_data(id, name, mark)` → user nickname cache
- Khởi tạo: `async with Database() as db:` (auto-create tables + defaults)

---

## 3. Việc Đã Làm

- [x] Đọc & phân tích toàn bộ cấu trúc project (19 packages)
- [x] Đọc `README.md`, `main.py`, `pyproject.toml`
- [x] Đọc code `TikTokDownloader.py` (463 dòng — lớp chính)
- [x] Kiểm tra `gui_edition/`, `tui_edition/`, `static/` → đều trống
- [x] Tìm kiếm references Web UI trong toàn bộ codebase → không có
- [x] Tạo `PROJECT_OVERVIEW.md` — tài liệu tổng quan
- [x] Tạo `CONTEXT.md` — file ngữ cảnh này
- [x] Phân tích `main_server.py` (762 dòng) — 16 endpoints, thiếu download
- [x] So sánh Web UI vs Mobile App → Web UI thắng
- [x] So sánh Web UI vs Desktop App → Desktop chọn cho native feel
- [x] Phân tích 3 hướng Desktop (Electron/Tauri, Python native, Web local)
- [x] Quyết định: Python Native GUI (CustomTkinter)
- [x] Tạo `GUI_STRUCTURE.md` — cấu trúc project desktop app
- [x] **Phase 1 Foundation:** `async_handler.py`, `console_adapter.py`, deps

## 4. Việc Cần Làm Tiếp

- [ ] Viết `gui_edition/theme.py` — bảng màu, font tokens
- [ ] Viết `gui_edition/app.py` — cửa sổ chính + sidebar nav + status bar
- [ ] Viết `gui_edition/widgets/` — LogPanel, ProgressCard, URLInput, Sidebar
- [ ] Viết `gui_edition/frames/download_frame.py` — tab Download
- [ ] Viết `gui_edition/frames/settings_frame.py` — tab Settings
- [ ] Viết `gui_edition/frames/monitor_frame.py` — tab Monitor
- [ ] Tạo `gui_main.py` — entry point
- [ ] Cookie management UI (paste + auto-detect từ browser)
- [ ] Download progress tracking (progress bar + log)
- [ ] Tích hợp backend (`TikTok`, `Parameter`, `Database`)
- [ ] Đóng gói PyInstaller → `.exe`
- [ ] Testing

---

## 5. Files Quan Trọng Để Đọc Lại

| File | Lý do |
|---|---|
| `src/application/TikTokDownloader.py` | Lớp chính, lifecycle, menu |
| `src/application/main_server.py` (762 dòng) | 16 FastAPI endpoints — cần bổ sung download |
| `src/application/main_terminal.py` (72KB) | Logic đầy đủ nhất — tham khảo cho UI flow |
| `src/config/parameter.py` (41KB) | Tất cả params & settings |
| `src/extract/extractor.py` (52KB) | Data parser — hiểu output format |
| `src/downloader/download.py` (30KB) | Download engine — cần wrap thành API |
| `src/manager/database.py` (145 dòng) | DB schema, CRUD — GUI dùng lại trực tiếp |
| `PROJECT_OVERVIEW.md` | Tổng quan project |
| `gui_edition/GUI_STRUCTURE.md` | Cấu trúc + danh sách tính năng — **bắt buộc tuân thủ** |

---

## 6. Ghi Chú Kỹ Thuật

- Cookie **bắt buộc** để tải video chất lượng cao
- Hỗ trợ đọc cookie từ Chrome/Edge/Firefox qua `rookiepy`
- Thuật toán `aBogus` là anti-bot signature quan trọng nhất
- `static/js/` chứa JS implementation của X-Bogus và a_bogus (reference, không dùng cho UI)
- Project dùng `aiosqlite` lưu config + download records
- Multilingual qua gettext (locale/zh_CN, locale/en_US)
- `APIServer` kế thừa `TikTok` (từ `main_terminal.py`) → có truy cập đầy đủ logic CLI
- Token auth header tùy chọn (`is_valid_token()` trong `custom/function.py`)
