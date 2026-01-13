package com.knowledgebase.controller;

import com.knowledgebase.model.FAQDocument;
import com.knowledgebase.service.FAQDocumentService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * 文档管理控制器
 * 处理FAQ文档的增删改查和批量上传功能
 */
@RestController
@RequestMapping("/api/documents")
@Tag(name = "文档管理接口", description = "FAQ文档的增删改查和批量上传接口")
public class DocumentController {

    @Autowired
    private FAQDocumentService faqDocumentService;

    /**
     * 获取所有文档
     * @return 文档列表
     */
    @GetMapping
    @Operation(summary = "获取所有文档", description = "获取系统中所有的FAQ文档")
    public ResponseEntity<List<FAQDocument>> getAllDocuments() {
        List<FAQDocument> documents = faqDocumentService.getAllDocuments();
        return ResponseEntity.ok(documents);
    }

    /**
     * 根据ID获取文档
     * @param id 文档ID
     * @return 文档信息
     */
    @GetMapping("/{id}")
    @Operation(summary = "根据ID获取文档", description = "根据文档ID获取详细信息")
    public ResponseEntity<?> getDocumentById(@PathVariable Long id) {
        Optional<FAQDocument> document = faqDocumentService.getDocumentById(id);
        if (document.isPresent()) {
            return ResponseEntity.ok(document.get());
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body("文档不存在");
        }
    }

    /**
     * 创建新文档
     * @param document 文档信息
     * @return 创建的文档
     */
    @PostMapping
    @Operation(summary = "创建文档", description = "创建新的FAQ文档")
    public ResponseEntity<?> createDocument(@RequestBody FAQDocument document) {
        try {
            FAQDocument createdDocument = faqDocumentService.createDocument(document);
            return ResponseEntity.status(HttpStatus.CREATED).body(createdDocument);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("创建文档失败: " + e.getMessage());
        }
    }

    /**
     * 更新文档
     * @param id 文档ID
     * @param document 更新的文档信息
     * @return 更新后的文档
     */
    @PutMapping("/{id}")
    @Operation(summary = "更新文档", description = "更新现有FAQ文档的信息")
    public ResponseEntity<?> updateDocument(@PathVariable Long id, @RequestBody FAQDocument document) {
        FAQDocument updatedDocument = faqDocumentService.updateDocument(id, document);
        if (updatedDocument != null) {
            return ResponseEntity.ok(updatedDocument);
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body("文档不存在");
        }
    }

    /**
     * 删除文档
     * @param id 文档ID
     * @return 删除结果
     */
    @DeleteMapping("/{id}")
    @Operation(summary = "删除文档", description = "根据ID删除FAQ文档")
    public ResponseEntity<?> deleteDocument(@PathVariable Long id) {
        boolean deleted = faqDocumentService.deleteDocument(id);
        if (deleted) {
            return ResponseEntity.ok("文档删除成功");
        } else {
            return ResponseEntity.status(HttpStatus.NOT_FOUND)
                    .body("文档不存在");
        }
    }

    /**
     * 根据分类获取文档
     * @param category 分类名称
     * @return 文档列表
     */
    @GetMapping("/category/{category}")
    @Operation(summary = "按分类获取文档", description = "根据分类名称获取FAQ文档列表")
    public ResponseEntity<List<FAQDocument>> getDocumentsByCategory(@PathVariable String category) {
        List<FAQDocument> documents = faqDocumentService.getDocumentsByCategory(category);
        return ResponseEntity.ok(documents);
    }

    /**
     * 搜索文档
     * @param keyword 搜索关键词
     * @return 文档列表
     */
    @GetMapping("/search")
    @Operation(summary = "搜索文档", description = "根据关键词搜索FAQ文档")
    public ResponseEntity<List<FAQDocument>> searchDocuments(@RequestParam String keyword) {
        List<FAQDocument> documents = faqDocumentService.searchDocuments(keyword);
        return ResponseEntity.ok(documents);
    }

    /**
     * 获取所有分类
     * @return 分类列表
     */
    @GetMapping("/categories")
    @Operation(summary = "获取所有分类", description = "获取系统中所有的FAQ分类")
    public ResponseEntity<List<String>> getAllCategories() {
        List<String> categories = faqDocumentService.getAllCategories();
        return ResponseEntity.ok(categories);
    }

    /**
     * 批量上传文档
     * @param file 上传的文件
     * @return 上传结果
     */
    @PostMapping("/batch-upload")
    @Operation(summary = "批量上传文档", description = "通过文件批量上传FAQ文档")
    public ResponseEntity<?> batchUpload(@RequestParam("file") MultipartFile file) {
        // TODO: 实现批量上传功能
        // 目前仅返回成功消息，实际项目中需要解析文件内容并创建文档
        return ResponseEntity.ok("批量上传功能待实现");
    }
}