<div align="center">

# 大模型安全权威指南

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![GitHub stars](https://img.shields.io/github/stars/yeasy/ai_security_guide?style=social)](https://github.com/yeasy/ai_security_guide)
[![Online Reading](https://img.shields.io/badge/在线阅读-GitBook-brightgreen)](https://yeasy.gitbook.io/ai_security_guide)

> 从原理到实践，全面掌握大语言模型的安全攻防之道

<img src="_images/cover.jpg" width="300" alt="AI Security Guide Cover">

</div>

---

## 关于本书

随着 ChatGPT、Claude、Gemini 等大语言模型（Large Language Model，LLM）的广泛普及，人工智能正以前所未有的速度渗透到社会的各个角落。然而，伴随着这场技术革命而来的，是日益严峻的安全挑战。提示注入攻击可以绕过模型的安全护栏，越狱技术能够诱导模型生成有害内容，数据投毒可能在训练阶段埋下隐患，而敏感信息泄露则威胁着用户隐私与企业机密。

本书系统性地梳理了大语言模型安全领域的核心知识，从基础概念到前沿攻防技术，从理论原理到工程实践，旨在帮助读者建立完整的 LLM 安全知识体系。无论是希望了解 LLM 安全风险的技术管理者，还是致力于构建安全 LLM 应用的开发者，亦或是专注于 AI 安全研究的学者，都能从本书中获得有价值的知识与启发。

---

## 目标读者

- **AI/ML 工程师与开发者**：希望在开发 LLM 应用时融入安全设计，避免常见漏洞
- **安全工程师与渗透测试人员**：需要掌握 LLM 特有的攻击面与防御手段
- **技术管理者与架构师**：负责制定 AI 安全策略与合规方案
- **AI 安全研究人员**：关注学术前沿，探索新型攻击与防御方法
- **对 AI 安全感兴趣的技术爱好者**：希望系统性了解 LLM 安全全貌

---

## 你将学到什么

阅读本书后，你将能够：

1. **理解 LLM 安全的基本概念**
 - 掌握大语言模型的工作原理与安全边界
 - 了解 LLM 安全与传统软件安全的异同
 - 熟悉 OWASP LLM Top 10 等权威安全框架

2. **识别与分析 LLM 攻击手段**
 - 深入理解提示注入、越狱、数据投毒等核心攻击技术
 - 掌握针对智能体系统、RAG 架构的新型攻击向量
 - 学会使用红队测试方法评估模型安全性

3. **构建安全的 LLM 应用**
 - 设计具备纵深防御能力的安全架构
 - 实施输入验证、输出过滤、权限控制等防护措施
 - 部署监控告警与应急响应机制

4. **应对合规与治理挑战**
 - 了解全球 AI 监管格局，包括 EU AI Act、中国《生成式人工智能服务管理暂行办法》等核心法规
 - 建立完善的 AI 治理框架与安全运营体系
 - 平衡安全性、可用性与创新性

---

## 本书特色

- **系统全面**：覆盖 LLM 安全的全生命周期，从训练到部署，从攻击到防御
- **理论与实践结合**：既有深入的技术原理剖析，也有可落地的工程实践指南
- **紧跟前沿**：覆盖最新的关键安全研究成果与行业实践，并提供持续更新路径
- **案例驱动**：通过真实案例帮助读者理解抽象概念

---

## 阅读建议

本书采用循序渐进的结构，建议按顺序阅读：

- **第一部分（第 1-3 章）** 建立基础认知，适合所有读者
- **第二部分（第 4-7 章）** 深入攻击技术，适合需要了解威胁的读者
- **第三部分（第 8-10 章）** 聚焦防御实践，适合需要构建安全系统的读者
- **第四部分（第 11 章与附录）** 治理展望与资源汇总，适合持续学习者

对于时间有限的读者，可优先阅读第 1 章、第 4 章、第 8 章和第 11 章，快速建立整体认知。

---

## 作者说明

本书创作于近期，并已完成一轮法规、框架与工具清单校准。由于该领域发展极为迅速，书中部分内容可能随着时间推移而需要更新。建议读者结合附录中的资源列表，持续关注该领域的最新动态。

---

## 推荐阅读

本书是 AI 技术丛书的一部分。以下书籍与本书形成互补：

| 书名 | 与本书的关系 |
|------|------------|
| [《零基础学 AI》](https://github.com/yeasy/ai_beginner_guide) | AI 零基础入门，适合缺乏 AI 背景的读者 |
| [《大模型提示词工程指南》](https://github.com/yeasy/prompt_engineering_guide) | 理解提示词注入攻击的前置知识 |
| [《大模型上下文工程权威指南》](https://github.com/yeasy/context_engineering_guide) | 深入理解 RAG 安全的上下文工程基础 |
| [《智能体 AI 权威指南》](https://github.com/yeasy/agentic_ai_guide) | 理解智能体系统的架构，为智能体安全提供背景 |
| [《Claude 技术指南》](https://github.com/yeasy/claude_guide) | 了解 Claude 的安全设计理念（宪法式 AI）与工具安全 |
| [《OpenClaw 从入门到精通》](https://github.com/yeasy/openclaw_guide) | 智能体框架的安全基线与审计流程实践 |
| [《大模型原理与架构》](https://github.com/yeasy/llm_internals) | 深入理解大语言模型底层逻辑与架构 |

---

## 快速开始

### 在线阅读

👉 **推荐**：[GitBook 在线版](https://yeasy.gitbook.io/ai_security_guide/)

### 本地阅读

使用 [HonKit](https://github.com/honkit/honkit) 构建本地阅读环境：

```bash
npm install        # 安装依赖
npx honkit serve   # 启动本地服务
```

启动后访问 http://localhost:4000 即可阅读。

---

## 参与贡献

欢迎贡献！您可以通过以下方式参与：

- 🐛 [提交 Issue](https://github.com/yeasy/ai_security_guide/issues) — 报告错误或提出建议
- 📝 [提交 PR](https://github.com/yeasy/ai_security_guide/pulls) — 改进内容或修复 typo
- ⭐ Star 本项目 — 帮助更多人发现这本书

---

## 许可证

本书采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。

您可以自由分享和演绎，但需署名、非商业使用、相同方式共享。
