#!/usr/bin/env bash
# Uploads Playwright-recorded videos to a SharePoint document library via
# Microsoft Graph, using client-credentials auth (app registration / service
# principal — no interactive user involved, suitable for a pipeline).
#
# Usage: publish-to-sharepoint.sh <video-dir> <branch> <build-number>
#
# Required env vars: SP_TENANT_ID, SP_CLIENT_ID, SP_CLIENT_SECRET,
# SP_SITE_ID, SP_DRIVE_ID (site/drive IDs come from Graph's
# /sites/{hostname}:/{site-path} and /sites/{site-id}/drives lookups).
#
# NOTE: this uses a direct PUT, which the Graph API only accepts for files
# under 4MB. Longer recordings need the resumable upload-session API
# (POST .../createUploadSession, then PUT in chunks) — swap that in before
# using this against real, non-trivial-length test videos.

set -euo pipefail

VIDEO_DIR="${1:?Usage: publish-to-sharepoint.sh <video-dir> <branch> <build-number>}"
BRANCH="${2:-unknown-branch}"
BUILD_NUMBER="${3:-unknown-build}"

: "${SP_TENANT_ID:?SP_TENANT_ID is required}"
: "${SP_CLIENT_ID:?SP_CLIENT_ID is required}"
: "${SP_CLIENT_SECRET:?SP_CLIENT_SECRET is required}"
: "${SP_SITE_ID:?SP_SITE_ID is required}"
: "${SP_DRIVE_ID:?SP_DRIVE_ID is required}"

echo "Requesting Graph API token..."
TOKEN=$(curl -sS -X POST \
  "https://login.microsoftonline.com/${SP_TENANT_ID}/oauth2/v2.0/token" \
  -d "client_id=${SP_CLIENT_ID}" \
  -d "client_secret=${SP_CLIENT_SECRET}" \
  -d "scope=https://graph.microsoft.com/.default" \
  -d "grant_type=client_credentials" \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

if [ -z "$TOKEN" ] || [ "$TOKEN" = "None" ]; then
  echo "Failed to acquire Graph API token" >&2
  exit 1
fi

# Staging path — a human reviews/promotes into the advisor-facing library
# rather than this script publishing directly to it. See pitch notes on
# why raw test recordings shouldn't go straight to end users.
TARGET_FOLDER="qa-staging/${BRANCH}/build-${BUILD_NUMBER}"

shopt -s nullglob
videos=("$VIDEO_DIR"/**/*.webm)
shopt -u nullglob

if [ ${#videos[@]} -eq 0 ]; then
  echo "No .webm recordings found under $VIDEO_DIR — nothing to upload."
  exit 0
fi

for file in "${videos[@]}"; do
  filename=$(basename "$file")
  echo "Uploading ${filename} to ${TARGET_FOLDER}..."
  curl -sS -f -X PUT \
    "https://graph.microsoft.com/v1.0/sites/${SP_SITE_ID}/drives/${SP_DRIVE_ID}/root:/${TARGET_FOLDER}/${filename}:/content" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: video/webm" \
    --data-binary "@${file}"
  echo "Uploaded ${filename}"
done

echo "Upload complete: ${#videos[@]} file(s) pushed to ${TARGET_FOLDER}."
