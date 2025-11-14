/**
 * 中间件
 */

// Express中间件示例
export function createExpressMiddleware(client: any) {
  return async (req: any, res: any, next: any) => {
    const authHeader = req.headers.authorization || '';
    
    if (!authHeader.startsWith('Bearer ')) {
      return res.status(401).json({ error: '缺少认证Token' });
    }

    const token = authHeader.replace('Bearer ', '');

    try {
      const user = await client.verifyToken(token);
      req.user = user;
      next();
    } catch (error) {
      return res.status(401).json({ error: '认证失败' });
    }
  };
}

