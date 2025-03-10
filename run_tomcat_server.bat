@echo off
setlocal

:: Set the base directory and search for tomcat folder
set "BASE_DIR=C:\"
for /d %%i in ("%BASE_DIR%\apache-tomcat-*") do (
    set "TOMCAT_DIR=%%i"
    goto found
)

echo Tomcat directory not found!
exit /b 1

:found
echo Found Tomcat directory: %TOMCAT_DIR%

:: Go to the bin directory
cd /d "%TOMCAT_DIR%\bin"

:: Shutdown Tomcat
echo Stopping Tomcat...
call shutdown.bat

timeout /t 5

:: Start Tomcat
echo Starting Tomcat...
call startup.bat

echo Tomcat restarted!

:: Return to original directory (optional, but recommended)
cd /d %WORKSPACE%

endlocal