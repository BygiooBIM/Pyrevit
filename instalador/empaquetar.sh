#!/usr/bin/env bash
# Genera BygiooBIM_Instalador_v<version>.zip para compartir con compañeros.
# Uso: bash instalador/empaquetar.sh <carpeta_salida>
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$(cd "${1:-.}" && pwd)"
VER="$(tr -d '\r\n' < "$ROOT/version.txt")"
TMP="$(mktemp -d)"
# Paquete de la extensión: solo lo que pyRevit necesita
(cd "$ROOT" && zip -qr "$TMP/BygiooBIM.zip" BygiooBIM.tab lib README.md version.txt -x '*.pyc' '*__pycache__*')
cp "$ROOT/instalador/Instalar_BygiooBIM.bat" "$TMP/"
printf 'BygiooBIM %s - pyRevit para Revit 2026\r\n\r\n1. Descomprime esta carpeta.\r\n2. Doble clic en Instalar_BygiooBIM.bat (deja BygiooBIM.zip junto a el).\r\n3. Abre Revit 2026 o pulsa pyRevit > Reload.\r\n\r\nRequisito: pyRevit 5.x instalado.\r\nPara actualizar: ejecuta el .bat de la version nueva.\r\n' "$VER" > "$TMP/LEEME.txt"
rm -f "$OUT/BygiooBIM_Instalador_v$VER.zip"
(cd "$TMP" && zip -q "$OUT/BygiooBIM_Instalador_v$VER.zip" Instalar_BygiooBIM.bat BygiooBIM.zip LEEME.txt)
rm -rf "$TMP"
echo "$OUT/BygiooBIM_Instalador_v$VER.zip"
