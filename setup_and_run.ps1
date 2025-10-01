# DemandForge Setup and Run Script
# PowerShell script to set up and launch the application

Write-Host "🔨 DemandForge - Setup and Launch" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "1. Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host "   $pythonVersion" -ForegroundColor Green

# Check if requirements are installed
Write-Host ""
Write-Host "2. Checking installed packages..." -ForegroundColor Yellow
$streamlit = pip show streamlit 2>&1 | Select-String "Version"
if ($streamlit) {
    Write-Host "   ✅ Streamlit: $streamlit" -ForegroundColor Green
} else {
    Write-Host "   ❌ Streamlit not found. Installing..." -ForegroundColor Red
    pip install -r requirements.txt
}

# Verify project structure
Write-Host ""
Write-Host "3. Verifying project structure..." -ForegroundColor Yellow
$requiredFiles = @("app.py", "requirements.txt", "README.md")
$requiredDirs = @("models", "agents", "integrations", "utils", "tests")

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $file missing!" -ForegroundColor Red
    }
}

foreach ($dir in $requiredDirs) {
    if (Test-Path $dir) {
        Write-Host "   ✅ $dir/" -ForegroundColor Green
    } else {
        Write-Host "   ❌ $dir/ missing!" -ForegroundColor Red
    }
}

# Run tests (optional)
Write-Host ""
Write-Host "4. Would you like to run tests first? (y/n)" -ForegroundColor Yellow
$runTests = Read-Host
if ($runTests -eq "y") {
    Write-Host "   Running tests..." -ForegroundColor Cyan
    pytest tests/ -v
}

# Launch application
Write-Host ""
Write-Host "5. Launching DemandForge..." -ForegroundColor Yellow
Write-Host "   🌐 Opening browser at http://localhost:8501" -ForegroundColor Cyan
Write-Host "   ⚡ Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""
Write-Host "=================================" -ForegroundColor Cyan

# Start Streamlit
streamlit run app.py
