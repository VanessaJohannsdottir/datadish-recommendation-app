@REM # Starte 10 Cleaning-Prozesse parallel.
@REM # Jeder Prozess bekommt einen Teil der Reviews (insgesamt ca. 3,5 Mio.).
@REM # So wird das Cleaning gleichzeitig (parallel) ausgeführt und dauert deutlich kürzer

@echo off
start "" python cleaning_process.py --jam 5000 --start 0 --end 343450
start "" python cleaning_process.py --jam 5001 --start 343450 --end 686900
start "" python cleaning_process.py --jam 5002 --start 686900 --end 1030350
start "" python cleaning_process.py --jam 5003 --start 1030350 --end 1373800
start "" python cleaning_process.py --jam 5004 --start 1373800 --end 1717250
start "" python cleaning_process.py --jam 5005 --start 1717250 --end 2060700
start "" python cleaning_process.py --jam 5006 --start 2060700 --end 2404150
start "" python cleaning_process.py --jam 5007 --start 2404150 --end 2747600
start "" python cleaning_process.py --jam 5008 --start 2747600 --end 3091050
start "" python cleaning_process.py --jam 5009 --start 3091050 --end 3434505