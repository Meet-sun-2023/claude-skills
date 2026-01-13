import React, { useState } from 'react';
import { Layout, Menu, Typography, ConfigProvider } from 'antd';
import { 
  SearchOutlined, FileTextOutlined, HomeOutlined, 
  DatabaseOutlined, SettingOutlined 
} from '@ant-design/icons';
import QueryComponent from './components/QueryComponent';
import DocumentManager from './components/DocumentManager';
import './App.css';

const { Header, Content, Sider } = Layout;
const { Title } = Typography;

function App() {
  const [currentMenu, setCurrentMenu] = useState('query');

  // 菜单选择处理
  const handleMenuSelect = ({ key }) => {
    setCurrentMenu(key);
  };

  // 渲染当前内容
  const renderContent = () => {
    switch (currentMenu) {
      case 'query':
        return <QueryComponent />;
      case 'documents':
        return <DocumentManager />;
      case 'statistics':
        return <div style={{ padding: 20 }}>统计分析功能开发中...</div>;
      case 'settings':
        return <div style={{ padding: 20 }}>系统设置功能开发中...</div>;
      default:
        return <QueryComponent />;
    }
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        {/* 左侧导航栏 */}
        <Sider
          breakpoint="lg"
          collapsedWidth="0"
          theme="light"
        >
          <div className="logo">
            <DatabaseOutlined style={{ fontSize: 24, color: '#1890ff' }} />
            <span>知识库系统</span>
          </div>
          <Menu
            theme="light"
            mode="inline"
            selectedKeys={[currentMenu]}
            onSelect={handleMenuSelect}
            items={[
              {
                key: 'query',
                icon: <SearchOutlined />,
                label: '自然语言查询',
              },
              {
                key: 'documents',
                icon: <FileTextOutlined />,
                label: '文档管理',
              },
              {
                key: 'statistics',
                icon: <DatabaseOutlined />,
                label: '统计分析',
              },
              {
                key: 'settings',
                icon: <SettingOutlined />,
                label: '系统设置',
              },
            ]}
          />
        </Sider>
        
        <Layout>
          {/* 顶部导航栏 */}
          <Header style={{ 
            background: '#fff', 
            padding: '0 20px', 
            display: 'flex', 
            alignItems: 'center',
            borderBottom: '1px solid #f0f0f0'
          }}>
            <Title level={3} style={{ margin: 0 }}>知识库系统</Title>
          </Header>
          
          {/* 主内容区域 */}
          <Content style={{ 
            margin: '20px', 
            padding: 20, 
            background: '#fff', 
            borderRadius: 8,
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.09)'
          }}>
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  );
}

export default App;