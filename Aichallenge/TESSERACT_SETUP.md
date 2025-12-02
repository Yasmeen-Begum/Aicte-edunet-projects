# Tesseract OCR Setup for Image Support

To enable image upload and OCR text extraction, you need to install Tesseract OCR on your system.

## Windows Installation

### Option 1: Using Installer (Recommended)

1. Download the Tesseract installer from:
   https://github.com/UB-Mannheim/tesseract/wiki

2. Run the installer (tesseract-ocr-w64-setup-v5.x.x.exe)

3. During installation, note the installation path (default: `C:\Program Files\Tesseract-OCR`)

4. Add Tesseract to your system PATH:
   - Right-click "This PC" → Properties → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all windows

5. Restart your terminal/command prompt

6. Verify installation:
   ```bash
   tesseract --version
   ```

### Option 2: Using Chocolatey

```bash
choco install tesseract
```

## Linux Installation

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

### Fedora:
```bash
sudo dnf install tesseract
```

## macOS Installation

### Using Homebrew:
```bash
brew install tesseract
```

## Verify Installation

After installation, verify Tesseract is working:

```bash
tesseract --version
```

You should see output like:
```
tesseract 5.x.x
```

## Troubleshooting

If you get an error like "pytesseract.pytesseract.TesseractNotFoundError":

1. Make sure Tesseract is installed
2. Make sure Tesseract is in your system PATH
3. Restart your terminal/IDE
4. If still not working, you can manually set the path in Python:

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Supported Image Formats

Once Tesseract is installed, the application supports:
- JPG/JPEG
- PNG
- Other image formats supported by PIL/Pillow

## Note

Without Tesseract OCR installed, the application will still work for PDF, TXT, and DOCX files. Image upload will show an error message prompting you to install Tesseract.
