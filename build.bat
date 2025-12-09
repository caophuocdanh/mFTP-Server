@echo off
echo --- CLEANING UP ---
taskkill /f /im "mFTP.exe" 2>nul
taskkill /f /im "mFTP Setup.exe" 2>nul
rmdir /S /Q dist build 2>nul
del /Q *.spec 2>nul

echo --- INSTALLING REQS ---
:: Chỉ cần dòng này là đủ cài tất cả thư viện cần thiết
pip install -r requirements.txt

echo --- BUILDING MAIN APP (Windowed for GUI) ---
pyinstaller --noconsole --onefile --add-data "icon.ico:." --icon="icon.ico" --name mFTP mFTP_Server.py

echo --- BUILDING SETUP (GUI + Admin Require) ---
pyinstaller --noconsole --onefile --uac-admin --name "mFTP Setup" --icon="icon.ico" --add-data "dist/mFTP.exe:." "mFTP_Server_Setup.py"

echo --- CLEANUP ---
del *.spec
rmdir /s /q build
del /Q "dist\mFTP.exe"

echo --- DONE! Check dist/mFTP Setup.exe ---