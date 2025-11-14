"""飞书OAuth2.0集成"""
import httpx
from typing import Dict, Optional
from app.core.config import settings


class FeishuClient:
    """飞书API客户端"""
    
    def __init__(self):
        self.app_id = settings.FEISHU_APP_ID
        self.app_secret = settings.FEISHU_APP_SECRET
        self.base_url = "https://open.feishu.cn/open-apis"
        
    async def get_app_access_token(self) -> str:
        """
        获取应用访问令牌
        
        Returns:
            app_access_token
        """
        url = f"{self.base_url}/auth/v3/app_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取app_access_token失败: {data.get('msg')}")
            
            return data.get("app_access_token")
    
    async def get_user_access_token(self, code: str) -> str:
        """
        获取用户访问令牌
        
        Args:
            code: 飞书授权码
            
        Returns:
            user_access_token
        """
        app_access_token = await self.get_app_access_token()
        
        url = f"{self.base_url}/authen/v1/access_token"
        headers = {
            "Authorization": f"Bearer {app_access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "grant_type": "authorization_code",
            "code": code
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取user_access_token失败: {data.get('msg')}")
            
            return data.get("data", {}).get("access_token")
    
    async def get_user_info(self, user_access_token: str) -> Dict:
        """
        获取用户信息
        
        Args:
            user_access_token: 用户访问令牌
            
        Returns:
            用户信息字典
        """
        url = f"{self.base_url}/authen/v1/user_info"
        headers = {
            "Authorization": f"Bearer {user_access_token}",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取用户信息失败: {data.get('msg')}")
            
            return data.get("data", {})
    
    async def get_user_detail(self, user_id: str) -> Dict:
        """
        获取用户详细信息(包含部门信息)
        
        Args:
            user_id: 飞书用户ID
            
        Returns:
            用户详细信息
        """
        app_access_token = await self.get_app_access_token()
        
        url = f"{self.base_url}/contact/v3/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {app_access_token}",
        }
        params = {
            "user_id_type": "open_id"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            data = response.json()
            
            if data.get("code") != 0:
                raise Exception(f"获取用户详细信息失败: {data.get('msg')}")
            
            return data.get("data", {}).get("user", {})


# 全局飞书客户端实例
feishu_client = FeishuClient()

