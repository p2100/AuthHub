#!/bin/bash
set -e

echo "🚀 Starting AuthHub..."

# 1. Generate keys if they don't exist
# 检查私钥是否存在，不存在则生成
if [ ! -f "./keys/private_key.pem" ]; then
    echo "🔑 Keys not found. Generating new RSA keys..."
    python scripts/generate_keys.py
else
    echo "✅ Keys found."
fi

# 2. Run migrations
echo "📦 Running database migrations..."
alembic upgrade head

# 3. Start application
echo "🔥 Starting Uvicorn server on $HOST:$PORT..."
exec uvicorn app.main:app --host $HOST --port $PORT
