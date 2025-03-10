@echo off

:: Find the Tomcat directory (simplified, specify or search)
set "BASE_DIR=C:\"
for /d %%i in ("%BASE_DIR%\apache-tomcat-*") do (
    set "TOMCAT_DIR=%%i"
    goto found
)

echo Tomcat directory not found!
exit /b 1

:found
echo Found Tomcat directory: %TOMCAT_DIR%

:: Move to bin folder
cd /d "%TOMCAT_DIR%\bin"

:: Restart Tomcat
echo Stopping Tomcat...
call shutdown.bat

timeout /t 5 /nobreak

echo Starting Tomcat...
call startup.bat

echo Tomcat restarted!