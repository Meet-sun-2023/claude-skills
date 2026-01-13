package com.knowledgebase.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * 向量生成工具类
 * 用于将文本转换为向量表示
 * 注意：这里使用的是模拟向量生成，实际项目中应使用真实的向量模型（如BERT、Word2Vec等）
 */
@Component
public class VectorUtils {

    @Value("${milvus.collection.dimension}")
    private Integer dimension;

    private Random random = new Random();

    /**
     * 将文本转换为向量表示
     * @param text 输入文本
     * @return 向量表示（浮点数列表）
     */
    public List<Float> generateVector(String text) {
        List<Float> vector = new ArrayList<>(dimension);
        
        // 基于文本的哈希值生成伪随机向量
        // 实际项目中应替换为真实的向量模型
        long seed = text.hashCode();
        Random localRandom = new Random(seed);
        
        for (int i = 0; i < dimension; i++) {
            // 生成-1到1之间的随机浮点数
            float value = (localRandom.nextFloat() - 0.5f) * 2.0f;
            vector.add(value);
        }
        
        return vector;
    }

    /**
     * 计算两个向量的余弦相似度
     * @param vector1 第一个向量
     * @param vector2 第二个向量
     * @return 相似度分数（-1到1之间）
     */
    public double calculateCosineSimilarity(List<Float> vector1, List<Float> vector2) {
        if (vector1.size() != vector2.size()) {
            throw new IllegalArgumentException("Vectors must have the same dimension");
        }

        double dotProduct = 0.0;
        double norm1 = 0.0;
        double norm2 = 0.0;

        for (int i = 0; i < vector1.size(); i++) {
            dotProduct += vector1.get(i) * vector2.get(i);
            norm1 += Math.pow(vector1.get(i), 2);
            norm2 += Math.pow(vector2.get(i), 2);
        }

        if (norm1 == 0 || norm2 == 0) {
            return 0.0;
        }

        return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
    }

    /**
     * 计算两个向量的欧氏距离
     * @param vector1 第一个向量
     * @param vector2 第二个向量
     * @return 欧氏距离
     */
    public double calculateEuclideanDistance(List<Float> vector1, List<Float> vector2) {
        if (vector1.size() != vector2.size()) {
            throw new IllegalArgumentException("Vectors must have the same dimension");
        }

        double sum = 0.0;
        for (int i = 0; i < vector1.size(); i++) {
            double diff = vector1.get(i) - vector2.get(i);
            sum += diff * diff;
        }

        return Math.sqrt(sum);
    }
}