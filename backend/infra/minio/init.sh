#!/bin/sh
set -eu

mc alias set carveo "$MINIO_ENDPOINT" "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD"
mc mb --ignore-existing "carveo/$CARVEO_OBJECT_STORAGE_BUCKET"
