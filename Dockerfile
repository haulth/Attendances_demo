# Sử dụng Ubuntu 22.04 làm image nền
FROM ubuntu:22.04

# Thiết lập biến môi trường
ENV DEBIAN_FRONTEND="noninteractive"

# Cập nhật hệ thống và cài đặt các gói cần thiết
RUN set -ex; \
    apt-get clean && apt-get update && apt-get upgrade -y && \
    apt-get install -y \
    poppler-utils \
    python3-pip \
    python3-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-setuptools \
    aria2 \
    libglib2.0-0 \
    wget \
    libgl1-mesa-glx && \
    rm -rf /var/lib/apt/lists/*  # Xóa cache apt để giảm kích thước image

# Sao chép toàn bộ mã nguồn vào container
COPY . /app

# Chuyển đến thư mục ứng dụng
WORKDIR /app

# Cài đặt các thư viện cần thiết từ file requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Lệnh mặc định để khởi động ứng dụng bằng gunicorn
CMD ["gunicorn", "--timeout", "600", "--threads", "3", "--bind", "0.0.0.0:80", "college_management_system.wsgi:application"]
