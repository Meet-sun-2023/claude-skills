# Spring Boot开发规范

## 1. 概述
本规范定义了Spring Boot项目开发的统一标准，包括项目结构、配置管理、依赖管理、REST API设计等，旨在提高开发效率和代码质量。

## 2. 项目结构

### 2.1 标准结构
采用Maven/Gradle标准项目结构，结合Spring Boot最佳实践：

```
src/
├── main/
│   ├── java/
│   │   └── com/
│   │       └── example/
│   │           └── project/
│   │               ├── Application.java        # 应用入口类
│   │               ├── config/                 # 配置类
│   │               ├── controller/             # 控制器层
│   │               ├── service/                # 服务层
│   │               │   └── impl/               # 服务实现类
│   │               ├── repository/             # 数据访问层
│   │               ├── domain/                 # 实体类
│   │               ├── dto/                    # 数据传输对象
│   │               ├── vo/                     # 视图对象
│   │               ├── exception/              # 异常类
│   │               ├── handler/                # 全局异常处理器
│   │               └── util/                   # 工具类
│   └── resources/
│       ├── application.yml                     # 主配置文件
│       ├── application-dev.yml                 # 开发环境配置
│       ├── application-prod.yml                # 生产环境配置
│       ├── static/                             # 静态资源
│       ├── templates/                          # 模板文件
│       └── META-INF/
│           └── additional-spring-configuration-metadata.json  # 配置元数据
└── test/
    ├── java/
    │   └── com/
    │       └── example/
    │           └── project/
    │               ├── controller/             # 控制器测试
    │               ├── service/                # 服务测试
    │               └── repository/             # 数据访问测试
    └── resources/
        └── application-test.yml                # 测试环境配置
```

### 2.2 包命名规范
- `config`: 存放配置类，如数据源配置、Redis配置等
- `controller`: 存放REST API控制器
- `service`: 存放业务逻辑接口
- `service.impl`: 存放业务逻辑实现类
- `repository`: 存放数据访问接口
- `domain`: 存放数据库实体类
- `dto`: 存放数据传输对象，用于层间数据传递
- `vo`: 存放视图对象，用于返回给前端的数据结构
- `exception`: 存放自定义异常类
- `handler`: 存放全局异常处理器
- `util`: 存放通用工具类

## 3. 配置管理

### 3.1 配置文件格式
- 使用YAML格式的配置文件(`application.yml`)，提高可读性
- 避免使用Properties格式的配置文件

### 3.2 多环境配置
- 使用`application-{profile}.yml`格式管理多环境配置
- 主要环境包括：
  - `dev`: 开发环境
  - `test`: 测试环境
  - `prod`: 生产环境

### 3.3 配置属性绑定
- 使用`@ConfigurationProperties`注解将配置绑定到Java类
- 配置类应放在`config`包下
- 使用`@Validated`和Bean Validation注解验证配置属性

**示例：**
```java
@Configuration
@ConfigurationProperties(prefix = "app.user")
@Validated
public class UserConfig {
    
    @NotBlank
    private String defaultRole;
    
    @Min(5)
    private int maxLoginAttempts;
    
    // getter和setter
}
```

```yaml
app:
  user:
    default-role: USER
    max-login-attempts: 5
```

### 3.4 敏感信息管理
- 避免在配置文件中硬编码敏感信息（如密码、API密钥等）
- 使用环境变量或配置中心管理敏感信息
- 在开发环境中可以使用`@Value`注解或Spring Cloud Config

## 4. 依赖管理

### 4.1 Spring Boot版本
- 使用最新稳定版本的Spring Boot
- 避免使用过时版本

### 4.2 依赖选择
- 优先使用Spring Boot Starter依赖
- 避免引入不必要的依赖
- 保持依赖版本的一致性

### 4.3 Maven配置
- 使用BOM（Bill of Materials）管理依赖版本
- 合理配置`dependencyManagement`和`dependencies`

**示例：**
```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>3.2.0</version>
    <relativePath/> <!-- lookup parent from repository -->
</parent>

<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-test</artifactId>
        <scope>test</scope>
    </dependency>
</dependencies>
```

## 5. REST API设计

