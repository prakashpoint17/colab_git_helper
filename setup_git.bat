@echo off

REM Prompt user to enter repository URL
set /p REPO_URL="Enter your GitHub repository URL: "

REM Validate input is not empty
if "%REPO_URL%"=="" (
    echo Error: Repository URL cannot be empty.
    pause
    exit /b
)

REM Run Git Setup Commands
echo # Project Setup >> README.md
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo Setup completed successfully!
pause