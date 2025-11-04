@echo off
REM Build script for Cloud Architect AI Docker container

echo Building Cloud Architect AI Docker image...

REM Build the Docker image
docker build -t cloud-architect-ai .

if %ERRORLEVEL% EQU 0 (
    echo ✅ Docker image built successfully!
    echo.
    echo To run the container locally:
    echo docker run -p 8080:8080 -e GEMINI_API_KEY=your_api_key_here cloud-architect-ai
    echo.
    echo To test the container:
    echo docker run -p 8080:8080 --env-file .env cloud-architect-ai
) else (
    echo ❌ Docker build failed!
    exit /b 1
)