### 5.1 API命名规范
- 使用RESTful风格设计API
- URL使用小写字母，单词间用连字符(`-`)分隔
- 使用名词表示资源，避免使用动词
- 使用复数形式表示资源集合

**示例：**
```
GET /api/users               # 获取用户列表
GET /api/users/{id}          # 获取单个用户
POST /api/users              # 创建用户
PUT /api/users/{id}          # 更新用户
DELETE /api/users/{id}       # 删除用户
```

### 5.2 HTTP方法使用
- `GET`: 获取资源
- `POST`: 创建资源
- `PUT`: 更新资源（全量更新）
- `PATCH`: 更新资源（部分更新）
- `DELETE`: 删除资源

### 5.3 响应格式
- 统一API响应格式
- 包含状态码、消息、数据等字段

**示例：**
```java
public class ApiResponse<T> {
    private int code;
    private String message;
    private T data;
    
    // 构造方法、getter和setter
    
    public static <T> ApiResponse<T> success(T data) {
        return new ApiResponse<>(200, "success", data);
    }
    
    public static <T> ApiResponse<T> error(int code, String message) {
        return new ApiResponse<>(code, message, null);
    }
}
```

### 5.4 状态码使用
- 使用标准HTTP状态码
- 2xx: 成功
  - 200 OK: 请求成功
  - 201 Created: 资源创建成功
  - 204 No Content: 请求成功但无返回内容
- 4xx: 客户端错误
  - 400 Bad Request: 请求参数错误
  - 401 Unauthorized: 未授权
  - 403 Forbidden: 禁止访问
  - 404 Not Found: 资源不存在
- 5xx: 服务器错误
  - 500 Internal Server Error: 服务器内部错误
  - 503 Service Unavailable: 服务不可用

### 5.5 分页与排序
- 使用统一的分页请求参数
- 使用`page`（页码）、`size`（每页大小）、`sort`（排序字段）
- 返回分页响应，包含总记录数、总页数、当前页数据等

**示例：**
```java
@GetMapping("/users")
public ApiResponse<Page<UserVO>> getUsers(
        @RequestParam(defaultValue = "0") int page,
        @RequestParam(defaultValue = "10") int size,
        @RequestParam(defaultValue = "id") String sort) {
    
    Pageable pageable = PageRequest.of(page, size, Sort.by(sort));
    Page<User> userPage = userService.findAll(pageable);
    Page<UserVO> userVOPage = userPage.map(userMapper::toVO);
    
    return ApiResponse.success(userVOPage);
}
```

## 6. 数据访问

### 6.1 ORM框架使用
- 使用Spring Data JPA进行数据访问
- 定义Repository接口继承`JpaRepository`

**示例：**
```java
public interface UserRepository extends JpaRepository<User, Long> {
    
    Optional<User> findByUsername(String username);
    
    List<User> findByEmailContaining(String email);
}
```

### 6.2 查询优化
- 使用`@Query`注解编写复杂查询
- 使用`@Modifying`注解标识更新/删除查询
- 合理使用`@EntityGraph`或`JOIN FETCH`解决N+1查询问题
- 避免在循环中执行数据库查询

### 6.3 事务管理
- 使用`@Transactional`注解管理事务
- 合理设置事务传播行为和隔离级别
- 事务注解应添加在服务层方法上

## 7. 日志管理

### 7.1 日志框架
- 使用SLF4J作为日志门面
- 使用Logback作为日志实现
- 避免使用`System.out.println()`

### 7.2 日志配置
- 在`application.yml`中配置日志级别
- 按环境配置不同的日志级别

**示例：**
```yaml
logging:
  level:
    root: INFO
    com.example.project: DEBUG
    org.springframework.security: WARN
  file:
    name: logs/application.log
```

### 7.3 日志使用
- 使用适当的日志级别：
  - `TRACE`: 最详细的日志，用于调试
  - `DEBUG`: 调试信息
  - `INFO`: 一般信息
  - `WARN`: 警告信息
  - `ERROR`: 错误信息
- 日志消息应包含必要的上下文信息
- 避免记录敏感信息

**示例：**
```java
private static final Logger logger = LoggerFactory.getLogger(UserService.class);

public User getUserById(Long userId) {
    logger.debug("Getting user by ID: {}", userId);
    User user = userRepository.findById(userId).orElse(null);
    if (user == null) {
        logger.warn("User not found for ID: {}", userId);
    }
    return user;
}
```

