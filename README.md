# Simple CAPTCHA Solver GUI

A clean, standalone GUI application for solving CAPTCHAs using AI.

## 🚀 Quick Start

1. **Double-click**: `run_simple_gui.bat`
2. **Choose method**: Clipboard, File Upload, or Screen Capture
3. **Solve CAPTCHAs**: Instant results with auto-copy to clipboard

## 📋 Files

- `simple_captcha_gui.py` - Main GUI application
- `run_simple_gui.bat` - Windows launcher
- `captcha.onnx` - AI model for CAPTCHA solving
- `tokenizer_base.py` - Text processing helper
- `app.py` - Original solver core
- `requirements_simple.txt` - Required packages
- Sample CAPTCHA images for testing

## 💡 Usage

### Method 1: Clipboard (Recommended)
1. Right-click any CAPTCHA image
2. Select "Copy Image"
3. Click "Solve from Clipboard"
4. Solution copies automatically!

### Method 2: Auto-Monitor
1. Click "Start Auto-Monitor"
2. Copy any CAPTCHA from anywhere
3. Automatic solving with popup notification

### Method 3: File Upload
1. Save CAPTCHA as image file
2. Click "Load Image File"
3. Instant solving

### Method 4: Screen Capture
1. Click "Capture Screen Region"
2. Select CAPTCHA area on screen
3. Automatic solving

## 📦 Installation

### Method 1: Using UV (Recommended - Faster)

UV is a modern Python package manager that's significantly faster than pip.

1. **Install UV** (if not already installed):
   ```powershell
   # On Windows (PowerShell)
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements_simple.txt
   ```

3. **Run the application**:
   ```bash
   uv run python simple_captcha_gui.py
   ```

### Method 2: Using Traditional pip

```bash
pip install -r requirements_simple.txt
python simple_captcha_gui.py
```

## ✅ Features

- ✅ No browser automation required
- ✅ Works with any website
- ✅ Instant clipboard copying
- ✅ Real-time monitoring
- ✅ Clean, simple interface
- ✅ High accuracy AI model
