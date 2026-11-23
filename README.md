# 大模型安全权威指南

理解大语言模型与智能体的安全风险，设计并验证权限、隔离和执行控制。

**[在 GitBook 阅读第一章 · 大语言模型安全导论](https://yeasy.gitbook.io/ai_security_guide/di-yi-bu-fen-ji-chu-pian/01_intro)**

[全书目录（GitHub）](https://github.com/yeasy/ai_security_guide/blob/main/SUMMARY.md?plain=0) · [正式 PDF（发布页）](https://github.com/yeasy/ai_security_guide/releases/latest)

<img src="_images/cover.jpg" width="210" alt="大模型安全权威指南封面">

## 关于本书

本书讲解大语言模型与智能体的攻击原理、防御机制和验证方法。以邮件助手为例：模型读取来信，选择文档并请求发送；安全设计要查清来信能影响哪些参数、文档允许谁读取、谁批准发送，以及失败重试会不会重复执行。

阅读时始终区分两个问题：模型产生危险输出的概率能否降低；即使模型输出错误，系统是否仍能阻止越权读取、发送或执行。前者涉及对齐与检测，后者依赖模型之外的授权、隔离和执行检查。每种控制都须说明适用条件与未覆盖的路径。

## 从哪里开始

- **第一次学习大模型安全** · 从[第一章](https://yeasy.gitbook.io/ai_security_guide/di-yi-bu-fen-ji-chu-pian/01_intro)开始，画出一个应用的数据流，标记输入来源、敏感资源和执行权限。
- **正在加固大模型应用** · 从[安全架构设计](https://yeasy.gitbook.io/ai_security_guide/di-san-bu-fen-fang-yu-pian/08_architecture)入手。若应用使用知识库，重点读[检索时的访问控制](https://yeasy.gitbook.io/ai_security_guide/di-er-bu-fen-gong-ji-pian/07_rag_security/7.6_retrieval_access_control)，检查未授权文档能否进入模型上下文。
- **正在开发能调用工具的智能体** · 先读[智能体的调用过程](https://yeasy.gitbook.io/ai_security_guide/di-si-bu-fen-zhi-neng-ti-an-quan-pian/11_agent_foundations/11.1_agent_implementation)，再看[邮件与文档助手案例](https://yeasy.gitbook.io/ai_security_guide/di-si-bu-fen-zhi-neng-ti-an-quan-pian/14_agent_practice/14.1_case_study)，沿一次工具调用检查身份、参数、批准和执行结果。
- **负责安全治理与交付** · 参照[合规实操指南](https://yeasy.gitbook.io/ai_security_guide/di-wu-bu-fen-zhi-li-yu-zhan-wang/15_governance/15.4_compliance_operational)，用[附录 E 的工作模板](https://yeasy.gitbook.io/ai_security_guide/fu-lu/16_appendix/e_compliance_templates)记录工程控制、责任人、验收证据和复核条件。

<details>

<summary>完整学习路线与前置知识</summary>

工程实践需要 Python、HTTP、身份权限与日志基础；训练与攻击搜索还需要概率统计、线性代数和梯度基础。

| 学习任务 | 阅读顺序 | 应完成的练习 |
|----------|----------|--------------|
| 建立基础 | 第 1–3 章 | 画出应用的数据流，标记输入来源、敏感资源和执行权限 |
| 分析攻击 | 第 4–7 章 | 分析合成用例，解释不可信输入如何影响模型输出或系统动作 |
| 实现与验证防御 | 第 8–10 章 | 实现控制，分别测正常效用、拒绝行为、失败路径和运营指标 |
| 设计智能体系统 | 第 11–14 章 | 沿一次工具调用检查身份、参数、凭据、批准、执行与状态回写 |
| 治理与交付 | 第 15 章 | 将适用要求对应到责任人、工程控制、证据与复核条件 |

研究比较、完整策略实现和治理模板见[附录](https://yeasy.gitbook.io/ai_security_guide/fu-lu/16_appendix)。

</details>

## 配套实验

实验使用 Python 标准库和固定合成数据，包含正常请求与控制失效的对照用例。

- [邮件与文档助手](https://yeasy.gitbook.io/ai_security_guide/fu-lu/16_appendix/mail_assistant) · 检查文档读取权限、发送审批与超时后的状态查询。
- [可信预算状态](https://yeasy.gitbook.io/ai_security_guide/fu-lu/16_appendix/payment_budget) · 验证并发请求、重复提交和执行结果未知时，预算如何预留和结算。
- [RAG 轨迹与授权](https://yeasy.gitbook.io/ai_security_guide/fu-lu/16_appendix/rag_trace) · 对照检索候选与实际交给模型的上下文，检查访问控制、权限撤销和缓存。

<details>

<summary>运行命令与对应章节</summary>

在本书的 [GitHub 仓库](https://github.com/yeasy/ai_security_guide)根目录运行对应的命令。

```bash
python3 examples/mail_assistant/lab.py
python3 examples/payment_budget/ledger.py
python3 examples/rag_trace/lab.py
```

| 实验 | 对应章节 |
|------|----------|
| 邮件与文档助手 | [架构级防御](13_agent_architecture/13.2_architectural_defenses.md)、[邮件与文档助手](14_agent_practice/14.1_case_study.md)、[智能体安全全景](14_agent_practice/14.2_security_panorama.md) |
| 可信预算状态 | [授权凭证与可信预算](14_agent_practice/14.5_payment_security.md)、[智能体身份与委托授权](13_agent_architecture/13.4_agent_identity.md)、[多智能体系统的安全](12_agent_attack_surface/12.7_multi_agent_security.md) |
| RAG 轨迹与授权 | [向量数据库与嵌入安全](07_rag_security/7.5_vector_database_security.md)、[检索时的访问控制](07_rag_security/7.6_retrieval_access_control.md)、[评测与最佳实践](07_rag_security/7.8_rag_evaluation_best_practices.md) |

实验验证本地模拟程序的行为。真实模型的攻击成功率、操作系统沙箱和生产支付需要分别验收，具体边界见各实验说明。

</details>

## 延伸阅读

- [大模型原理与架构](https://yeasy.gitbook.io/llm_internals/) · 理解训练、推理和模型行为。
- [大模型上下文工程权威指南](https://yeasy.gitbook.io/context_engineering_guide/) · 理解检索、上下文构建和评估。
- [智能体 AI 权威指南](https://yeasy.gitbook.io/agentic_ai_guide/) · 理解智能体的架构、工具调用和协作。

<details>

<summary>更多系列图书</summary>

- [零基础学 AI](https://yeasy.gitbook.io/ai_beginner_guide/)
- [大模型提示词工程指南](https://yeasy.gitbook.io/prompt_engineering_guide/)
- [Claude 技术指南](https://yeasy.gitbook.io/claude_guide/)
- [OpenClaw 从入门到精通](https://yeasy.gitbook.io/openclaw_guide/)
- [智能体 Harness 工程指南](https://yeasy.gitbook.io/harness_engineering_guide/)

</details>

## 反馈与贡献

欢迎在 [GitHub Issues](https://github.com/yeasy/ai_security_guide/issues) 报告勘误或提出建议。

## 许可证

本书采用 [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/) 许可证。

您可以自由分享和演绎，但需署名、非商业使用、相同方式共享。
