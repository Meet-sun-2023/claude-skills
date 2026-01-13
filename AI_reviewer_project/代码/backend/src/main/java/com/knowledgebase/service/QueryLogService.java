package com.knowledgebase.service;

import com.knowledgebase.model.QueryLog;
import com.knowledgebase.repository.QueryLogRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;

/**
 * 查询日志业务逻辑服务层
 * 处理查询日志的CRUD和业务逻辑
 */
@Service
public class QueryLogService {

    @Autowired
    private QueryLogRepository queryLogRepository;

    @Autowired
    private FAQDocumentService faqDocumentService;

    /**
     * 创建查询日志
     * @param queryLog 查询日志对象
     * @return 创建的查询日志
     */
    public QueryLog createQueryLog(QueryLog queryLog) {
        return queryLogRepository.save(queryLog);
    }

    /**
     * 根据ID获取查询日志
     * @param id 查询日志ID
     * @return 查询日志
     */
    public QueryLog getQueryLogById(Long id) {
        return queryLogRepository.findById(id).orElse(null);
    }

    /**
     * 获取所有查询日志
     * @return 查询日志列表
     */
    public List<QueryLog> getAllQueryLogs() {
        return queryLogRepository.findAll();
    }

    /**
     * 根据用户ID获取查询日志
     * @param userId 用户ID
     * @return 查询日志列表
     */
    public List<QueryLog> getQueryLogsByUserId(Long userId) {
        return queryLogRepository.findByUserId(userId);
    }

    /**
     * 根据文档ID获取查询日志
     * @param documentId 文档ID
     * @return 查询日志列表
     */
    public List<QueryLog> getQueryLogsByDocumentId(Long documentId) {
        return queryLogRepository.findByDocumentId(documentId);
    }

    /**
     * 提交查询反馈
     * @param logId 查询日志ID
     * @param feedback 反馈类型 (1: 正面, -1: 负面)
     * @param feedbackText 反馈文本
     * @return 是否提交成功
     */
    public boolean submitFeedback(Long logId, Integer feedback, String feedbackText) {
        QueryLog queryLog = queryLogRepository.findById(logId).orElse(null);
        if (queryLog == null) {
            return false;
        }

        // 更新查询日志的反馈信息
        queryLog.setFeedback(feedback);
        queryLog.setFeedbackText(feedbackText);
        queryLogRepository.save(queryLog);

        // 更新文档的反馈统计
        if (queryLog.getDocumentId() != null) {
            boolean isPositive = feedback == 1;
            faqDocumentService.updateFeedback(queryLog.getDocumentId(), isPositive);
        }

        return true;
    }

    /**
     * 获取指定时间范围内的查询日志
     * @param startDate 开始时间
     * @param endDate 结束时间
     * @return 查询日志列表
     */
    public List<QueryLog> getQueryLogsByDateRange(Date startDate, Date endDate) {
        return queryLogRepository.findByCreatedAtBetween(startDate, endDate);
    }

    /**
     * 获取有反馈的查询日志
     * @return 查询日志列表
     */
    public List<QueryLog> getQueryLogsWithFeedback() {
        return queryLogRepository.findByFeedbackIsNotNull();
    }

    /**
     * 获取每日查询统计
     * @return 统计结果列表
     */
    public List<Object[]> getDailyQueryCount() {
        return queryLogRepository.getDailyQueryCount();
    }
}