#!/usr/bin/env bash
set -euo pipefail

MODEL_DIR="model"
MODEL_FILE="akanna-1.5b-q4_k_m.gguf"
MODEL_PATH="${MODEL_DIR}/${MODEL_FILE}"
MODEL_URL="https://huggingface.co/bartowski/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/Qwen2.5-1.5B-Instruct-Q4_K_M.gguf"
MIN_EXPECTED_BYTES=900000000

mkdir -p "${MODEL_DIR}"

file_size() {
  stat -c%s "$1" 2>/dev/null || stat -f%z "$1"
}

if [ -f "${MODEL_PATH}" ]; then
  existing_bytes=$(file_size "${MODEL_PATH}")
  if [ "${existing_bytes}" -ge "${MIN_EXPECTED_BYTES}" ]; then
    echo "Model already present at ${MODEL_PATH} (${existing_bytes} bytes). Skipping download."
    exit 0
  fi
  rm -f "${MODEL_PATH}"
fi

echo "Downloading ${MODEL_FILE} from Hugging Face..."
curl -L --fail --retry 3 --retry-delay 5 -o "${MODEL_PATH}.part" "${MODEL_URL}"
mv "${MODEL_PATH}.part" "${MODEL_PATH}"

final_bytes=$(file_size "${MODEL_PATH}")
if [ "${final_bytes}" -lt "${MIN_EXPECTED_BYTES}" ]; then
  echo "ERROR: downloaded file is only ${final_bytes} bytes, smaller than expected." >&2
  exit 1
fi

echo "Done. Model weights at ${MODEL_PATH} (${final_bytes} bytes)."
