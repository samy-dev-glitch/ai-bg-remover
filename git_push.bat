@echo off
echo ==========================================
echo      AI Background Remover - Final Fix
echo ==========================================
echo.
echo [1/5] Removing old Git config...
rmdir /s /q .git 2>nul

echo.
echo [2/5] Initializing Git...
git init
git add .
git commit -m "Fix: Resolve HTML syntax error and Alt Text button logic"
git branch -M main

echo.
echo [3/5] Linking to GitHub...
git remote add origin https://github.com/samy-dev-glitch/ai-bg-remover.git

echo.
echo [4/5] Pushing to GitHub (Force)...
git push -f origin main

echo.
echo ==========================================
echo [SUCCESS] Updates pushed!
echo Go to Vercel and check the new deployment.
echo ==========================================
pause
