package com.knowledgebase.service;

import com.knowledgebase.model.FAQDocument;
import com.knowledgebase.repository.FAQDocumentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.Date;
import java.util.List;
import java.util.Optional;

/**
 * FAQ文档业务逻辑服务层
 * 处理FAQ文档的CRUD和业务逻辑
 */
@Service
public class FAQDocumentService {

    @Autowired
    private FAQDocumentRepository faqDocumentRepository;

    @Autowired
    private RagService ragService;

    @Autowired
    private VectorUtils vectorUtils;

    /**
     * 获取所有FAQ文档
     * @return FAQ文档列表
     */
    public List<FAQDocument> getAllDocuments() {
        return faqDocumentRepository.findAll();
    }

    /**
     * 根据ID获取FAQ文档
     * @param id 文档ID
     * @return FAQ文档
     */
    public Optional<FAQDocument> getDocumentById(Long id) {
        Optional<FAQDocument> document = faqDocumentRepository.findById(id);
        // 更新文档访问信息
        document.ifPresent(doc -> {
            doc.setLastAccessed(new Date());
            doc.setAccessCount(doc.getAccessCount() != null ? doc.getAccessCount() + 1 : 1);
            faqDocumentRepository.save(doc);
        });
        return document;
    }

    /**
     * 创建新的FAQ文档
     * @param document FAQ文档对象
     * @return 创建的FAQ文档
     */
    public FAQDocument createDocument(FAQDocument document) {
        // 设置默认值
        if (document.getStatus() == null) {
            document.setStatus("active");
        }
        if (document.getAccessCount() == null) {
            document.setAccessCount(0);
        }
        if (document.getFeedbackPositive() == null) {
            document.setFeedbackPositive(0);
        }
        if (document.getFeedbackNegative() == null) {
            document.setFeedbackNegative(0);
        }
        if (document.getVersion() == null) {
            document.setVersion(1);
        }

        // 保存文档到数据库
        FAQDocument savedDocument = faqDocumentRepository.save(document);

        try {
            // 生成向量并存储到Milvus
            List<Float> vector = vectorUtils.generateVector(savedDocument.getQuestion() + " " + savedDocument.getAnswer());
            String vectorId = ragService.storeVector(savedDocument, vector);
            // 更新文档的向量ID
            savedDocument.setVectorId(vectorId);
            faqDocumentRepository.save(savedDocument);
        } catch (Exception e) {
            // 如果向量存储失败，记录日志但不影响文档创建
            System.err.println("Failed to store vector: " + e.getMessage());
        }

        return savedDocument;
    }

    /**
     * 更新FAQ文档
     * @param id 文档ID
     * @param document 更新的文档信息
     * @return 更新后的FAQ文档
     */
    public FAQDocument updateDocument(Long id, FAQDocument document) {
        Optional<FAQDocument> existingDocument = faqDocumentRepository.findById(id);
        if (!existingDocument.isPresent()) {
            return null;
        }

        FAQDocument docToUpdate = existingDocument.get();
        docToUpdate.setQuestion(document.getQuestion());
        docToUpdate.setAnswer(document.getAnswer());
        docToUpdate.setCategory(document.getCategory());
        docToUpdate.setKeywords(document.getKeywords());
        docToUpdate.setStatus(document.getStatus());
        docToUpdate.setVersion(docToUpdate.getVersion() + 1);

        // 保存更新后的文档
        FAQDocument updatedDocument = faqDocumentRepository.save(docToUpdate);

        try {
            // 删除旧向量
            ragService.deleteVectorByDocumentId(id);
            // 生成新向量并存储
            List<Float> vector = vectorUtils.generateVector(updatedDocument.getQuestion() + " " + updatedDocument.getAnswer());
            String vectorId = ragService.storeVector(updatedDocument, vector);
            updatedDocument.setVectorId(vectorId);
            faqDocumentRepository.save(updatedDocument);
        } catch (Exception e) {
            System.err.println("Failed to update vector: " + e.getMessage());
        }

        return updatedDocument;
    }

    /**
     * 删除FAQ文档
     * @param id 文档ID
     * @return 是否删除成功
     */
    public boolean deleteDocument(Long id) {
        Optional<FAQDocument> document = faqDocumentRepository.findById(id);
        if (document.isPresent()) {
            // 删除Milvus中的向量
            ragService.deleteVectorByDocumentId(id);
            // 删除数据库中的文档
            faqDocumentRepository.deleteById(id);
            return true;
        }
        return false;
    }

    /**
     * 根据分类获取FAQ文档
     * @param category 分类名称
     * @return FAQ文档列表
     */
    public List<FAQDocument> getDocumentsByCategory(String category) {
        return faqDocumentRepository.findByCategory(category);
    }

    /**
     * 搜索FAQ文档
     * @param keyword 搜索关键词
     * @return FAQ文档列表
     */
    public List<FAQDocument> searchDocuments(String keyword) {
        return faqDocumentRepository.searchByKeyword(keyword);
    }

    /**
     * 获取所有分类
     * @return 分类列表
     */
    public List<String> getAllCategories() {
        return faqDocumentRepository.findDistinctCategories();
    }

    /**
     * 更新文档的反馈统计
     * @param documentId 文档ID
     * @param isPositive 是否正面反馈
     * @return 是否更新成功
     */
    public boolean updateFeedback(Long documentId, boolean isPositive) {
        Optional<FAQDocument> document = faqDocumentRepository.findById(documentId);
        if (document.isPresent()) {
            FAQDocument doc = document.get();
            if (isPositive) {
                doc.setFeedbackPositive(doc.getFeedbackPositive() != null ? doc.getFeedbackPositive() + 1 : 1);
            } else {
                doc.setFeedbackNegative(doc.getFeedbackNegative() != null ? doc.getFeedbackNegative() + 1 : 1);
            }
            faqDocumentRepository.save(doc);
            return true;
        }
        return false;
    }
}