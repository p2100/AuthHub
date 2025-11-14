/**
 * 异常类
 */

export class TokenException extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'TokenException';
  }
}

export class TokenExpiredException extends TokenException {
  constructor(message = 'Token已过期') {
    super(message);
    this.name = 'TokenExpiredException';
  }
}

export class TokenRevokedException extends TokenException {
  constructor(message = 'Token已撤销') {
    super(message);
    this.name = 'TokenRevokedException';
  }
}

export class InvalidTokenException extends TokenException {
  constructor(message = 'Token无效') {
    super(message);
    this.name = 'InvalidTokenException';
  }
}

export class PermissionDeniedException extends Error {
  constructor(message = '权限不足') {
    super(message);
    this.name = 'PermissionDeniedException';
  }
}

