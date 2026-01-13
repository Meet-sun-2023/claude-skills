# MySQL数据库设计与开发规范

## 一、数据库设计规范

### 1.1 命名规范
```
- 所有命名使用小写字母、数字和下划线
- 表名：业务模块_表含义（复数），如：user_profiles, order_items
- 字段名：使用蛇形命名法，如：created_at, is_deleted
- 主键：统一命名为 id (BIGINT UNSIGNED)
- 外键：关联表名_singular_id，如：user_id, organization_id
- 索引：idx_字段名[_字段名2]，如：idx_status_created
- 唯一索引：uk_字段名[_字段名2]
- 存储过程/函数：sp_/func_功能名
```

### 1.2 表设计规范
```sql
-- 每个表必须包含的字段
CREATE TABLE sample_table (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    created_by VARCHAR(64) COMMENT '创建人',
    updated_by VARCHAR(64) COMMENT '更新人',
    is_deleted TINYINT NOT NULL DEFAULT 0 COMMENT '软删除标记:0-正常,1-删除',
    version INT NOT NULL DEFAULT 0 COMMENT '乐观锁版本号',
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci 
  COMMENT='表注释必须清晰描述业务含义';

-- 字段设计原则
-- 1. 优先选择符合业务的最小数据类型
-- 2. 所有字段必须NOT NULL并设置默认值（除非业务强制要求）
-- 3. 金额相关使用DECIMAL(总位数,小数位)，如DECIMAL(15,2)
-- 4. 状态字段使用TINYINT并明确注释枚举值
-- 5. 文本字段根据实际长度选择：VARCHAR(n)或TEXT系列
```

### 1.3 索引设计规范
```sql
-- 索引创建原则
-- 1. 单表索引数不超过5个
-- 2. 联合索引字段数不超过5个
-- 3. 创建索引的字段区分度要高（一般>20%）
-- 4. 避免冗余索引

-- 联合索引最佳实践
-- 正确示例：WHERE a=? AND b=? ORDER BY c
CREATE INDEX idx_a_b_c ON table_name(a, b, c);

-- 需要避免的索引设计
-- ❌ 在低区分度字段建索引
CREATE INDEX idx_gender ON users(gender); -- gender只有2-3个值

-- ✅ 正确做法：与高区分度字段组合
CREATE INDEX idx_gender_city ON users(gender, city);
```

## 二、SQL开发规范

### 2.1 查询规范
```sql
-- ✅ 正确示例
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(o.id) AS order_count
FROM users u
JOIN orders o ON u.id = o.user_id
WHERE u.status = 1
    AND u.created_at >= '2024-01-01'
    AND u.is_deleted = 0
GROUP BY u.id
HAVING order_count > 5
ORDER BY u.created_at DESC
LIMIT 20 OFFSET 0;

-- ❌ 需要避免的写法
-- 1. SELECT * （明确列出所需字段）
-- 2. 函数操作索引字段：WHERE DATE(created_at) = '2024-01-01'
-- 3. 隐式类型转换：WHERE user_id = '123' （user_id是整数）
-- 4. OR连接不同字段：WHERE a=1 OR b=2 （可改用UNION）
```

### 2.2 事务规范
```sql
-- 事务使用原则
START TRANSACTION;

-- 1. 事务要短小精悍，尽快提交
-- 2. 避免在事务中进行远程调用或复杂计算
-- 3. 更新操作按相同顺序访问记录，避免死锁
-- 4. 控制单次操作数据量（分批处理）

UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- 添加适当的等待和重试机制处理死锁
COMMIT;

-- 明确设置事务隔离级别（根据业务需求）
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

## 三、性能与安全规范

### 3.1 性能优化条款
```sql
-- 1. 大数据量操作使用分页，避免深度翻页
-- ✅ 优化后的分页（基于有序唯一键）
SELECT * FROM orders 
WHERE id > 上一页最后ID 
  AND status = 1
ORDER BY id
LIMIT 20;

-- 2. 统计类查询使用汇总表
-- 创建定时任务更新的统计表
CREATE TABLE daily_user_stats (
    stat_date DATE NOT NULL,
    user_count INT NOT NULL,
    active_count INT NOT NULL,
    PRIMARY KEY (stat_date)
);

-- 3. 定期分析表并优化
ANALYZE TABLE table_name;
OPTIMIZE TABLE table_name; -- 注意锁表问题
```

### 3.2 安全规范
```sql
-- 1. 禁止拼接SQL，使用参数化查询
-- ❌ 危险
SET @sql = CONCAT('SELECT * FROM ', @table, ' WHERE id=', @id);
PREPARE stmt FROM @sql;

-- ✅ 安全
PREPARE stmt FROM 'SELECT * FROM users WHERE id=?';
SET @id = 123;
EXECUTE stmt USING @id;

