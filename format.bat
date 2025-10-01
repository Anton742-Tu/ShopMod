@echo off
echo 🎨 Formatting code with Black and Isort...
black .
isort .
echo ✅ Formatting complete!