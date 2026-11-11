@echo off
setlocal EnableExtensions
title Instalador BygiooBIM para pyRevit
REM ==================================================================
REM  Instala o ACTUALIZA la extension BygiooBIM de pyRevit (Revit 2026)
REM  - Si junto a este .bat hay un archivo BygiooBIM.zip, lo usa.
REM  - Si no, descarga la ultima version desde GitHub.
REM  Ejecutarlo de nuevo = actualizar. No requiere permisos de administrador.
REM ==================================================================

set "BASE=C:\Autodesk\Extensiones"
set "DEST=%BASE%\BygiooBIM.extension"
set "URL=https://github.com/BygiooBIM/Pyrevit/archive/refs/heads/main.zip"
set "WORK=%TEMP%\BygiooBIM_instalador"
set "ZIP=%~dp0BygiooBIM.zip"

echo.
echo  ===============================================
echo   BygiooBIM - instalacion / actualizacion
echo  ===============================================
echo.

REM --- 1. Verificar pyRevit ------------------------------------------
where pyrevit >nul 2>&1
if errorlevel 1 (
    echo  [!] No se encontro pyRevit en este equipo.
    echo      Instala pyRevit 5.x primero: https://github.com/pyrevitlabs/pyRevit/releases
    echo      y vuelve a ejecutar este instalador.
    goto :fin_error
)

REM --- 2. Obtener el ZIP (local o desde GitHub) ----------------------
if exist "%WORK%" rmdir /s /q "%WORK%"
mkdir "%WORK%"

if exist "%ZIP%" (
    echo  [1/4] Usando el paquete local: %ZIP%
    copy /y "%ZIP%" "%WORK%\paquete.zip" >nul
) else (
    echo  [1/4] Descargando la ultima version desde GitHub...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "[Net.ServicePointManager]::SecurityProtocol='Tls12'; Invoke-WebRequest -UseBasicParsing -Uri '%URL%' -OutFile '%WORK%\paquete.zip'"
    if errorlevel 1 (
        echo  [!] No se pudo descargar. Si el repositorio es privado, pide el archivo BygiooBIM.zip
        echo      y ponlo en la misma carpeta que este .bat.
        goto :fin_error
    )
)

REM --- 3. Descomprimir -----------------------------------------------
echo  [2/4] Descomprimiendo...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Expand-Archive -Path '%WORK%\paquete.zip' -DestinationPath '%WORK%\x' -Force; Get-ChildItem -Recurse '%WORK%\x' | Unblock-File"
if errorlevel 1 goto :fin_error

REM El ZIP de GitHub trae una carpeta Pyrevit-main; el paquete local no.
set "SRC=%WORK%\x"
if exist "%WORK%\x\Pyrevit-main\BygiooBIM.tab" set "SRC=%WORK%\x\Pyrevit-main"
if not exist "%SRC%\BygiooBIM.tab" (
    echo  [!] El paquete no contiene BygiooBIM.tab. Archivo danado o incorrecto.
    goto :fin_error
)

REM --- 4. Copiar (reemplaza la version anterior) ---------------------
echo  [3/4] Instalando en %DEST% ...
if not exist "%BASE%" mkdir "%BASE%"
robocopy "%SRC%" "%DEST%" /MIR /NFL /NDL /NJH /NJS /NP >nul
if %ERRORLEVEL% GEQ 8 (
    echo  [!] Error al copiar archivos. Cierra Revit y vuelve a intentarlo.
    goto :fin_error
)

REM --- 5. Registrar la carpeta en pyRevit ----------------------------
echo  [4/4] Registrando la carpeta en pyRevit...
pyrevit extensions paths add "%BASE%" >nul 2>&1

rmdir /s /q "%WORK%" >nul 2>&1
echo.
if exist "%DEST%\version.txt" (
    set /p VER=<"%DEST%\version.txt"
)
echo  LISTO. BygiooBIM %VER% instalado en %DEST%
echo.
echo  Siguiente paso: abre Revit 2026 (o pulsa pyRevit ^> Reload si ya esta abierto).
echo  Aparecera la pestana BygiooBIM.
echo.
echo  Si no aparece: pyRevit ^> Settings ^> Custom Extension Directories ^>
echo  Add folder ^> %BASE% ^> Save Settings and Reload.
echo.
pause
exit /b 0

:fin_error
echo.
echo  La instalacion NO se completo. Envia una captura de esta ventana.
echo.
pause
exit /b 1
