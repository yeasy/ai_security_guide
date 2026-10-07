<div align="center">

# 大模型安全权威指南

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![GitHub stars](https://img.shields.io/github/stars/yeasy/ai_security_guide?style=social)](https://github.com/yeasy/ai_security_guide)
[![Release](https://img.shields.io/github/release/yeasy/ai_security_guide.svg)](https://github.com/yeasy/ai_security_guide/releases)
[![Online Reading](https://img.shields.io/badge/在线阅读-GitBook-brightgreen)](https://yeasy.gitbook.io/ai_security_guide)
[![PDF](https://img.shields.io/badge/PDF-下载-orange)](https://github.com/yeasy/ai_security_guide/releases/latest)

> 从原理到实践，全面掌握大语言模型的安全攻防之道

<img src="_images/cover.jpg" width="300" alt="AI Security Guide Cover">

</div>

---

## 开始阅读

- **在线阅读**：[GitBook 在线版](https://yeasy.gitbook.io/ai_security_guide/)（推荐）
- **PDF 下载**：前往 [GitHub Releases](https://github.com/yeasy/ai_security_guide/releases/latest) 下载最新版本

---

## 关于本书

本书讲解大语言模型与智能体的攻击原理、防御机制和验证方法。以邮件助手为例：模型读取来信，选择文档并请求发送；安全设计要查清来信能影响哪些参数、文档允许谁读取、谁批准发送，以及失败重试会不会重复执行。

阅读时始终区分两个问题：模型产生危险输出的概率能否降低；即使模型输出错误，系统是否仍能阻止越权读取、发送或执行。前者涉及对齐与检测，后者依赖模型之外的授权、隔离和执行检查。每种控制都须说明适用条件与未覆盖的路径。

## 阅读路径

工程实践需要 Python、HTTP、身份权限与日志基础；训练与攻击搜索还需要概率统计、线性代数和梯度基础。

| 学习任务 | 阅读顺序 | 应完成的练习 |
|----------|----------|--------------|
| 建立基础 | 第 1–3 章 | 画出应用的数据流，标记输入来源、敏感资源和执行权限 |
| 分析攻击 | 第 4–7 章 | 复现合成攻击，解释攻击者可控内容如何影响输出或动作 |
| 实现与验证防御 | 第 8–10 章 | 实现控制，分别测正常效用、拒绝行为、失败路径和运营指标 |
| 设计智能体系统 | 第 11–14 章 | 沿一次工具调用检查身份、参数、凭据、批准、执行与状态回写 |
| 治理与交付 | 第 15 章 | 将适用要求对应到责任人、工程控制、证据与复核条件 |

已有开发经验、希望先完成一个系统的读者，可从 [11.1 的调用循环](11_agent_foundations/11.1_agent_implementation.md)进入，阅读 [14.1 的邮件助手案例](14_agent_practice/14.1_case_study.md)，再结合 [13.2 的架构防御](13_agent_architecture/13.2_architectural_defenses.md)运行下方实验。涉及研究比较、完整策略实现和治理模板的材料放在[拓展阅读与附录](SUMMARY.md#附录)，可按问题查阅。

## 配套实验

实验使用 Python 标准库和固定合成数据，运行入口位于仓库根目录：

| 实验 | 连接的章节 | 需要观察的内部行为 |
|------|------------|--------------------|
| [邮件助手](examples/mail_assistant/README.md) | [13.2](13_agent_architecture/13.2_architectural_defenses.md)、[14.1](14_agent_practice/14.1_case_study.md)–[14.2](14_agent_practice/14.2_security_panorama.md) | 变量来源、读取授权、发送判定、参数摘要批准、发送箱与未知状态查询 |
| [支付预算](examples/payment_budget/README.md) | [14.5](14_agent_practice/14.5_payment_security.md)、[12.7](12_agent_attack_surface/12.7_multi_agent_security.md)、[13.4](13_agent_architecture/13.4_agent_identity.md) | 并发原子预留、参数绑定重放、UNKNOWN 占用与可信对账 |
| [RAG 轨迹](examples/rag_trace/README.md) | [7.3](07_rag_security/7.3_retrieval_manipulation.md)、[7.5](07_rag_security/7.5_vector_database_security.md)–[7.8](07_rag_security/7.8_rag_evaluation_best_practices.md) | 候选与排序、ACL、上下文、生成判定、缓存撤销及 ASR 分母 |

```bash
python3 examples/mail_assistant/lab.py
python3 examples/payment_budget/ledger.py
python3 examples/rag_trace/lab.py
```

先保留正常效用，再分别关闭控制，核对同一判定器是否捕获预期错误。合成实验不测真实模型攻击成功率、操作系统沙箱或生产支付；各实验说明列出了替换这些组件时需要补充的验收。

---

## 推荐阅读

本书是 AI 技术丛书的一部分。以下书籍与本书形成互补：

| 书名 | 与本书的关系 |
|------|------------|
| [《零基础学 AI》](https://yeasy.gitbook.io/ai_beginner_guide) | AI 零基础入门，适合缺乏 AI 背景的读者 |
| [《大模型提示词工程指南》](https://yeasy.gitbook.io/prompt_engineering_guide) | 理解提示注入攻击的前置知识 |
| [《大模型上下文工程权威指南》](https://yeasy.gitbook.io/context_engineering_guide) | 深入理解 RAG 安全的上下文工程基础 |
| [《智能体 AI 权威指南》](https://yeasy.gitbook.io/agentic_ai_guide) | 理解智能体系统的架构，为智能体安全提供背景 |
| [《Claude 技术指南》](https://yeasy.gitbook.io/claude_guide) | 了解 Claude 的安全设计理念（宪法式 AI）与工具安全 |
| [《OpenClaw 入门到精通》](https://yeasy.gitbook.io/openclaw_guide) | 智能体框架的安全基线与审计流程实践 |
| [《大模型原理与架构》](https://yeasy.gitbook.io/llm_internals) | 深入理解大语言模型底层逻辑与架构 |
| [《智能体 Harness 工程指南》](https://yeasy.gitbook.io/harness_engineering_guide) | 智能体 Harness 层的安全体系设计与沙箱隔离实践 |

---

## 许可证

本书采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。

您可以自由分享和演绎，但需署名、非商业使用、相同方式共享。
