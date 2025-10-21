@echo off
taskkill /f /im "mFTP.exe"
taskkill /f /im "mFTP Setup.exe"
rmdir /S /Q dist
rmdir /S /Q build
echo Installing dependencies...
pip install -r requirements.txt
echo Building the main application (mFTP.exe)...
pyinstaller --noconsole --onefile --add-data "icon.ico:." --icon="icon.ico" --name mFTP mFTP_Server.py
echo Cleaning up main application build artifacts...
del mFTP.spec
rmdir /s /q build
echo Building the setup application (mFTP Setup.exe)...
pyinstaller --onefile --name "mFTP Setup" --icon="icon.ico" --add-data "dist/mFTP.exe:." "mFTP_Server_Setup.py"
echo Cleaning up setup application build artifacts...
del *.spec
rmdir /s /q "build"
del /Q "dist\mFTP.exe"
echo All builds complete!