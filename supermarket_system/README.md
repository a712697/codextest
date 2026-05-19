# 生产级超市商品管理系统

这是按生产环境标准拆分的超市商品管理系统工程骨架，默认技术栈为 FastAPI、Vue 3、TypeScript、Element Plus、MySQL 8、SQLAlchemy、Alembic、Redis、JWT、RBAC、Docker Compose。

当前交付包含：

- 后端 FastAPI 项目骨架
- MySQL 8 建表 SQL
- SQLAlchemy 核心模型
- 统一响应格式与错误码
- JWT/密码哈希配置入口
- 商品、库存、入库、出库 API 模块骨架
- Vue 3 + Element Plus 前端骨架
- Docker Compose 部署文件
- 不依赖第三方库的核心业务验证层
- 库存入库/出库/流水/审计/导入校验测试

## 默认假设

- 单门店，后续可扩展多门店
- 单仓库
- 不允许负库存
- 入库、出库审核通过后才影响库存
- 删除默认逻辑删除
- 金额不用 float，使用 DECIMAL 或整数分
- 库存更新必须事务化，并考虑乐观锁/version
- 关键操作记录审计日志

## 目录结构

```text
supermarket_system/
  backend/
    app/
      api/v1/
      core/
      db/
      models/
      schemas/
    alembic/
    sql/001_init.sql
    requirements.txt
    Dockerfile
  frontend/
    src/
      api/
      router/
      views/
    package.json
    Dockerfile
  core/
    db.py
    services.py
    errors.py
  docker-compose.yml
```

## 本地核心测试

当前环境无法从 PyPI 安装 FastAPI/SQLAlchemy 依赖时，仍可以验证核心库存业务规则：

```bash
python3 -B -m unittest tests.test_supermarket_core -v
```

已覆盖：

- SKU 唯一
- 条码唯一但允许为空
- 价格不能为负
- 入库审核增加库存并生成流水
- 入库审核幂等
- 出库不能超过库存
- 出库审核扣减库存并生成流水
- 库存预警
- 有库存或单据历史时禁止删除商品
- Excel 导入风格的逐行校验错误返回

## Docker Compose 启动

先创建后端环境变量：

```bash
cp backend/.env.example backend/.env
```

修改 `backend/.env` 中的 `JWT_SECRET_KEY`、数据库密码和 Redis 配置。生产环境不要使用默认密码。

启动：

```bash
docker compose up --build
```

访问：

- 后端 OpenAPI: http://localhost:8000/docs
- 前端: http://localhost:5173

## 数据库初始化

Docker Compose 首次启动 MySQL 时会执行：

```text
backend/sql/001_init.sql
```

后续生产迭代应使用 Alembic migration 管理结构变更。

## API 统一响应

所有接口必须返回：

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "request_id": "uuid"
}
```

错误码：

| code | 含义 |
|---:|---|
| 0 | 成功 |
| 40000 | 参数错误 |
| 40100 | 未登录或 Token 无效 |
| 40300 | 无权限 |
| 40400 | 资源不存在 |
| 40900 | 数据冲突 |
| 42200 | 业务规则不满足 |
| 50000 | 系统错误 |

## 后续开发顺序

1. 完成 Auth 模块：用户表、密码哈希、JWT、Refresh Token。
2. 完成 RBAC：角色、权限、接口依赖、前端按钮权限。
3. 完成商品基础资料：分类、品牌、供应商、商品、条码、价格。
4. 完成库存服务：库存查询、库存预警。
5. 完成入库单：创建、明细、审核、流水、审计。
6. 完成出库单：创建、库存不足校验、审核扣减、流水、审计。
7. 完成 Excel 导入导出：逐行校验、错误行返回。
8. 完成前端页面与 API 对接。
9. 完成接口测试、权限测试、库存并发测试。
10. 完成生产部署配置、备份和监控说明。

## 测试账号

当前未硬编码测试账号。生产级实现应通过初始化脚本创建管理员，并要求首次登录修改密码。

## 生产注意事项

- 不要把数据库密码、Redis 密码、JWT 密钥写死在代码里。
- 生产环境关闭 debug。
- Redis 和 MySQL 不应暴露公网。
- 必须配置数据库备份。
- 必须保留审计日志。
- 不建议删除库存流水。
