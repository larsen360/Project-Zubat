$requirementsFile = "requirements.txt"
if (Test-Path $requirementsFile) {
    pip install -r $requirementsFile
} else { 
    pip install requests
    pip install beautifulsoup4

