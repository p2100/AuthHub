#!/bin/bash
set -e

echo "🚀 Starting AuthHub..."
echo "DEBUG: Current User: $(whoami)"
echo "DEBUG: JWT_PRIVATE_KEY_PATH is '${JWT_PRIVATE_KEY_PATH}'"
echo "DEBUG: JWT_PUBLIC_KEY_PATH is '${JWT_PUBLIC_KEY_PATH}'"

# 1. Generate keys if they don't exist
# 获取私钥路径，优先使用环境变量，默认为 ./keys/private_key.pem
export JWT_PRIVATE_KEY_PATH="${JWT_PRIVATE_KEY_PATH:-./keys/private_key.pem}"
export JWT_PUBLIC_KEY_PATH="${JWT_PUBLIC_KEY_PATH:-./keys/public_key.pem}"

echo "🔍 Checking key at: $JWT_PRIVATE_KEY_PATH"

if [ ! -f "$JWT_PRIVATE_KEY_PATH" ]; then
    echo "🔑 Keys not found at $JWT_PRIVATE_KEY_PATH. Generating new RSA keys..."
    # 确保 python 脚本也能读到导出后的环境变量
    python scripts/generate_keys.py
else
    echo "✅ Keys found at $JWT_PRIVATE_KEY_PATH."
fi

# 2. Run migrations
echo "📦 Running database migrations..."
alembic upgrade head

# 3. Start application
echo "🔥 Starting Uvicorn server on $HOST:$PORT..."
exec uvicorn app.main:app --host $HOST --port $PORT
