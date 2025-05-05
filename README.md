```markdown
# 🛡️ 大模型黑盒攻防能力评估平台

## 📖 项目概述

### 行业背景
随着大模型技术的快速发展，其安全可靠性面临严峻挑战。当前学术界虽已提出多种黑盒攻击方法与防御策略，但缺乏统一的评估体系，研究者需耗费大量时间在分散的测试环境中验证模型能力，严重阻碍攻防研究的迭代效率。

### 解决方案
本平台创新性地构建了首个**模块化大模型攻防评估系统**，具备以下核心能力：
- 🔧 **多攻击方法集成**：支持主流黑盒攻击技术横向对比
- 🛡️ **防御能力量化评估**：提供对抗样本抵御率、防御成功率等10+关键指标
- 🚀 **弹性扩展架构**：标准化接口设计，支持快速接入新模型/攻击策略
- 📊 **可视化分析**：生成多维度的攻防效能评估报告
- 🧠 **创新攻击引擎**：内置改进型黑盒攻击算法（论文级创新）（这个后期慢慢实现吧~）

## 🚀 快速启动

### 环境配置

# 后端
# 克隆项目仓库
git clone https://github.com/Nights0907/LLM-Attack-Defense-Platform-Backend.git
cd LLM-Attack-Defense-Platform-Backend

# 创建虚拟环境
conda create -n llm-attack python=3.9 -y
conda activate llm-attack

# 安装依赖
pip install -r requirements.txt

# 配置mysql和mongo数据库
    1. 本地开启mysql和mongodb服务
        (1) 配置mongodb参考: https://blog.csdn.net/X_xxxx7/article/details/142589242
        (2) 配置mysql数据库直接运行项目根目录下的 attack_llm.sql 文件
    2. 在app/__init__.py中更改自己的数据库信息
        # 配置mysql
        app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:123456@localhost/llm_attack'
        # 配置mongodb
        app.config["MONGO_URI"] = "mongodb://localhost:27017/llm_attack"

# 前端
# 克隆项目仓库
git clone https://github.com/Nights0907/LLM-Attack-Defense-Platform-Frontend.git
cd LLM-Attack-Defense-Platform-Frontend

npm install
npm run build
npm run serve


```
