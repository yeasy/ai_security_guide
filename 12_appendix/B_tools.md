# 附录 B：安全工具与资源

本附录收录 LLM 安全相关的工具和学习资源。以下条目同时包含开源项目、研究原型与云服务产品，选型前应以官方文档、仓库状态和发布日期为准。

## 安全测试工具

### 红队测试与安全评估

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| Garak | NVIDIA 的 LLM 漏洞探测与红队评估工具 | 活跃维护 | [NVIDIA/garak](https://github.com/NVIDIA/garak) |
| promptfoo | Prompt 测试、评估与红队框架 | 活跃维护 | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) |
| PyRIT | Microsoft 的生成式 AI 红队框架（Python Risk Identification Tool） | 活跃维护 | [microsoft/PyRIT](https://github.com/microsoft/PyRIT) |
| Claude Security | Anthropic 的代码漏洞扫描与修复工具，基于 Opus 4.7 推理式代码审计 | Public Beta | [Anthropic](https://www.anthropic.com/news/claude-security) |
| ART | 面向机器学习安全的工具箱，覆盖对抗样本、投毒、模型提取等；非 LLM 专用 | 活跃维护 | [Trusted-AI/adversarial-robustness-toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox) |
| HarmBench | 自动化红队与拒答鲁棒性的标准化评估框架 | 研究框架 | [centerforaisafety/HarmBench](https://github.com/centerforaisafety/HarmBench) |
| HouYi | 面向 LLM 集成应用的自动化提示注入框架 | 研究原型 | [LLMSecurity/HouYi](https://github.com/LLMSecurity/HouYi) |
| AutoDAN | 自动化越狱生成方法的研究实现 | 研究实现 | [SheltonLiu-N/AutoDAN](https://github.com/SheltonLiu-N/AutoDAN) |

### 防护框架

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| NeMo Guardrails | NVIDIA 的可编程安全护栏框架 | 活跃维护 | [NVIDIA/NeMo-Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) |
| Guardrails AI | 输入/输出校验与结构化验证框架 | 活跃维护 | [guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) |
| Invariant | 面向智能体的安全监测与策略控制产品 | 活跃维护 | [Invariant Labs](https://invariantlabs.ai/) |
| OpenAI Guardrails | OpenAI 的 Guardrails Python 包，提供可配置的输入/输出校验与审核 | Preview | [openai/openai-guardrails-python](https://github.com/openai/openai-guardrails-python) |

### 注入检测与防御

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| Meta Llama Prompt Guard | 专门检测提示注入和越狱的模型 | 活跃维护 | [meta-llama/Prompt-Guard-86M](https://huggingface.co/meta-llama/Prompt-Guard-86M) |
| Azure AI Content Safety | 微软云端内容安全服务（含 Prompt Shields） | 活跃维护 | [Microsoft](https://azure.microsoft.com/en-us/products/ai-services/ai-content-safety) |
| AWS Bedrock Guardrails | AWS 云端护栏服务，含内容过滤、PII 与 prompt attack detection | 活跃维护 | [AWS](https://aws.amazon.com/bedrock/guardrails/) |
| Google Cloud Model Armor | Google Cloud 运行时防护服务，可筛查提示、响应与 agent 交互 | 活跃维护 | [Google Cloud](https://cloud.google.com/security/products/model-armor) |
| Rebuff | 提示注入检测与防御框架 | 已归档 | [protectai/rebuff](https://github.com/protectai/rebuff) |

### 内容审核

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| OpenAI Moderation API | 内容审核 API | 活跃维护 | [OpenAI 文档](https://platform.openai.com/docs/guides/moderation) |
| Perspective API | Google 的毒性检测 API | 活跃维护 | [Perspective API](https://perspectiveapi.com/) |
| Azure AI Content Safety | 微软内容安全服务 | 活跃维护 | [Microsoft](https://azure.microsoft.com/en-us/products/ai-services/ai-content-safety) |

### 隐私保护

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| Presidio | 微软的 PII 检测和脱敏工具 | 活跃维护 | [microsoft/presidio](https://github.com/microsoft/presidio) |
| PySyft | 隐私保护机器学习库 | 维护中 | [OpenMined/PySyft](https://github.com/OpenMined/PySyft) |
| Opacus | PyTorch 差分隐私库 | 活跃维护 | [pytorch/opacus](https://github.com/pytorch/opacus) |

## 安全框架与指南

### 标准与框架

| 名称 | 描述 | 链接 |
|------|------|------|
| OWASP LLM Top 10 | LLM 十大安全风险 | [OWASP](https://genai.owasp.org/llm-top-10/) |
| NIST AI RMF | AI 风险管理框架 | [NIST](https://www.nist.gov/itl/ai-risk-management-framework) |
| NIST AI 600-1 (GenAI Profile) | 生成式 AI 风险管理配置文件 | [NIST](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) |
| MITRE ATLAS | AI 对抗威胁矩阵 | [MITRE ATLAS](https://atlas.mitre.org/) |
| ISO/IEC 42001 | AI 管理体系标准 | [ISO](https://www.iso.org/standard/81230.html) |

### 最佳实践

| 资源 | 描述 | 链接 |
|------|------|------|
| Google Secure AI Framework | Google 安全 AI 框架 | [Google Cloud](https://cloud.google.com/use-cases/secure-ai-framework) |
| Microsoft Responsible AI | 微软负责任 AI | [Microsoft](https://www.microsoft.com/ai/responsible-ai) |
| Anthropic Safety | Anthropic 安全研究 | [Anthropic](https://www.anthropic.com/research) |

## 学习资源

### 在线课程

| 课程 | 平台 | 描述 | 链接 |
|------|------|------|------|
| AI Security | Coursera | AI 安全基础 | [Coursera](https://www.coursera.org/learn/ai-security) |
| AI 学习资源 | edX | edX 的 AI 课程聚合页，可作为继续检索相关课程的入口 | [edX](https://www.edx.org/learn/artificial-intelligence) |
| Prompt Engineering | DeepLearning.AI | 提示工程最佳实践 | [DeepLearning.AI](https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/) |

### 研究论文

| 主题 | 代表论文 |
|------|----------|
| 安全对齐 | Training language models to follow instructions with human feedback (InstructGPT) |
| 越狱攻击 | Jailbroken: How Does LLM Safety Training Fail? |
| 提示注入 | Prompt Injection attack against LLM-integrated Applications |
| 隐私保护 | Extracting Training Data from Large Language Models |

### 社区与博客

| 资源 | 描述 | 链接 |
|------|------|------|
| LLM Security Newsletter | 定期 LLM 安全资讯 | [LLM Security Newsletter](https://llmsecurity.net/) |
| AI Safety Research | AI 安全研究进展 | [Alignment Forum](https://www.alignmentforum.org/) |
| Security Blog @ OpenAI | OpenAI 安全博客 | [OpenAI Safety](https://openai.com/safety/) |
| Model Context Protocol | MCP 规范与安全实践 | [Model Context Protocol](https://modelcontextprotocol.io/specification/) |

## 监控与运维工具

### 监控

| 工具 | 功能 |
|------|------|
| Prometheus + Grafana | 指标监控可视化 |
| ELK Stack | 日志管理分析 |
| Datadog | 统一可观测性 |

### 安全运营

| 工具 | 功能 |
|------|------|
| Splunk | SIEM 平台 |
| PagerDuty | 告警管理 |
| JIRA | 工单跟踪 |

## 模型与数据安全

### 模型安全

| 工具 | 功能 |
|------|------|
| ModelScan | 模型安全扫描 |
| ML-Guard | 模型保护框架 |

### 数据安全

| 工具 | 功能 |
|------|------|
| Great Expectations | 数据质量验证 |
| Apache Atlas | 数据治理 |

## 核心工具与 OWASP/生命周期映射索引（速查字典）

为了帮助安全评审人员与研发工程师在特定生命周期阶段，靶向处置特定的 OWASP Top 10 风险，特提供以下实战速查映射表：

| 开发生命周期阶段 | 防御的核心 OWASP 风险 | 推荐部署的开源工具/基线 | 典型落地场景与章节指引 |
|------------------|-----------------------|-------------------------|------------------------|
| **模型训练/微调** | LLM03 (供应链风险)<br>LLM04 (数据投毒) | Great Expectations<br>ModelScan | 数据清洗质量强制卡点验证、第三方模型权重后门漏洞扫描（第 6 章） |
| **应用架构设计** | LLM06 (过度自主权)<br>LLM07 (系统提示泄露) | Microsoft Responsible AI<br>Google SAIF | 会话分层架构设计、RBAC 与人机协同（HITL）审批流预发设计（第 8 章） |
| **知识检索 (RAG)** | LLM08 (向量与嵌入弱点)<br>LLM09 (错误信息) | LlamaIndex<br>自建入库前校验与元数据过滤基线 | 外部文档切块入库前的洗消验签、基于多租户身份的检索结果过滤（第 7 章） |
| **网关边界拦截** | LLM01 (提示注入)<br>LLM10 (无边界消耗) | Meta Llama Prompt Guard<br>NeMo Guardrails | 部署于最外层 API 代理作为低延迟分类器探测越狱，并实施 Token 熔断限流（第 4 章） |
| **输出校验与脱敏**| LLM02 (敏感数据泄露)<br>LLM05 (输出处理不当) | Microsoft Presidio<br>Guardrails AI | 双向 PII 实体检测与掩码还原，强制输出转为受控 Schema 并严格阻断执行链（第 9 章） |
| **CI/CD 安全门禁** | LLM01 (注入绕过)<br>通用安全性回归 | promptfoo<br>Garak<br>HarmBench | 迭代上线前构建自动化对抗评估，将最新漏洞形成集成测试硬拦截门禁（第 10 章） |

---

*注意：工具和资源持续更新。请访问官方网站获取最新信息，部分项目可能停更或归档。*

*状态说明：开源工具、研究项目与云服务的状态可能随时变化，建议在选型前检查项目的最近更新日期、官方说明和社区活跃度。*
