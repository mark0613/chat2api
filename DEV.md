# DEV

## Admin
## Create Admin
```bash
python manage.py createadmin --name "Admin Name" --email admin@example.com --password password123
```


## DB
### 變更資料庫引擎
專案預設使用 SQLite 作為資料庫。如果需要改用其他資料庫，請修改以下檔案 `.env` 中的 `DATABASE_URL` 變數

### 初始化所有資料和表格
初始化資料庫並創建所有表格：
```bash
python manage.py initdb
```


## DB Migration
### Init
```bash
python manage.py migration init
```

### Generate Migration
```bash
# 使用自動生成的消息
python manage.py migration generate

# 使用自定義消息
python manage.py migration generate --message "Add user table"
```

這會在 `migrations/versions/` 目錄下生成一個新的遷移腳本。

### Migrate
```bash
# 升級到最新版本
python manage.py migration upgrade

# 升級到特定版本
python manage.py migration upgrade --revision abc123
```

### Rollback
```bash
# 回滾一個版本
python manage.py migration downgrade

# 回滾到特定版本
python manage.py migration downgrade --revision abc123
```

### History
```bash
python manage.py migration history
```
