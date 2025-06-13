$requirementsFile = "requirements.txt"
if (Test-Path $requirementsFile) {
    python -m pip install -r $requirementsFile
} else {
    python -m pip install requests
    python -m pip install beautifulsoup4
}