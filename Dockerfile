# Python 3.9 slim 이미지를 사용하여 기본 이미지 설정
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 설치를 위한 requirements.txt 복사
COPY requirements.txt .

# 종속성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY . .

# 포트 8000을 노출
EXPOSE 8000