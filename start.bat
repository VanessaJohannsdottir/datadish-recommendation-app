@echo off
echo 🚀 Starting Docker container...
docker-compose up -d

echo  Waiting for Streamlit to become healthy...

:check
for /f %%i in ('docker inspect -f "{{.State.Health.Status}}" datadish-dashboard') do (
    if "%%i"=="healthy" (
        echo Streamlit is healthy and running at http://localhost:8501
        start http://localhost:8501
        goto :done
    ) else (
        echo Still starting...
        timeout /t 30 >nul
        goto :check
    )
)

:done
