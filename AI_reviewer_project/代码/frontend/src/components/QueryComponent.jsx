import React, { useState } from 'react';
import { Card, Input, Button, Spin, message, Rate } from 'antd';
import { SearchOutlined, LoadingOutlined, MessageOutlined } from '@ant-design/icons';
import { queryApi } from '../services/api';

const { TextArea } = Input;

const QueryComponent = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [queryId, setQueryId] = useState(null);
  const [feedbackGiven, setFeedbackGiven] = useState(false);
  const [rating, setRating] = useState(0);

  // 处理查询
  const handleQuery = async () => {
    if (!question.trim()) {
      message.warning('请输入您的问题');
      return;
    }

    setLoading(true);
    setAnswer('');
    setQueryId(null);
    setFeedbackGiven(false);
    setRating(0);

    try {
      const response = await queryApi.queryFAQ(question);
      if (response.success) {
        setAnswer(response.data.answer);
        setQueryId(response.data.queryId);
      } else {
        message.error(response.message || '查询失败');
      }
    } catch (error) {
      message.error('查询失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  // 处理反馈
  const handleFeedback = async (isHelpful) => {
    if (!queryId) return;

    setFeedbackGiven(true);

    try {
      await queryApi.feedbackQuery(queryId, isHelpful, rating, '');
      message.success('感谢您的反馈！');
    } catch (error) {
      message.error('反馈提交失败');
    }
  };

  return (
    <Card title="自然语言查询" className="query-component" style={{ marginBottom: 20 }}>
      <div style={{ marginBottom: 20 }}>
        <TextArea
          placeholder="请输入您的问题，例如：如何使用知识库系统？"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={4}
          onPressEnter={() => handleQuery()}
        />
      </div>
      
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 20 }}>
        <Button
          type="primary"
          icon={loading ? <Spin indicator={<LoadingOutlined />} /> : <SearchOutlined />}
          onClick={handleQuery}
          loading={loading}
        >
          查询
        </Button>
      </div>

      {answer && (
        <div className="answer-section">
          <Card
            title="查询结果"
            bordered={false}
            style={{ marginBottom: 16, boxShadow: '0 2px 8px rgba(0, 0, 0, 0.09)' }}
          >
            <div style={{ fontSize: 16, lineHeight: 1.8 }}>{answer}</div>
          </Card>

          {!feedbackGiven && (
            <Card
              title="您对这个答案满意吗？"
              bordered={false}
              style={{ boxShadow: '0 2px 8px rgba(0, 0, 0, 0.09)' }}
            >
              <div style={{ display: 'flex', gap: 16, alignItems: 'center', marginBottom: 16 }}>
                <Button
                  type="primary"
                  onClick={() => handleFeedback(true)}
                  style={{ flex: 1 }}
                >
                  满意
                </Button>
                <Button
                  type="default"
                  onClick={() => handleFeedback(false)}
                  style={{ flex: 1 }}
                >
                  不满意
                </Button>
              </div>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <span style={{ whiteSpace: 'nowrap' }}>评分：</span>
                <Rate
                  value={rating}
                  onChange={setRating}
                  style={{ flex: 1 }}
                />
              </div>
            </Card>
          )}
        </div>
      )}
    </Card>
  );
};

export default QueryComponent;