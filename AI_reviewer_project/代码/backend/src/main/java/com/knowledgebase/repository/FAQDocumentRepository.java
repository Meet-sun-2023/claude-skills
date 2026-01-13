package com.knowledgebase.repository;

import com.knowledgebase.model.FAQDocument;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * FAQ文档数据访问接口
 * 提供对faq_documents表的CRUD操作
 */
@Repository
public interface FAQDocumentRepository extends JpaRepository<FAQDocument, Long> {

    /**
     * 根据分类查询FAQ文档
     * @param category 分类名称
     * @return FAQ文档列表
     */
    List<FAQDocument> findByCategory(String category);

    /**
     * 根据状态查询FAQ文档
     * @param status 文档状态
     * @return FAQ文档列表
     */
    List<FAQDocument> findByStatus(String status);

    /**
     * 根据向量ID查询FAQ文档
     * @param vectorId 向量ID
     * @return FAQ文档
     */
    FAQDocument findByVectorId(String vectorId);

    /**
     * 搜索包含关键词的FAQ文档
     * @param keyword 搜索关键词
     * @return FAQ文档列表
     */
    @Query("SELECT f FROM FAQDocument f WHERE f.question LIKE %?1% OR f.answer LIKE %?1% OR f.keywords LIKE %?1%")
    List<FAQDocument> searchByKeyword(String keyword);

    /**
     * 获取所有分类
     * @return 分类列表
     */
    @Query("SELECT DISTINCT f.category FROM FAQDocument f")
    List<String> findDistinctCategories();
}