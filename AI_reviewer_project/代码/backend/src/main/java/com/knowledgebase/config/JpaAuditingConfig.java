package com.knowledgebase.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.data.jpa.repository.config.EnableJpaAuditing;

/**
 * JPA审计配置类
 * 启用Spring Data JPA的审计功能，用于自动填充创建时间和更新时间
 */
@Configuration
@EnableJpaAuditing
public class JpaAuditingConfig {
    // 该配置类用于启用JPA审计功能
    // 配合@CreatedDate和@LastModifiedDate注解使用
}