-- 2. 最小权限原则
-- 创建只读账号
CREATE USER 'reader'@'%' IDENTIFIED BY 'strong_password';
GRANT SELECT ON db_name.* TO 'reader'@'%';

-- 3. 敏感数据加密存储
CREATE TABLE users (
    id BIGINT UNSIGNED,
    phone VARCHAR(20) COMMENT '需加密存储',
    id_card_hash CHAR(64) COMMENT '身份证号哈希值，用于去重验证'
);
```

## 四、DDL变更规范

### 4.1 变更流程
```
1. 预检查（开发环境）
   - EXPLAIN分析执行计划
   - 检查对现有业务的影响
   
2. 评审与审核
   - DDL语句需经DBA或技术负责人评审
   - 重大变更需提供回滚方案
   
3. 变更窗口执行
   - 选择低峰期执行
   - 使用在线DDL工具（pt-online-schema-change）
   
4. 验证与监控
   - 验证数据一致性
   - 监控性能指标变化
```

### 4.2 常用DDL示例
```sql
-- 添加字段（包含注释和默认值）
ALTER TABLE users 
ADD COLUMN last_login_ip VARCHAR(45) NOT NULL DEFAULT '' 
COMMENT '最后登录IP地址'
AFTER last_login_time;

-- 修改字段（注意数据兼容性）
ALTER TABLE users 
MODIFY COLUMN email VARCHAR(255) NOT NULL DEFAULT '' 
COMMENT '邮箱地址，唯一';

-- 添加索引（在线添加）
ALTER TABLE orders 
ADD INDEX idx_user_status (user_id, status), 
ALGORITHM=INPLACE, LOCK=NONE;
```

## 五、监控与维护

### 5.1 必须监控的指标
```sql
-- 慢查询监控（阈值：> 2秒）
SET GLOBAL slow_query_log = 1;
SET GLOBAL long_query_time = 2;

-- 检查锁等待
SHOW ENGINE INNODB STATUS;

-- 监控索引使用情况
SELECT 
    object_schema,
    object_name,
    index_name,
    count_star
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE count_star = 0 
  AND index_name IS NOT NULL
ORDER BY object_schema, object_name;
```

### 5.2 定期维护任务
```sql
-- 1. 每周检查表碎片率
SELECT 
    TABLE_SCHEMA,
    TABLE_NAME,
    DATA_FREE / (DATA_LENGTH + INDEX_LENGTH) AS frag_ratio
FROM information_schema.TABLES 
WHERE DATA_LENGTH > 1000000  -- 大于1MB的表
  AND DATA_FREE / (DATA_LENGTH + INDEX_LENGTH) > 0.2; -- 碎片率>20%

-- 2. 每月清理历史数据（根据业务保留策略）
DELETE FROM operation_logs 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 180 DAY)
LIMIT 10000; -- 分批删除
```

## 六、规范检查清单（Code Review要点）

### 6.1 设计审查
- [ ] 表名、字段名是否符合命名规范
- [ ] 是否包含必要的审计字段（created_at, updated_at等）
- [ ] 字符集是否为utf8mb4（支持emoji）
- [ ] 索引设计是否合理（数量、字段顺序）
- [ ] 是否有适当的表注释和字段注释

### 6.2 SQL审查
- [ ] 是否避免使用SELECT *
- [ ] WHERE条件是否使用索引
- [ ] 是否存在N+1查询问题
- [ ] 是否使用参数化查询防止注入
- [ ] 事务大小是否合理，是否及时提交

### 6.3 性能审查
- [ ] 单次查询是否可能返回过多数据
- [ ] 是否存在全表扫描的风险
- [ ] JOIN操作是否在关联字段上有索引
- [ ] 是否存在隐式类型转换
- [ ] 分页查询是否优化

### 6.4 变更审查
- [ ] DDL变更是否有回滚方案
- [ ] 字段修改是否考虑数据兼容性
- [ ] 是否在低峰期执行变更
- [ ] 是否有充分的测试验证

---

## 附录：常见反模式及修正

```sql
-- ❌ 反模式1：过度索引
CREATE TABLE orders (
    id BIGINT,
    user_id BIGINT,
    status TINYINT,
    created_at TIMESTAMP,
    INDEX idx1 (user_id),
    INDEX idx2 (status),
    INDEX idx3 (user_id, status), -- 与idx1部分冗余
    INDEX idx4 (created_at, status),
    INDEX idx5 (user_id, created_at)
);

-- ✅ 优化后：精简索引，考虑查询模式
CREATE TABLE orders (
    id BIGINT,
    user_id BIGINT,
    status TINYINT,
    created_at TIMESTAMP,
    PRIMARY KEY (id),
    INDEX idx_user_status (user_id, status), -- 覆盖user_id单查
    INDEX idx_status_created (status, created_at) -- 覆盖状态+时间查询
);
```