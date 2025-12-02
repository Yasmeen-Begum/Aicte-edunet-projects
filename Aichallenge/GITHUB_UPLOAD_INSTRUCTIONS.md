# GitHub Upload Instructions

## Step-by-Step Guide to Upload to GitHub

### Prerequisites
- Git installed on your system
- GitHub account with access to the repository

### Method 1: Upload to Existing Repository (Recommended)

```bash
# Navigate to your project directory
cd C:\Users\DELL\Music\Medical_report

# Initialize git (if not already initialized)
git init

# Add the remote repository
git remote add origin https://github.com/Yasmeen-Begum/Aicte-edunet-projects.git

# Pull existing content (if any)
git pull origin main

# Create a new folder for this project in Aichallenge
mkdir -p Aichallenge/medical-report-summarizer
# Or on Windows:
# md Aichallenge\medical-report-summarizer

# Copy all project files to the new folder
# (You can do this manually or use commands)

# Add all files
git add .

# Commit with a message
git commit -m "Add RAG-Based Medical Report Summarizer with Personalized Nutrition"

# Push to the repository
git push origin main
```

### Method 2: Direct Upload via GitHub Web Interface

1. Go to: https://github.com/Yasmeen-Begum/Aicte-edunet-projects/tree/main/Aichallenge

2. Click "Add file" → "Upload files"

3. Drag and drop these files:
   - main.py
   - config.py
   - models.py
   - document_processor.py
   - vector_store.py
   - llm_manager.py
   - agents.py
   - ui.py
   - requirements.txt
   - README.md
   - PROJECT_REPORT.md
   - FEATURES.md
   - TESSERACT_SETUP.md
   - sample_report.txt
   - .gitignore

4. Add commit message: "Add RAG-Based Medical Report Summarizer"

5. Click "Commit changes"

### Method 3: Using GitHub Desktop

1. Open GitHub Desktop
2. File → Add Local Repository
3. Choose your project folder
4. Publish repository or push to existing remote
5. Select files to commit
6. Add commit message
7. Push to origin

### Files to Upload

**Core Application:**
- main.py
- config.py
- models.py
- document_processor.py
- vector_store.py
- llm_manager.py
- agents.py
- ui.py

**Dependencies:**
- requirements.txt

**Documentation:**
- README.md
- PROJECT_REPORT.md
- FEATURES.md
- TESSERACT_SETUP.md

**Example:**
- sample_report.txt

**Configuration:**
- .gitignore

**DO NOT Upload:**
- chroma_db/ (database files)
- outputs/ (generated PDFs)
- models/ (large model files)
- __pycache__/ (Python cache)
- .kiro/ (IDE files)
- medical_summarizer.py (old single file - replaced by modular version)

### Verify Upload

After uploading, verify at:
https://github.com/Yasmeen-Begum/Aicte-edunet-projects/tree/main/Aichallenge/medical-report-summarizer

### Update Repository README

Add this section to the main Aichallenge README:

```markdown
## Medical Report Summarizer

RAG-Based Medical Report Summarizer with Personalized Nutrition

- **Technology**: Python, LangChain, ChromaDB, CrewAI, Gradio
- **Features**: Disease detection, medication suggestions, recovery estimation, dietary recommendations
- **Location**: `/Aichallenge/medical-report-summarizer/`
- **Documentation**: See [README.md](./medical-report-summarizer/README.md)
```

### Troubleshooting

**Large File Error:**
If you get "file too large" error, make sure you're not uploading:
- chroma_db/ folder
- models/ folder (GGUF files are huge)
- outputs/ folder

**Permission Denied:**
Make sure you have write access to the repository.

**Merge Conflicts:**
If there are conflicts, pull first:
```bash
git pull origin main
# Resolve conflicts
git add .
git commit -m "Resolve conflicts"
git push origin main
```

## Quick Command Summary

```bash
cd C:\Users\DELL\Music\Medical_report
git init
git remote add origin https://github.com/Yasmeen-Begum/Aicte-edunet-projects.git
git add .
git commit -m "Add RAG-Based Medical Report Summarizer with Personalized Nutrition"
git push origin main
```

## Need Help?

If you encounter issues:
1. Check GitHub documentation: https://docs.github.com
2. Verify repository permissions
3. Ensure git is installed: `git --version`
