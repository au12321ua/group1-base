# Auth JWT 配置指南

Auth Service **在内部完成 JWT 签发与验签**（`/internal/verify`）。外部/Gateway **不需要**也**不提供**公钥端点。

## 算法开关

通过 `JWT_SUPPORT_*` 声明**验签**时接受哪些算法；通过 `JWT_SIGNING_ALGORITHM` 声明**新签发** Token 使用哪种算法。两种算法的密钥材料可同时配置。

| 变量 | 默认 | 说明 |
|------|------|------|
| `JWT_SUPPORT_HS256` | `true` | 是否接受 HS256 Token |
| `JWT_SUPPORT_RS256` | `false` | 是否接受 RS256 Token |
| `JWT_SIGNING_ALGORITHM` | `HS256` | 新 Token 签发算法（须在 SUPPORT 列表中） |

**典型场景**

- 本地原型：`SUPPORT_HS256=true`，`SIGNING=HS256`
- 生产 RS256：`SUPPORT_RS256=true`，`SIGNING=RS256`，配置 RSA PEM
- 迁移期：两者均为 `true`，先 `SIGNING=HS256` 再切 `RS256`；旧 HS256 Token 在过期前仍可验签

## HS256

```env
JWT_SUPPORT_HS256=true
JWT_SUPPORT_RS256=false
JWT_SIGNING_ALGORITHM=HS256
TOKEN_SECRET_KEY=<至少 32 字符随机串>
JWT_HS256_KEY_ID=auth-hs256-key-1
```

## RS256

```bash
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
```

```env
JWT_SUPPORT_HS256=false
JWT_SUPPORT_RS256=true
JWT_SIGNING_ALGORITHM=RS256
JWT_RSA_PRIVATE_KEY_PEM=-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----
JWT_RSA_PUBLIC_KEY_PEM=-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----
JWT_RSA_KEY_ID=auth-rs256-key-1
```

## 换密钥

更换 `TOKEN_SECRET_KEY` 或 RSA PEM 后**重启 Auth Service**。不做在线轮换；已签发 Token 在 `exp` 前仍按旧密钥验签（迁移期可 temporarily 双开 SUPPORT）。

## Token 数据库

`tokens.token_hash` 存 JWT 的 SHA-256 摘要，不存明文。与签发算法无关。

设计背景见 [04-security-architecture.md](design/v2/04-security-architecture.md)。
