package com.knowledgebase.repository;

import com.knowledgebase.model.QueryLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.Date;
import java.util.List;

/**
 * 查询日志数据访问接口
 * 提供对query_logs表的CRUD操作
 */
@Repository
public interface QueryLogRepository extends JpaRepository<QueryLog, Long> {

    /**
     * 根据用户ID查询查询日志
     * @param userId 用户ID
     * @return 查询日志列表
     */
    List<QueryLog> findByUserId(Long userId);

    /**
     * 根据文档ID查询查询日志
     * @param documentId 文档ID
     * @return 查询日志列表
     */
    List<QueryLog> findByDocumentId(Long documentId);

    /**
     * 查询指定时间范围内的查询日志
     * @param startDate 开始时间
     * @param endDate 结束时间
     * @return 查询日志列表
     */
    List<QueryLog> findByCreatedAtBetween(Date startDate, Date endDate);

    /**
     * 查询有反馈的查询日志
     * @return 查询日志列表
     */
    List<QueryLog> findByFeedbackIsNotNull();

    /**
     * 查询特定反馈类型的查询日志
     * @param feedback 反馈类型 (1: 正面, -1: 负面)
     * @return 查询日志列表
     */
    List<QueryLog> findByFeedback(Integer feedback);

    /**
     * 根据会话ID查询查询日志
     * @param sessionId 会话ID
     * @return 查询日志列表
     */
    List<QueryLog> findBySessionId(String sessionId);

    /**
     * 获取统计数据：按天分组的查询次数
     * @return 统计结果列表
     */
    @Query("SELECT DATE(q.createdAt) as date, COUNT(q.id) as count FROM QueryLog q GROUP BY DATE(q.createdAt) ORDER BY date DESC")
    List<Object[]> getDailyQueryCount();
}