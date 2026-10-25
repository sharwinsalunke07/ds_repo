@echo off
echo ========================================
echo Building Real-Time Emergency Scheduler
echo ========================================

REM Compile to MinGW bin directly (executes under Windows AppLocker policy)
g++ -std=c++17 -O2 -Wall -Isrc src\Scenario.cpp src\Logger.cpp src\Scheduler.cpp src\main.cpp -o C:\MinGW\bin\scheduler.exe

REM Also build local copy for portable distribution
g++ -std=c++17 -O2 -Wall -Isrc src\Scenario.cpp src\Logger.cpp src\Scheduler.cpp src\main.cpp -o scheduler.exe

if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] scheduler compiled successfully!
) else (
    echo [ERROR] Compilation failed.
)
