# Java开发规范

## 1. 概述
本规范定义了Java项目开发的统一标准，包括代码风格、命名约定、架构原则等，旨在提高代码质量、可读性和可维护性。

## 2. 代码风格

### 2.1 缩进与格式
- 使用4个空格进行缩进，不使用制表符
- 每行代码长度不超过120个字符
- 左大括号(`{`)与声明语句同行，右大括号(`}`)单独成行
- 方法体、循环体、条件语句等都要使用大括号包裹，即使只有一行代码
- 代码块之间使用空行分隔，提高可读性

**示例：**
```java
public void exampleMethod() {
    if (condition) {
        // 代码块
        doSomething();
    }
}
```

### 2.2 注释规范
- 使用Javadoc注释为类、方法、常量提供文档
- Javadoc注释应包含：功能描述、参数说明、返回值说明、异常说明
- 使用单行注释(`//`)解释复杂代码逻辑
- 避免多余注释，代码本身应具有自解释性

**示例：**
```java
/**
 * 用户服务类，提供用户管理相关功能
 */
public class UserService {
    
    /**
     * 根据ID获取用户信息
     * @param userId 用户ID
     * @return 用户对象
     * @throws UserNotFoundException 当用户不存在时抛出
     */
    public User getUserById(Long userId) throws UserNotFoundException {
        // 查询数据库获取用户
        // ...
        return user;
    }
}
```

### 2.3 导入规范
- 避免使用通配符导入(`import java.util.*`)
- 导入语句按以下顺序分组，每组之间用空行分隔：
  1. Java标准库
  2. 第三方库
  3. 项目内部包
- 同一组内的导入按字母顺序排列

**示例：**
```java
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.example.domain.User;
import com.example.repository.UserRepository;
```

## 3. 命名约定

### 3.1 包名
- 使用小写字母，避免使用下划线
- 采用反转域名的命名方式：`com.company.project.module`
- 包名应反映模块结构和功能

**示例：**
```
com.example.knowledgebase.controller
com.example.knowledgebase.service
com.example.knowledgebase.repository
```

### 3.2 类名与接口名
- 使用大驼峰命名法(PascalCase)
- 类名应使用名词或名词短语
- 接口名应使用形容词或名词
- 抽象类名可以使用`Abstract`前缀
- 接口实现类名可以使用`Impl`后缀

**示例：**
```java
public class UserController {}
public interface UserService {}
public class UserServiceImpl implements UserService {}
public abstract class AbstractBaseService {}
```

### 3.3 方法名
- 使用小驼峰命名法(camelCase)
- 方法名应使用动词或动词短语
- 方法名应清晰表达其功能

**示例：**
```java
public User getUserById(Long id) {}
public void saveUser(User user) {}
public List<User> findAllUsers() {}
```

### 3.4 变量名
- 使用小驼峰命名法(camelCase)
- 变量名应清晰表达其含义，避免使用缩写
- 成员变量不使用前缀
- 常量使用全大写，单词间用下划线分隔

**示例：**
```java
private String userName;
private Long userId;
public static final int MAX_RETRY_COUNT = 3;
```

### 3.5 参数名
- 使用小驼峰命名法(camelCase)
- 参数名应清晰表达其含义
- 避免使用单字符参数名(除了循环变量i, j, k等)

**示例：**
```java
public void updateUser(Long userId, String newName) {}
```

## 4. 架构原则

### 4.1 分层架构
- 采用经典的三层架构：
  - 控制层(Controller)：处理HTTP请求和响应
  - 服务层(Service)：实现业务逻辑
  - 数据访问层(Repository/Dao)：与数据库交互
- 各层之间通过接口通信，避免直接依赖

### 4.2 依赖注入
- 优先使用构造函数注入，避免使用字段注入
- 依赖应面向接口，而非具体实现

**示例：**
```java
@Service
public class UserServiceImpl implements UserService {
    
    private final UserRepository userRepository;
    
    @Autowired
    public UserServiceImpl(UserRepository userRepository) {
        this.userRepository = userRepository;
    }
    
    // 方法实现
}
```

### 4.3 异常处理
- 使用自定义异常类表示业务异常
- 异常应包含有意义的错误消息
- 在控制层统一处理异常，返回标准格式的响应
- 避免使用异常控制业务流程

