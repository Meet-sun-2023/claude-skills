# 知识库系统

基于Java SpringBoot和ReactJS开发的知识库系统，支持自然语言查询和文档管理功能。

## 项目结构

```
├── 代码/                  # 代码目录
│   ├── backend/          # 后端代码
│   └── frontend/         # 前端代码
├── 设计文档/              # 设计文档
│   └── 知识库设计/        # 知识库系统设计文档
└── README.md             # 项目说明文档
```

## 技术栈

- **后端**: Java 11+, SpringBoot 2.7.x, Spring Data JPA, SpringDoc OpenAPI, Milvus Java SDK
- **前端**: ReactJS 18+, Ant Design, Vite
- **数据库**: MySQL
- **向量数据库**: Milvus

## 开发说明

- 后端使用SpringBoot MVC框架，基于Java 11+开发
- 使用Spring Data JPA实现数据库操作
- 使用SpringDoc OpenAPI生成API文档
- 前端使用React hooks和Ant Design组件库
- 采用RAG技术实现自然语言查询，集成Milvus向量数据库
- 支持CORS跨域请求
