# Đặt tên file sao lưu với ngày tháng
BACKUP_FILE="/backup/db_backup_$(date +%F).sqlite3"

# Tạo thư mục sao lưu nếu chưa tồn tại
mkdir -p /backup

# Sao lưu cơ sở dữ liệu SQLite từ Docker container
docker cp 45473652fe0a:/app/db.sqlite3 $BACKUP_FILE

# Đặt tên repository và thông tin GitHub
REPO_NAME="BDUCM-Attendance-System"
REPO_URL="git@github.com:haulth/$REPO_NAME.git"

# Kiểm tra và clone kho lưu trữ nếu chưa tồn tại
if [ ! -d "$REPO_NAME" ]; then
  git clone -b backup $REPO_URL
fi

cd $REPO_NAME

# Tạo thư mục /backup trong repo nếu chưa tồn tại
mkdir -p backup

# Sao chép file sao lưu vào thư mục /backup của repo
cp $BACKUP_FILE ./backup/

# Commit và đẩy file sao lưu lên GitHub
git add ./backup/$(basename $BACKUP_FILE)
git commit -m "Auto backup on $(date)"
git push