**示例：**
```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(UserNotFoundException.class)
    public ResponseEntity<ErrorResponse> handleUserNotFound(UserNotFoundException ex) {
        ErrorResponse error = new ErrorResponse("USER_NOT_FOUND", ex.getMessage());
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(error);
    }
    
    // 其他异常处理
}
```

### 4.4 事务管理
- 在服务层方法上声明事务注解
- 明确指定事务的传播行为和隔离级别
- 避免在同一方法中混用事务和非事务操作

**示例：**
```java
@Service
public class UserServiceImpl implements UserService {
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private OrderService orderService;
    
    @Transactional(propagation = Propagation.REQUIRED, isolation = Isolation.READ_COMMITTED)
    public void updateUserAndOrder(Long userId, Order order) {
        // 更新用户信息
        User user = userRepository.findById(userId).orElseThrow(UserNotFoundException::new);
        user.setLastUpdated(LocalDateTime.now());
        userRepository.save(user);
        
        // 创建订单
        orderService.createOrder(userId, order);
    }
}
```

## 5. 性能优化

### 5.1 集合使用
- 根据需求选择合适的集合类型
- 避免在循环中进行集合的增删操作
- 大集合遍历使用迭代器或增强for循环

### 5.2 数据库操作
- 使用批量操作处理大量数据
- 合理使用索引
- 避免N+1查询问题
- 使用分页查询处理大量结果

### 5.3 资源管理
- 使用try-with-resources自动关闭资源
- 避免频繁创建和销毁对象
- 使用连接池管理数据库连接

## 6. 安全规范

### 6.1 输入验证
- 对所有用户输入进行验证
- 使用Bean Validation(JSR 380)进行数据验证
- 避免SQL注入、XSS等安全漏洞

**示例：**
```java
public class UserDTO {
    
    @NotNull
    @Size(min = 3, max = 50)
    private String username;
    
    @NotNull
    @Email
    private String email;
    
    // getter和setter
}
```

### 6.2 密码安全
- 密码必须进行哈希处理后存储
- 使用安全的哈希算法(如BCrypt)
- 避免在日志中记录敏感信息

### 6.3 权限控制
- 实现基于角色的访问控制(RBAC)
- 对敏感操作进行权限验证
- 避免硬编码权限信息

## 7. 测试规范

### 7.1 测试覆盖
- 单元测试覆盖核心业务逻辑
- 集成测试验证模块间的交互
- 端到端测试验证完整业务流程

### 7.2 测试命名
- 测试类名使用`Test`后缀
- 测试方法名使用`should_行为_when_条件`格式

**示例：**
```java
public class UserServiceTest {
    
    @Test
    public void shouldReturnUser_whenUserIdExists() {
        // 测试代码
    }
}
```

### 7.3 测试框架
- 使用JUnit 5进行单元测试
- 使用Mockito进行Mock测试
- 使用Spring Boot Test进行集成测试

## 8. 版本控制

### 8.1 提交规范
- 提交信息应清晰描述修改内容
- 遵循"类型: 描述"的格式
- 类型包括：feat(新功能)、fix(修复bug)、docs(文档)、style(代码风格)、refactor(重构)、test(测试)、chore(构建/工具)

**示例：**
```
feat: 添加用户注册功能
fix: 修复登录验证失败的问题
docs: 更新API文档
```

### 8.2 分支管理
- 使用Git Flow或GitHub Flow进行分支管理
- 主分支：main/master
- 开发分支：develop
- 特性分支：feature/xxx
- 修复分支：hotfix/xxx

## 9. 代码审查

### 9.1 审查要点
- 代码风格是否符合规范
- 业务逻辑是否正确
- 是否存在潜在的性能问题
- 是否存在安全漏洞
- 代码可读性和可维护性

### 9.2 审查流程
- 开发完成后创建Pull Request
- 至少1名团队成员进行代码审查
- 审查通过后合并到目标分支
- 发现问题及时反馈并修复

## 10. 总结
本规范是Java项目开发的基础标准，所有开发人员都应严格遵守。规范将根据项目需求和技术发展不断更新和完善。