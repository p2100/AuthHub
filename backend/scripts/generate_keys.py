#!/usr/bin/env python3
"""生成RSA密钥对脚本"""

import os
import sys

# 添加父目录到path以便导入app模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.security import generate_rsa_keys


def main():
    """生成并保存RSA密钥对"""
    print("正在生成RSA密钥对...")

    # 生成密钥
    private_key, public_key = generate_rsa_keys(key_size=2048)

    # 创建keys目录
    keys_dir = os.path.dirname(settings.JWT_PRIVATE_KEY_PATH)
    if keys_dir and not os.path.exists(keys_dir):
        os.makedirs(keys_dir)
        print(f"已创建目录: {keys_dir}")

    # 保存私钥
    with open(settings.JWT_PRIVATE_KEY_PATH, "w") as f:
        f.write(private_key)
    print(f"私钥已保存到: {settings.JWT_PRIVATE_KEY_PATH}")

    # 保存公钥
    with open(settings.JWT_PUBLIC_KEY_PATH, "w") as f:
        f.write(public_key)
    print(f"公钥已保存到: {settings.JWT_PUBLIC_KEY_PATH}")

    # 设置文件权限(仅所有者可读)
    os.chmod(settings.JWT_PRIVATE_KEY_PATH, 0o600)
    os.chmod(settings.JWT_PUBLIC_KEY_PATH, 0o644)

    print("\n✅ RSA密钥对生成成功!")
    print("\n⚠️  请妥善保管私钥文件,不要提交到版本控制系统!")


if __name__ == "__main__":
    main()
