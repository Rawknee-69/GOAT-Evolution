#!/usr/bin/env bash
set -euo pipefail

if ! command -v git >/dev/null 2>&1; then
  echo "git is required"
  exit 1
fi
if ! command -v hf >/dev/null 2>&1; then
  echo "Install huggingface_hub CLI first: pip install -U huggingface_hub"
  exit 1
fi

HF_USER="${1:-}"
SPACE_NAME="${2:-}"

if [[ -z "${HF_USER}" || -z "${SPACE_NAME}" ]]; then
  echo "Usage: bash scripts/deploy_hf_space.sh <hf-username> <space-name>"
  exit 1
fi

SPACE_ID="${HF_USER}/${SPACE_NAME}"
SPACE_REMOTE_URL="https://huggingface.co/spaces/${SPACE_ID}"

echo "Creating Space (if it does not exist): ${SPACE_ID}"
hf repo create "${SPACE_ID}" --type space --space_sdk docker -y || true

if git remote | rg -x "hf-space" >/dev/null 2>&1; then
  git remote set-url hf-space "${SPACE_REMOTE_URL}"
else
  git remote add hf-space "${SPACE_REMOTE_URL}"
fi

echo "Pushing current branch to HF Space..."
git push hf-space HEAD:main

echo "Done."
echo "Space URL: https://huggingface.co/spaces/${SPACE_ID}"
echo "Runtime URL: https://${HF_USER}-${SPACE_NAME}.hf.space"
