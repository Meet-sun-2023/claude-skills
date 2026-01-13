package com.knowledgebase.repository;

import com.knowledgebase.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

/**
 * 用户数据访问接口
 * 提供对users表的CRUD操作
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * 根据用户名查询用户
     * @param username 用户名
     * @return 用户对象
     */
    User findByUsername(String username);

    /**
     * 根据邮箱查询用户
     * @param email 邮箱地址
     * @return 用户对象
     */
    User findByEmail(String email);

    /**
     * 根据角色查询用户列表
     * @param role 用户角色
     * @return 用户列表
     */
    java.util.List<User> findByRole(String role);
}