package com.knowledgebase.service;

import com.knowledgebase.model.FAQDocument;
import io.milvus.client.MilvusServiceClient;
import io.milvus.common.clientenum.ConsistencyLevelEnum;
import io.milvus.grpc.*;
import io.milvus.param.*;
import io.milvus.param.collection.*;
import io.milvus.param.dml.*;
import io.milvus.param.index.*;
import io.milvus.param.partition.*;
import io.milvus.param.query.QueryParam;
import io.milvus.param.query.SearchParam;
import io.milvus.response.SearchResultsWrapper;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import javax.annotation.PostConstruct;
import java.util.*;

/**
 * RAG服务类
 * 实现与Milvus向量数据库的交互，包括向量存储和检索
 */
@Service
public class RagService {

    @Value("${milvus.host}")
    private String milvusHost;

    @Value("${milvus.port}")
    private Integer milvusPort;

    @Value("${milvus.collection.name}")
    private String collectionName;

    @Value("${milvus.collection.dimension}")
    private Integer dimension;

    @Value("${milvus.collection.index-type}")
    private String indexType;

    private MilvusServiceClient milvusClient;

    /**
     * 初始化Milvus客户端并创建集合
     */
    @PostConstruct
    public void init() {
        // 建立Milvus连接
        ConnectParam connectParam = ConnectParam.newBuilder()
                .withHost(milvusHost)
                .withPort(milvusPort)
                .build();

        milvusClient = new MilvusServiceClient(connectParam);

        // 检查集合是否存在
        HasCollectionParam hasCollectionParam = HasCollectionParam.newBuilder()
                .withCollectionName(collectionName)
                .build();

        R<RpcStatus> hasCollectionResponse = milvusClient.hasCollection(hasCollectionParam);
        boolean collectionExists = hasCollectionResponse.getData().hasCollection();

        if (!collectionExists) {
            // 创建集合
            CreateCollectionParam createCollectionParam = CreateCollectionParam.newBuilder()
                    .withCollectionName(collectionName)
                    .withDescription("FAQ向量集合")
                    .withShardsNum(2)
                    .addFieldType(FieldType.newBuilder()
                            .withName("id")
                            .withDataType(DataType.Int64)
                            .withPrimaryKey(true)
                            .withAutoID(true)
                            .build())
                    .addFieldType(FieldType.newBuilder()
                            .withName("document_id")
                            .withDataType(DataType.Int64)
                            .build())
                    .addFieldType(FieldType.newBuilder()
                            .withName("vector")
                            .withDataType(DataType.FloatVector)
                            .withDimension(dimension)
                            .build())
                    .build();

            milvusClient.createCollection(createCollectionParam);

            // 创建索引
            CreateIndexParam createIndexParam = CreateIndexParam.newBuilder()
                    .withCollectionName(collectionName)
                    .withFieldName("vector")
                    .withIndexType(IndexType.HNSW)
                    .withMetricType(MetricType.L2)
                    .withExtraParam("{\"M\": 16, \"efConstruction\": 512}")
                    .build();

            milvusClient.createIndex(createIndexParam);

            // 加载集合
            LoadCollectionParam loadCollectionParam = LoadCollectionParam.newBuilder()
                    .withCollectionName(collectionName)
                    .build();

            milvusClient.loadCollection(loadCollectionParam);
        }
    }

    /**
     * 将FAQ文档的向量存储到Milvus
     * @param document FAQ文档
     * @param vector 向量数据
     * @return 向量ID
     */
    public String storeVector(FAQDocument document, List<Float> vector) {
        // 构建插入数据
        List<InsertParam.Field> fields = new ArrayList<>();
        fields.add(new InsertParam.Field("document_id", Arrays.asList(document.getId())));
        fields.add(new InsertParam.Field("vector", Collections.singletonList(vector)));

        InsertParam insertParam = InsertParam.newBuilder()
                .withCollectionName(collectionName)
                .withFields(fields)
                .build();

        R<MutationResult> insertResponse = milvusClient.insert(insertParam);
        if (insertResponse.getStatus() != R.Status.Success.getCode()) {
            throw new RuntimeException("Failed to insert vector: " + insertResponse.getMessage());
        }

        // 获取插入的向量ID
        List<Long> ids = insertResponse.getData().getIDs().getInt64IdsList();
        return ids.get(0).toString();
    }

    /**
     * 根据查询向量检索最相似的FAQ文档
     * @param queryVector 查询向量
     * @param topK 返回的最相似文档数量
     * @return 最相似的文档ID列表
     */
    public List<Long> searchSimilarDocuments(List<Float> queryVector, int topK) {
        // 构建搜索参数
        List<String> outFields = Arrays.asList("document_id");
        SearchParam searchParam = SearchParam.newBuilder()
                .withCollectionName(collectionName)
                .withConsistencyLevel(ConsistencyLevelEnum.STRONG)
                .withMetricType(MetricType.L2)
                .withOutFields(outFields)
                .withTopK(topK)
                .withVectorFieldName("vector")
                .withVectors(Collections.singletonList(queryVector))
                .withParams("{\"ef\": 100}")
                .build();

        R<SearchResults> searchResponse = milvusClient.search(searchParam);
        if (searchResponse.getStatus() != R.Status.Success.getCode()) {
            throw new RuntimeException("Search failed: " + searchResponse.getMessage());
        }

        // 解析搜索结果
        SearchResultsWrapper wrapper = new SearchResultsWrapper(searchResponse.getData().getResults());
        List<Long> documentIds = new ArrayList<>();

        for (int i = 0; i < wrapper.getResultCount(); i++) {
            List<SearchResultsWrapper.IDScore> scores = wrapper.getIDScore(i);
            for (SearchResultsWrapper.IDScore score : scores) {
                JSONObject jsonObject = new JSONObject(wrapper.getFieldData("document_id", i, score.getIndex()));
                Long documentId = jsonObject.getLong("document_id");
                documentIds.add(documentId);
            }
        }

        return documentIds;
    }

    /**
     * 根据文档ID删除向量
     * @param documentId 文档ID
     */
    public void deleteVectorByDocumentId(Long documentId) {
        DeleteParam deleteParam = DeleteParam.newBuilder()
                .withCollectionName(collectionName)
                .withExpr("document_id == " + documentId)
                .build();

        milvusClient.delete(deleteParam);
    }

    /**
     * 关闭Milvus连接
     */
    public void close() {
        if (milvusClient != null) {
            milvusClient.close();
        }
    }
}