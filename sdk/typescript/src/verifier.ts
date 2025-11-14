/**
 * Token验证器
 */

import * as jose from 'jose';
import type { TokenPayload } from './types';
import {
  TokenExpiredException,
  TokenRevokedException,
  InvalidTokenException,
} from './exceptions';

export class TokenVerifier {
  private publicKey: string = '';

  setPublicKey(publicKeyPem: string) {
    this.publicKey = publicKeyPem;
  }

  async verify(token: string): Promise<TokenPayload> {
    if (!this.publicKey) {
      throw new InvalidTokenException('公钥未设置');
    }

    try {
      const publicKey = await jose.importSPKI(this.publicKey, 'RS256');
      const { payload } = await jose.jwtVerify(token, publicKey);

      // 注意: 实际应用中需要检查黑名单(查询Redis)
      // 这里简化处理

      return payload as unknown as TokenPayload;
    } catch (error) {
      if (error instanceof jose.errors.JWTExpired) {
        throw new TokenExpiredException();
      }
      throw new InvalidTokenException(`Token验证失败: ${error}`);
    }
  }
}

