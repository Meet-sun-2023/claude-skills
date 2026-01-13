package com.knowledgebase.controller;

import com.knowledgebase.model.FAQDocument;
import com.knowledgebase.model.QueryLog;
import com.knowledgebase.service.FAQDocumentService;
import com.knowledgebase.service.QueryLogService;
import com.knowledgebase.service.RagService;
import com.knowledgebase.service.VectorUtils;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * 查询控制器
 * 处理FAQ查询和反馈请求
 */
@RestController
@RequestMapping("/api/query")
@Tag(name = "查询接口", description = "FAQ查询和反馈相关接口")
public class QueryController {

    @Autowired
    private FAQDocumentService faqDocumentService;

    @Autowired
    private QueryLogService queryLogService;

    @Autowired
    private RagService ragService;

    @Autowired
    private VectorUtils vectorUtils;

    /**
     * 查询FAQ
     * @param query 查询参数
     * @return 查询结果
     */
    @PostMapping
    @Operation(summary = "查询FAQ", description = "根据用户查询内容返回最相关的FAQ回答")
    public ResponseEntity<?> queryFAQ(@RequestBody Map<String, Object> query) {
        String queryText = (String) query.get("query");
        if (queryText == null || queryText.isEmpty()) {
            return ResponseEntity.badRequest().body("查询内容不能为空");
        }

        try {
            // 生成查询向量
            List<Float> queryVector = vectorUtils.generateVector(queryText);
            
            // 在Milvus中搜索最相似的文档
            List<Long> documentIds = ragService.searchSimilarDocuments(queryVector, 3);
            
            // 获取最相关的文档
            Optional<FAQDocument> bestDocument = Optional.empty();
            if (!documentIds.isEmpty()) {
                bestDocument = faqDocumentService.getDocumentById(documentIds.get(0));
            }

            // 创建查询日志
            QueryLog queryLog = new QueryLog();
            queryLog.setQueryText(queryText);
            if (bestDocument.isPresent()) {
                queryLog.setDocumentId(bestDocument.get().getId());
                queryLog.setResponse(bestDocument.get().getAnswer());
            }
            queryLog.setSessionId((String) query.get("session_id"));
            queryLog.setIpAddress((String) query.get("ip_address"));
            queryLog.setUserAgent((String) query.get("user_agent"));
            QueryLog savedLog = queryLogService.createQueryLog(queryLog);

            // 构建响应
            Map<String, Object> response = new HashMap<>();
            if (bestDocument.isPresent()) {
                FAQDocument doc = bestDocument.get();
                response.put("success", true);
                response.put("id", doc.getId());
                response.put("question", doc.getQuestion());
                response.put("answer", doc.getAnswer());
                response.put("category", doc.getCategory());
                response.put("log_id", savedLog.getId());
            } else {
                response.put("success", false);
                response.put("message", "未找到相关的FAQ");
                response.put("log_id", savedLog.getId());
            }

            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("查询失败: " + e.getMessage());
        }
    }

    /**
     * 提交反馈
     * @param feedbackRequest 反馈请求参数
     * @return 反馈结果
     */
    @PostMapping("/feedback")
    @Operation(summary = "提交反馈", description = "对查询结果提交正面或负面反馈")
    public ResponseEntity<?> submitFeedback(@RequestBody Map<String, Object> feedbackRequest) {
        Long logId = Long.parseLong(feedbackRequest.get("log_id").toString());
        Integer feedback = (Integer) feedbackRequest.get("feedback");
        String feedbackText = (String) feedbackRequest.get("feedback_text");

        boolean success = queryLogService.submitFeedback(logId, feedback, feedbackText);
        if (success) {
            return ResponseEntity.ok(Map.of("success", true, "message", "反馈提交成功"));
        } else {
            return ResponseEntity.badRequest().body("反馈提交失败，日志不存在");
        }
    }
}