## 8. 安全管理

### 8.1 Spring Security
- 使用Spring Security进行安全管理
- 配置适当的认证和授权机制
- 实现基于角色的访问控制

### 8.2 API安全
- 使用JWT或OAuth 2.0进行身份认证
- 对敏感API进行权限验证
- 实现接口限流和防暴力破解

### 8.3 输入验证
- 使用Bean Validation进行请求参数验证
- 在控制器层添加`@Valid`或`@Validated`注解
- 自定义验证注解处理复杂验证逻辑

**示例：**
```java
@PostMapping("/users")
public ApiResponse<UserVO> createUser(@Valid @RequestBody UserDTO userDTO) {
    // 创建用户
    User user = userMapper.toEntity(userDTO);
    User savedUser = userService.save(user);
    return ApiResponse.success(userMapper.toVO(savedUser));
}
```

## 9. 测试

### 9.1 单元测试
- 使用JUnit 5进行单元测试
- 使用Mockito进行Mock测试
- 测试覆盖率应达到80%以上

**示例：**
```java
@ExtendWith(MockitoExtension.class)
public class UserServiceTest {
    
    @Mock
    private UserRepository userRepository;
    
    @InjectMocks
    private UserServiceImpl userService;
    
    @Test
    public void shouldReturnUser_whenUserIdExists() {
        // 准备数据
        Long userId = 1L;
        User user = new User();
        user.setId(userId);
        user.setUsername("testuser");
        
        // Mock行为
        when(userRepository.findById(userId)).thenReturn(Optional.of(user));
        
        // 执行测试
        User result = userService.getUserById(userId);
        
        // 验证结果
        assertNotNull(result);
        assertEquals(userId, result.getId());
        assertEquals("testuser", result.getUsername());
        verify(userRepository, times(1)).findById(userId);
    }
}
```

### 9.2 集成测试
- 使用Spring Boot Test进行集成测试
- 使用`@SpringBootTest`注解加载完整应用上下文
- 使用`@AutoConfigureTestDatabase`配置测试数据库

**示例：**
```java
@SpringBootTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.ANY)
public class UserRepositoryIntegrationTest {
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    public void shouldSaveAndFindUser() {
        // 准备数据
        User user = new User();
        user.setUsername("testuser");
        user.setEmail("test@example.com");
        
        // 保存用户
        User savedUser = userRepository.save(user);
        
        // 查询用户
        Optional<User> foundUser = userRepository.findById(savedUser.getId());
        
        // 验证结果
        assertTrue(foundUser.isPresent());
        assertEquals("testuser", foundUser.get().getUsername());
        assertEquals("test@example.com", foundUser.get().getEmail());
    }
}
```

## 10. 性能优化

### 10.1 缓存使用
- 合理使用缓存（如Redis）提高性能
- 使用`@Cacheable`、`@CachePut`、`@CacheEvict`注解
- 避免缓存雪崩、缓存穿透、缓存击穿等问题

### 10.2 异步处理
- 使用`@Async`注解处理异步任务
- 配置线程池参数
- 避免在异步方法中使用`RequestContextHolder`

### 10.3 数据库优化
- 合理设计数据库表结构
- 创建适当的索引
- 使用批量操作处理大量数据
- 避免全表扫描

## 11. 部署与监控

### 11.1 打包部署
- 使用Maven/Gradle打包成可执行JAR文件
- 配置`spring-boot-maven-plugin`

**示例：**
```xml
<build>
    <plugins>
        <plugin>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-maven-plugin</artifactId>
            <configuration>
                <mainClass>com.example.project.Application</mainClass>
            </configuration>
        </plugin>
    </plugins>
</build>
```

### 11.2 健康检查
- 使用Spring Boot Actuator进行健康检查
- 配置`management.endpoints.web.exposure.include`暴露端点
- 实现自定义健康检查指示器

### 11.3 监控
- 集成Prometheus和Grafana进行监控
- 配置指标收集
- 设置告警规则

## 12. 总结
本规范定义了Spring Boot项目开发的最佳实践，包括项目结构、配置管理、API设计、数据访问、安全管理等方面。遵循这些规范可以提高开发效率、代码质量和系统可维护性。