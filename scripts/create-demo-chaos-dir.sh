#!/usr/bin/env bash
# Creates demo/chaos: many subdirs and empty files of diverse types so that
# the CLI scan shows high entropy ("High entropy... lots of disorder... recommend organizing.").
# Usage: ./scripts/create-demo-chaos-dir.sh
# Output: prints the absolute path of the created folder (demo/chaos).

set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHAOS="${ROOT}/demo/chaos"

# Extensions supported by wizard404_core (subset of SUPPORTED_EXTENSIONS)
# We use 22 extensions so num_ext > 12; we keep few files per ext so total/num_ext < 8.
EXTS=(.txt .md .pdf .py .js .json .csv .log .xml .html .docx .xlsx .png .jpg .svg .mp3 .mp4 .sh .yml .sql .php .jl .go .rs .yaml .ini .conf .tex .rst .ipynb)

# Subdirs: mixed depth, no order (chaos)
SUBDIRS=(
  proyectos
  proyectos/viejo
  proyectos/viejo/backup
  descargas
  descargas/2024
  descargas/2024/enero
  tmp
  tmp/cache
  docs
  docs/legal
  docs/legal/contratos
  codigo
  codigo/rust
  codigo/python
  codigo/python/scripts
  backup
  media
  media/audio
  media/video
  misc
  cosas
  cosas/old
  cosas/old/archived
  rootfiles
)

# Base names for files (avoid same name per dir)
BASENAMES=(file data doc report image notes draft readme config sample test temp out in)

# Remove previous run so demo is reproducible
rm -rf "$CHAOS"
mkdir -p "$CHAOS"

ext_idx=0
file_count=0

for subdir in "${SUBDIRS[@]}"; do
  mkdir -p "${CHAOS}/${subdir}"
  # Create 2-4 files per subdir with different extensions (rotate)
  for i in 0 1 2; do
    ext="${EXTS[$ext_idx]}"
    base="${BASENAMES[$(( (file_count + i) % ${#BASENAMES[@]} ))]}"
    name="${base}_${subdir//\//_}_${i}${ext}"
    touch "${CHAOS}/${subdir}/${name}"
    ((ext_idx = (ext_idx + 1) % ${#EXTS[@]})) || true
  done
  ((file_count += 3)) || true
done

# Add a few more files at root to bump total and keep ratio < 8
for i in 0 1 2 3 4 5 6 7; do
  ext="${EXTS[$ext_idx]}"
  touch "${CHAOS}/root_${i}${ext}"
  ((ext_idx = (ext_idx + 1) % ${#EXTS[@]})) || true
done

echo "Created: ${CHAOS}"
echo "Use this path in the CLI (Scan) to see high entropy and rich stats."
echo "${CHAOS}"
