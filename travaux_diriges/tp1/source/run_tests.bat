@echo off
setlocal enabledelayedexpansion

set orders=ijk jik ikj kij kji jki
set sizes=1024 2048

for %%o in (%orders%) do (
    for %%s in (%sizes%) do (
        echo Running LOOP_ORDER=%%o n=%%s
        set LOOP_ORDER=%%o
        TestProductMatrix.exe %%s
        echo.
    )
)