import React, { useState, useEffect } from 'react';
import { 
  Card, Button, Table, Input, Form, Modal, Upload, message, 
  Popconfirm, Space, Select, Tag 
} from 'antd';
import { 
  PlusOutlined, EditOutlined, DeleteOutlined, UploadOutlined,
  SearchOutlined 
} from '@ant-design/icons';
import { documentApi } from '../services/api';

const { TextArea } = Input;
const { Option } = Select;

const DocumentManager = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  
  const [form] = Form.useForm();
  const [modalVisible, setModalVisible] = useState(false);
  const [modalTitle, setModalTitle] = useState('添加文档');
  const [editingId, setEditingId] = useState(null);

  // 获取文档列表
  const fetchDocuments = async () => {
    setLoading(true);
    try {
      const params = {
        page: currentPage,
        page_size: pageSize,
        keyword: searchKeyword,
        category: categoryFilter
      };
      const response = await documentApi.getDocuments(params);
      if (response.success) {
        setDocuments(response.data.list);
        setTotal(response.data.total);
      } else {
        message.error(response.message || '获取文档列表失败');
      }
    } catch (error) {
      message.error('获取文档列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 组件加载时获取文档列表
  useEffect(() => {
    fetchDocuments();
  }, [currentPage, pageSize, searchKeyword, categoryFilter]);

  // 处理添加文档
  const handleAddDocument = () => {
    form.resetFields();
    setEditingId(null);
    setModalTitle('添加文档');
    setModalVisible(true);
  };

  // 处理编辑文档
  const handleEditDocument = (record) => {
    form.setFieldsValue({
      question: record.question,
      answer: record.answer,
      category: record.category,
      tags: record.tags ? record.tags.split(',') : []
    });
    setEditingId(record.id);
    setModalTitle('编辑文档');
    setModalVisible(true);
  };

  // 处理删除文档
  const handleDeleteDocument = async (id) => {
    try {
      const response = await documentApi.deleteDocument(id);
      if (response.success) {
        message.success('删除文档成功');
        fetchDocuments(); // 重新获取文档列表
      } else {
        message.error(response.message || '删除文档失败');
      }
    } catch (error) {
      message.error('删除文档失败，请稍后重试');
    }
  };

  // 处理表单提交
  const handleFormSubmit = async () => {
    try {
      const values = await form.validateFields();
      const documentData = {
        ...values,
        tags: values.tags ? values.tags.join(',') : ''
      };

      let response;
      if (editingId) {
        // 更新文档
        response = await documentApi.updateDocument(editingId, documentData);
      } else {
        // 添加文档
        response = await documentApi.createDocument(documentData);
      }

      if (response.success) {
        message.success(editingId ? '更新文档成功' : '添加文档成功');
        setModalVisible(false);
        fetchDocuments(); // 重新获取文档列表
      } else {
        message.error(response.message || '操作失败');
      }
    } catch (error) {
      message.error('操作失败，请稍后重试');
    }
  };

  // 处理文件上传
  const handleFileUpload = async (file) => {
    try {
      const response = await documentApi.uploadDocuments(file);
      if (response.success) {
        message.success(`成功上传 ${response.data.success_count} 个文档，失败 ${response.data.error_count} 个`);
        fetchDocuments(); // 重新获取文档列表
      } else {
        message.error(response.message || '上传失败');
      }
    } catch (error) {
      message.error('上传失败，请稍后重试');
    }
    return false; // 返回false以阻止自动上传
  };

  // 表格列配置
  const columns = [
    {
      title: '问题',
      dataIndex: 'question',
      key: 'question',
      width: 300,
      ellipsis: true,
      render: (text) => (
        <a href="#" onClick={(e) => e.preventDefault()} style={{ color: '#1890ff' }}>
          {text}
        </a>
      )
    },
    {
      title: '答案',
      dataIndex: 'answer',
      key: 'answer',
      width: 400,
      ellipsis: true,
      render: (text) => (
        <div style={{ display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {text}
        </div>
      )
    },
    {
      title: '分类',
      dataIndex: 'category',
      key: 'category',
      width: 150,
      render: (category) => (
        <Tag color={category ? 'blue' : 'default'}>{category || '未分类'}</Tag>
      )
    },
    {
      title: '标签',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags) => (
        <Space>
          {tags ? tags.split(',').map((tag, index) => (
            <Tag key={index}>{tag}</Tag>
          )) : null}
        </Space>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_, record) => (
        <Space size="middle">
          <Button
            type="link"
            icon={<EditOutlined />}
            onClick={() => handleEditDocument(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个文档吗？"
            onConfirm={() => handleDeleteDocument(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ];

  return (
    <Card title="文档管理" className="document-manager">
      <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center' }}>
        <div style={{ flex: 1, display: 'flex', gap: 16 }}>
          <Input
            placeholder="搜索问题或答案"
            prefix={<SearchOutlined />}
            value={searchKeyword}
            onChange={(e) => {
              setSearchKeyword(e.target.value);
              setCurrentPage(1);
            }}
            style={{ flex: 1 }}
          />
          <Select
            placeholder="选择分类"
            value={categoryFilter}
            onChange={(value) => {
              setCategoryFilter(value);
              setCurrentPage(1);
            }}
            style={{ width: 200 }}
            allowClear
          >
            {/* 动态加载分类选项 */}
            {Array.from(new Set(documents.map(doc => doc.category)))
              .filter(category => category)
              .map(category => (
                <Option key={category} value={category}>{category}</Option>
              ))}
          </Select>
        </div>
        
        <Space>
          <Upload
            accept=".txt,.md"
            beforeUpload={handleFileUpload}
            showUploadList={false}
          >
            <Button icon={<UploadOutlined />}>批量上传</Button>
          </Upload>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleAddDocument}>
            添加文档
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={documents}
        rowKey="id"
        loading={loading}
        pagination={{
          current: currentPage,
          pageSize: pageSize,
          total: total,
          onChange: (page, size) => {
            setCurrentPage(page);
            setPageSize(size);
          },
          showSizeChanger: true,
          pageSizeOptions: ['10', '20', '50', '100'],
          showTotal: (total, range) => 
            `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
        }}
        scroll={{ x: 1200 }}
      />

      {/* 文档编辑模态框 */}
      <Modal
        title={modalTitle}
        open={modalVisible}
        onOk={handleFormSubmit}
        onCancel={() => setModalVisible(false)}
        okText="保存"
        cancelText="取消"
        width={800}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ tags: [] }}
        >
          <Form.Item
            name="question"
            label="问题"
            rules={[{ required: true, message: '请输入问题' }]}
          >
            <Input placeholder="请输入问题" />
          </Form.Item>

          <Form.Item
            name="answer"
            label="答案"
            rules={[{ required: true, message: '请输入答案' }]}
          >
            <TextArea
              placeholder="请输入答案"
              rows={6}
            />
          </Form.Item>

          <Form.Item
            name="category"
            label="分类"
          >
            <Input placeholder="请输入分类" />
          </Form.Item>

          <Form.Item
            name="tags"
            label="标签"
          >
            <Select
              mode="tags"
              placeholder="请输入标签，多个标签用逗号分隔"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>
    </Card>
  );
};

export default DocumentManager;