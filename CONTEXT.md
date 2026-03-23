# TikTokDownloader — Session Context & Progress

> **Mục đích:** File này ghi lại toàn bộ những gì đã tìm hiểu và quyết định trong quá trình phát triển,
> để khi sang session mới vẫn có thể tiếp tục mà không mất ngữ cảnh.
>
> **Cập nhật lần cuối:** 2026-03-24 (All 8 phases GUI complete ✅)

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
  - `gui_edition/` — ✅ HOÀN THÀNH (CustomTkinter desktop app, 16 modules)
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
- `gui_edition/` — **100% hoàn thành** (8 phases, 16 modules, ~120KB code)
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

## 2.5 GUI Desktop — Tiến Độ Phát Triển (HOÀN THÀNH ✅)

**Tài liệu cấu trúc:** `src/gui_edition/GUI_STRUCTURE.md`

### Tất cả files đã tạo (Phase 1–8)

| Category | Files | Tổng size |
|----------|-------|-----------|
| **Core** | `__init__.py`, `app.py`, `async_handler.py`, `backend_bootstrap.py`, `console_adapter.py`, `coroutine_factory.py`, `download_manager.py`, `gui_main.py`, `theme.py` | ~39KB |
| **Frames** | `download_frame.py` (39KB), `settings_frame.py` (43KB), `monitor_frame.py` (12KB) | ~94KB |
| **Widgets** | `sidebar.py`, `log_panel.py`, `progress_card.py`, `url_input.py`, `status_bar.py`, `error_dialog.py`, `about_dialog.py` | ~31KB |
| **Packaging** | `gui_launcher.py`, `gui.spec` | ~2KB |
| **Tests** | `tests/test_gui_smoke.py`, `tests/test_gui_launch.py` | ~6KB |

### Dependencies thêm mới
- `customtkinter>=5.2.0` — Modern dark-mode Tkinter
- `Pillow>=10.0.0` — Image support cho logo/icon

### Tính năng đã implement

| Category | Count | Chi tiết |
|----------|-------|---------|
| Download modes | 15 | 11 Douyin + 4 TikTok (Account/Link/Mix/Live/Collection/Collects/Music/Comment/User/Hot/Search×4) |
| Settings controls | 20+ | Cookie, proxy, format, toggles, paths, text replace, record delete |
| Monitor | 6 | Clipboard listener, queue counters, log, stop, clear, reset |
| UI components | 7 | Sidebar, LogPanel, ProgressCard, URLInput, StatusBar, ErrorDialog, AboutDialog |
| Backend integration | 4 | BackendBootstrap, CoroutineFactory, DownloadManager, periodic cookie refresh |

### Deferred features (🟡)
- Check update button — cần API endpoint
- Language switch — backend i18n phức tạp, ít giá trị cho GUI
- Web API server toggle — chạy riêng bằng CLI

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

### Nghiên cứu & Phân tích
- [x] Đọc & phân tích toàn bộ cấu trúc project (19 packages)
- [x] Đọc `README.md`, `main.py`, `pyproject.toml`
- [x] Đọc code `TikTokDownloader.py` (463 dòng — lớp chính)
- [x] Phân tích `main_server.py` (762 dòng) — 16 endpoints
- [x] So sánh Web UI vs Mobile App vs Desktop App → Desktop (CustomTkinter)
- [x] Tạo `PROJECT_OVERVIEW.md`, `CONTEXT.md`, `GUI_STRUCTURE.md`

### Phase 1: Foundation ✅
- [x] `async_handler.py` — thread-safe asyncio ↔ GUI bridge
- [x] `console_adapter.py` — GUIConsole thay thế Rich
- [x] Dependencies: `customtkinter>=5.2.0`, `Pillow>=10.0.0`

### Phase 2: Core UI Shell ✅
- [x] `theme.py` — dark mode tokens
- [x] `app.py` — CTk window 800×600, sidebar, status bar
- [x] `widgets/` — Sidebar, LogPanel, URLInput, ProgressCard, StatusBar
- [x] `gui_main.py` entry point
- [x] Frame stubs: download, settings, monitor

### Phase 3: SettingsFrame ✅
- [x] Cookie management (paste + browser import via rookiepy)
- [x] Directory picker, storage format, platform toggles
- [x] Proxy, name format, folder mode, advanced settings
- [x] Text replacement rules (Section 5)
- [x] Delete download records (Section 6)
- [x] Save / Reset buttons

### Phase 4: DownloadFrame P1 ✅
- [x] Platform toggle (Douyin ↔ TikTok)
- [x] Tabs: Account, Link, Mix
- [x] Download progress integration + queue management
- [x] `download_manager.py` — TaskInfo/TaskStatus/DownloadManager

### Phase 5: DownloadFrame P2 ✅
- [x] Tabs: Live, Collection (3 actions), Data (Comment/User/Hot), Search (4 channels)
- [x] `_UnavailableOverlay` for Douyin-only tabs when TikTok selected
- [x] `coroutine_factory.py` — 11 factory functions

### Phase 6: MonitorFrame ✅
- [x] Clipboard listener toggle, auto-detect links, queue counters
- [x] Log panel, stop button, clear/reset, clean shutdown

### Phase 7: Integration & Polish ✅
- [x] `backend_bootstrap.py` — Database/Settings/Cookie/Parameter init
- [x] Coroutine wiring (all 11 modes → download_manager)
- [x] Periodic cookie refresh (daemon thread)
- [x] FFmpeg status indicator
- [x] `error_dialog.py` + `about_dialog.py`

### Phase 8: Packaging & Testing ✅
- [x] `gui_launcher.py` + `gui.spec` (PyInstaller one-dir windowed)
- [x] `--gui` flag in `main.py`
- [x] `test_gui_smoke.py` — 31 passed, 7 skipped, 0 failed
- [x] `test_gui_launch.py` — manual launch auto-destroy
- [x] Lazy `__init__.py` to avoid cascading imports

## 4. Việc Còn Lại (Deferred / Future)

- [ ] Check update button (cần API endpoint để so sánh version)
- [ ] Language switch UI (backend i18n bằng gettext, phức tạp)
- [ ] Web API server toggle từ GUI (hiện chạy riêng `main.py api`)
- [ ] Cross-platform test macOS / Linux (cần CI hoặc máy tương ứng)
- [ ] Assets: icon.ico, icon.png, logo.png (placeholder)

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
| `gui_edition/GUI_STRUCTURE.md` | Cấu trúc + trạng thái tính năng — **bắt buộc tuân thủ** |

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
