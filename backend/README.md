# Backend User System (Flask)

本目录实现了“注册认证 + 个人资料管理 + 适当性评估”的后端基础版本，采用 Flask + Pydantic 的分层结构，便于后续替换数据库和第三方服务。

## 目录结构

```text
backend/
  app/
    api/
      deps.py
      error_handlers.py
      router.py
      routers/
        auth.py
        profile.py
        suitability.py
    core/
      enums.py
      errors.py
      security.py
    models/
      user.py
    repositories/
      token_repository.py
      user_repository.py
    schemas/
      auth.py
      common.py
      profile.py
      suitability.py
    services/
      auth_service.py
      profile_service.py
      suitability_service.py
      user_service.py
    main.py
```

## 已实现功能

1. 注册与认证
- 手机号注册（含验证码字段校验）
- 邮箱注册（含验证码字段校验）
- 第三方账号注册入口（微信/微博）
- 基础认证状态查询和更新（手机/邮箱验证状态）
- 实名认证提交流程（身份证信息 + 可选人脸识别标志）
- 专业认证提交流程（上传从业资格/学历等材料）

2. 投资者适当性评估
- 问卷获取
- 问卷提交与风险等级计算
- 评估结果查询

3. 个人资料管理
- 基本信息维护：昵称、头像、简介、经验标签
- 投资偏好维护：关注市场、风险偏好
- 成就信息结构：发帖数、精华帖、影响力、勋章
- 隐私设置：字段可见性控制
- 公开资料查询（支持匿名访问，按隐私规则脱敏）

## 暂时无法完成（已用 pass + TODO 预留）

以下点在代码中已明确使用 `pass` 并标注 `TODO`：

- 短信/邮箱验证码真实校验服务对接
- 微信/微博 OAuth OpenID 真实换取
- 实名 OCR + KYC 服务对接
- 人脸活体和身份比对服务对接
- 专业认证反欺诈和人工审核队列对接

## 运行方式

1. 安装依赖（项目根目录）：

```bash
pip install -e .
```

2. 启动服务（在 `backend` 目录）：

```bash
python -m app.main
```

3. 健康检查：
- `http://127.0.0.1:8000/healthz`

## 说明

- 当前仓储层为内存实现（`InMemory*Repository`），重启后数据会清空。
- 若要接入 MySQL/PostgreSQL，可仅替换 `repositories` 实现，`services` 与 `api` 层保持不变。
