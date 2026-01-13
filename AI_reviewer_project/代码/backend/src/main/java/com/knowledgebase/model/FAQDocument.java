package com.knowledgebase.model;

import lombok.Data;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.LastModifiedDate;
import org.springframework.data.jpa.domain.support.AuditingEntityListener;

import javax.persistence.*;
import java.util.Date;

/**
 * FAQ文档数据模型
 * 对应数据库中的faq_documents表
 */
@Data
@Entity
@Table(name = "faq_documents")
@EntityListeners(AuditingEntityListener.class)
public class FAQDocument {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "question", nullable = false, columnDefinition = "TEXT")
    private String question;

    @Column(name = "answer", nullable = false, columnDefinition = "TEXT")
    private String answer;

    @Column(name = "category", nullable = false)
    private String category;

    @Column(name = "keywords")
    private String keywords;

    @Column(name = "status", nullable = false)
    private String status;

    @Column(name = "vector_id")
    private String vectorId;

    @Column(name = "created_at", nullable = false, updatable = false)
    @CreatedDate
    @Temporal(TemporalType.TIMESTAMP)
    private Date createdAt;

    @Column(name = "updated_at", nullable = false)
    @LastModifiedDate
    @Temporal(TemporalType.TIMESTAMP)
    private Date updatedAt;

    @Column(name = "last_accessed")
    @Temporal(TemporalType.TIMESTAMP)
    private Date lastAccessed;

    @Column(name = "access_count")
    private Integer accessCount;

    @Column(name = "feedback_positive")
    private Integer feedbackPositive;

    @Column(name = "feedback_negative")
    private Integer feedbackNegative;

    @Column(name = "version")
    private Integer version;
}