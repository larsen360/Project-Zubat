$requirementsFile = "requirements.txt"
if (Test-Path $requirementsFile) {
    python -m pip install -r $requirementsFile
} else {
    py -m pip install requests
    py -m pip install beautifulsoup4
    py -m pip install selenium
    py -m pip install undetected-chromedriver
    py -m pip install pillow
    py -m pip install setuptools
    py -m pip install pytesseract
}