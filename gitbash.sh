#!/bin/bash

# 프로젝트 디렉토리로 이동
cd C:/Users/sw126/my_flask_app

# Git 리포지토리 초기화
git init

# 변경 사항 추가 및 커밋
git add .
git commit -m "Initial commit with working Celery and Redis configuration"

# 원격 리포지토리 추가 (이미 추가되어 있다면 무시)
git remote remove origin
git remote add origin https://github.com/sw1261/my_flask_app.git

# 원격 리포지토리에서 병합 가져오기
git pull origin main --rebase

# 변경 사항 푸시
git push -u origin main
