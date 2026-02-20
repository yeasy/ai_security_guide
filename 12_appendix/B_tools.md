# 附录 B：安全工具与资源

本附录收录 LLM 安全相关的工具和学习资源。

## 安全测试工具

### 漏洞扫描

| 工具名称 | 描述 | 链接 |
|----------|------|------|
| Garak | NVIDIA 开发的 LLM 漏洞扫描工具 | https://github.com/NVIDIA/garak |
| promptfoo | Prompt 测试和评估框架 | https://github.com/promptfoo/promptfoo |
| PyRIT | AI 红队自动化工具 | https://github.com/Azure/PyRIT |
| ART | IBM 的对抗鲁棒性工具箱 | https://github.com/Trusted-AI/adversarial-robustness-toolbox |
| HarmBench | 针对 LLM 的自动化红队评估框架 | https://github.com/centerforaisafety/HarmBench |
| HouYi | 针对 LLM 集成应用的自动化注入框架 | https://github.com/LLMSecurity/HouYi |
| AutoDAN | 基于遗传算法的自动化越狱生成 | https://github.com/SheltonLiu-N/AutoDAN |


### 防护框架

| 工具名称 | 描述 | 链接 |
|----------|------|------|
| NeMo Guardrails | NVIDIA 的可编程安全护栏框架 | https://github.com/NVIDIA/NeMo-Guardrails |
| Guardrails AI | 输入/输出校验与结构化数据验证 | https://github.com/guardrails-ai/guardrails |
| Invariant | 面向 Agent 的持续监控与策略执行 | https://invariantlabs.ai/ |
| OpenAI Guardrails | OpenAI 的安全合规校验模块 | https://github.com/openai/guardrails |

### 注入检测与防御

| 工具名称 | 描述 | 链接 |
|----------|------|------|
| Meta Llama Prompt Guard | 专门检测提示注入和越狱的模型 | https://huggingface.co/meta-llama/Prompt-Guard-86M |
| Azure AI Content Safety | 微软云端内容安全服务（含注入检测） | https://azure.microsoft.com/products/ai-services/ai-content-safety |
| Rebuff（已归档） | 提示注入检测与防御框架（维护状态：Archived） | https://github.com/protectai/rebuff |

### 内容审核

| 工具名称 | 描述 | 链接 |
|----------|------|------|
| OpenAI Moderation API | 内容审核 API | https://platform.openai.com/docs/guides/moderation |
| Perspective API | Google 的毒性检测 API | https://perspectiveapi.com/ |
| Azure Content Safety | 微软内容安全服务 | https://azure.microsoft.com/services/ai-services/content-safety/ |

### 隐私保护

| 工具名称 | 描述 | 链接 |
|----------|------|------|
| Presidio | 微软的 PII 检测和脱敏工具 | https://github.com/microsoft/presidio |
| PySyft | 隐私保护机器学习库 | https://github.com/OpenMined/PySyft |
| Opacus | PyTorch 差分隐私库 | https://github.com/pytorch/opacus |

## 安全框架与指南

### 标准与框架

| 名称 | 描述 | 链接 |
|------|------|------|
| OWASP LLM Top 10 | LLM 十大安全风险 | https://genai.owasp.org/llm-top-10/ |
| NIST AI RMF | AI 风险管理框架 | https://www.nist.gov/itl/ai-risk-management-framework |
| NIST AI 600-1 (GenAI Profile) | 生成式 AI 风险管理配置文件 | https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence |
| MITRE ATLAS | AI 对抗威胁矩阵 | https://atlas.mitre.org/ |
| ISO/IEC 42001 | AI 管理体系标准 | https://www.iso.org/standard/81230.html |

### 最佳实践

| 资源 | 描述 | 链接 |
|------|------|------|
| Google Secure AI Framework | Google 安全 AI 框架 | https://safety.google/cybersecurity-advancements/saif/ |
| Microsoft Responsible AI | 微软负责任 AI | https://www.microsoft.com/ai/responsible-ai |
| Anthropic Safety | Anthropic 安全研究 | https://www.anthropic.com/research |

## 学习资源

### 在线课程

| 课程 | 平台 | 描述 | 链接 |
|------|------|------|------|
| AI Security | Coursera | AI 安全基础 | https://www.coursera.org/learn/ai-security |
| LLM Security | edX | LLM 安全专项 | https://www.edx.org/learn/artificial-intelligence |
| Prompt Engineering | DeepLearning.AI | 提示工程最佳实践 | https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/ |

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
| LLM Security Newsletter | 定期 LLM 安全资讯 | https://llmsecurity.net/ |
| AI Safety Research | AI 安全研究进展 | https://www.alignmentforum.org/ |
| Security Blog @ OpenAI | OpenAI 安全博客 | https://openai.com/safety/ |
| Model Context Protocol | MCP 规范与安全实践 | https://modelcontextprotocol.io/specification/ |

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

---

*注意：工具和资源持续更新。请访问官方网站获取最新信息，部分项目可能停更或归档。*
