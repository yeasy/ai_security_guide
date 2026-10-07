# 附录 B：安全工具与资源

本附录收录 LLM 与智能体安全相关的工具和学习资源，包括开源项目、研究原型与云服务产品；选型前应查阅官方文档、仓库状态和发布日期。智能体安全工具的分类口径、各类工具文档写明的边界与维护状态见 [13.5 节](../13_agent_architecture/13.5_tooling_selection.md)，本附录只做索引。

## 安全测试工具

### 红队测试与安全评估

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| Garak | NVIDIA 的 LLM 漏洞探测与红队评估工具 | 活跃维护 | [NVIDIA/garak](https://github.com/NVIDIA/garak) |
| promptfoo | Prompt 测试、评估与红队框架 | 活跃维护 | [promptfoo/promptfoo](https://github.com/promptfoo/promptfoo) |
| PyRIT | Microsoft 的生成式 AI 红队框架（Python Risk Identification Tool） | 活跃维护 | [microsoft/PyRIT](https://github.com/microsoft/PyRIT) |
| DeepTeam | Confident AI 的开源 LLM 红队框架，覆盖漏洞模板、攻击编排与报告 | 活跃维护 | [confident-ai/deepteam](https://github.com/confident-ai/deepteam) |
| AgentDojo | 评估工具型智能体提示注入攻防的动态基准，97 个任务、629 个安全测试用例；是评测环境，不是对自有系统的扫描器 | 研究基准 | [ethz-spylab/agentdojo](https://github.com/ethz-spylab/agentdojo) |
| Claude Security | Anthropic 面向代码库的漏洞扫描与补丁建议工具，模型版本和访问范围见官方产品页 | Public Beta（Claude Enterprise） | [Anthropic](https://claude.com/product/claude-security) |
| ART | 面向机器学习安全的工具箱，覆盖对抗样本、投毒、模型提取等；非 LLM 专用 | 活跃维护 | [Trusted-AI/adversarial-robustness-toolbox](https://github.com/Trusted-AI/adversarial-robustness-toolbox) |
| HarmBench | 自动化红队与拒答鲁棒性的标准化评估框架 | 研究框架 | [centerforaisafety/HarmBench](https://github.com/centerforaisafety/HarmBench) |
| HouYi | 面向 LLM 集成应用的自动化提示注入框架 | 研究原型 | [LLMSecurity/HouYi](https://github.com/LLMSecurity/HouYi) |
| AutoDAN | 自动化越狱生成方法的研究实现 | 研究实现 | [SheltonLiu-N/AutoDAN](https://github.com/SheltonLiu-N/AutoDAN) |

### 防护框架

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| NeMo Guardrails | NVIDIA 的可编程护栏框架，用 Colang 定义输入、检索、对话、执行、输出五类护栏 | 活跃维护；Colang 2.0 仍为测试版 | [NVIDIA-NeMo/Guardrails](https://github.com/NVIDIA-NeMo/Guardrails) |
| Guardrails AI | 输入/输出校验与结构化验证框架 | 活跃维护；已宣布停止托管远程推理，验证器改为 PyPI 包 | [guardrails-ai/guardrails](https://github.com/guardrails-ai/guardrails) |
| LlamaFirewall（Meta） | 编排 Prompt Guard 2、AlignmentCheck（审计智能体推理与动作序列）与 CodeShield（生成代码静态分析）的护栏框架 | 框架 MIT，模型权重走 Llama 许可 | [meta-llama/PurpleLlama](https://github.com/meta-llama/PurpleLlama) |
| Invariant Guardrails | 规则式智能体护栏，以 MCP 或 LLM 代理方式拦截工具调用，规则可表达跨调用的流 | 公司被 Snyk 收购后开源仓库停更，托管的 Explorer 已关停 | [Invariant Labs](https://invariantlabs.ai/) |
| OpenAI Guardrails | OpenAI 的 Guardrails Python 包，提供可配置的输入/输出校验与审核 | Preview | [openai/openai-guardrails-python](https://github.com/openai/openai-guardrails-python) |

### 守卫模型与注入检测

开源守卫模型的类别口径、判定对象与选型要点见 [9.2.9 节](../09_io_protection/9.2_output_moderation.md)。

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| Meta Llama Guard 4 | 12B 多模态安全分类器，MLCommons 危害分类 S1 至 S13 加 S14 代码解释器滥用，判定输入与输出 | 活跃维护，Llama 4 Community License | [meta-llama/Llama-Guard-4-12B](https://huggingface.co/meta-llama/Llama-Guard-4-12B) |
| Meta Llama Prompt Guard 2 | 检测提示注入与越狱的多语言分类器（86M / 22M，mDeBERTa，2025-04 随 Llama 4 发布） | 活跃维护，Llama 4 Community License | [meta-llama/Llama-Prompt-Guard-2-86M](https://huggingface.co/meta-llama/Llama-Prompt-Guard-2-86M) |
| IBM Granite Guardian 3.3 | 8B 守卫模型，危害与越狱之外还判定 RAG 幻觉（上下文相关性、有据性、答案相关性）与函数调用幻觉，可选输出推理过程 | 活跃维护，Apache 2.0 | [ibm-granite/granite-guardian-3.3-8b](https://huggingface.co/ibm-granite/granite-guardian-3.3-8b) |
| Google ShieldGemma / ShieldGemma 2 | 2B、9B、27B 文本分类器，判定色情、危险内容、仇恨、骚扰四类；ShieldGemma 2 为 4B 图像分类器 | 活跃维护，Gemma 使用条款 | [google/shieldgemma-2b](https://huggingface.co/google/shieldgemma-2b)、[google/shieldgemma-2-4b-it](https://huggingface.co/google/shieldgemma-2-4b-it) |
| AI2 WildGuard | 7B，一体判定输入有害性、输出有害性与输出是否拒答 | 研究模型，Apache 2.0 | [allenai/wildguard](https://huggingface.co/allenai/wildguard) |
| Azure AI Content Safety | 微软云端内容安全服务，含 Prompt Shields（区分用户提示攻击与文档攻击） | 活跃维护 | [Microsoft](https://azure.microsoft.com/en-us/products/ai-services/ai-content-safety) |
| AWS Bedrock Guardrails | AWS 云端护栏服务，含内容过滤、PII 与 prompt attack detection；提示攻击过滤不评估工具结果 | 活跃维护 | [AWS](https://aws.amazon.com/bedrock/guardrails/) |
| Google Cloud Model Armor | Google Cloud 运行时防护服务，筛查提示、响应与 agent 交互；按单轮检查，不解码编码内容 | 活跃维护 | [Google Cloud](https://cloud.google.com/security/products/model-armor) |
| Rebuff | 提示注入检测与防御框架 | 已归档 | [protectai/rebuff](https://github.com/protectai/rebuff) |

### 内容审核

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| OpenAI Moderation API | 内容审核 API | 活跃维护 | [OpenAI 文档](https://developers.openai.com/api/docs/guides/moderation) |
| Perspective API | Google 的毒性检测 API | 活跃维护 | [Perspective API](https://perspectiveapi.com/) |
| Azure AI Content Safety | 微软内容安全服务 | 活跃维护 | [Microsoft](https://azure.microsoft.com/en-us/products/ai-services/ai-content-safety) |

### 隐私保护

| 工具名称 | 描述 | 状态 | 链接 |
|----------|------|------|------|
| Presidio | PII 检测和脱敏工具，源自微软，现已移交社区治理的 Data Privacy Stack 组织 | 活跃维护 | [data-privacy-stack/presidio](https://github.com/data-privacy-stack/presidio) |
| PySyft | 隐私保护机器学习库 | 维护中 | [OpenMined/PySyft](https://github.com/OpenMined/PySyft) |
| Opacus | PyTorch 差分隐私库 | 活跃维护 | [meta-pytorch/opacus](https://github.com/meta-pytorch/opacus) |

## 智能体安全工具（按架构位置）

分类与位置对应 [14.5 节](../14_agent_practice/14.5_security_panorama.md)的参考架构图；每类工具保证的性质、文档写明的边界与维护状态见 [13.5](../13_agent_architecture/13.5_tooling_selection.md) 节，本节只列入口。

| 类别 | 图 14-2 中的位置 | 保证的性质 | 代表工具 |
|------|--------|------------|----------|
| 策略引擎 | 第 4 步（策略网关） | 确定性：每次工具调用按规则放行或拒绝 | [OPA](https://github.com/open-policy-agent/opa)、[Cedar](https://github.com/cedar-policy/cedar)、[OpenFGA](https://github.com/openfga/openfga) |
| 护栏框架 | 第 4 步的风险分、第 12 步的出口检测（图中未单列） | 概率性：检测可疑输入输出 | 见上文「防护框架」与「守卫模型与注入检测」 |
| LLM 与智能体网关 | 第 4、7 步的执行点与工具注册表 | 确定性：统一入口、凭据集中、配额与审计 | [LiteLLM](https://github.com/BerriAI/litellm)、Kong AI Gateway、Cloudflare AI Gateway、[agentgateway](https://github.com/agentgateway/agentgateway)、[IBM ContextForge](https://github.com/IBM/mcp-context-forge)、[Docker MCP Gateway](https://github.com/docker/mcp-gateway) |
| MCP 供应链扫描 | 供应链准入 | 概率性：发现已知模式 | [Snyk Agent Scan](https://github.com/snyk/agent-scan)（原 mcp-scan）、[MCP Registry](https://registry.modelcontextprotocol.io/)（预览，不做代码扫描） |
| 执行沙箱 | 第 6 步 | 确定性：进程能触及什么 | [Anthropic sandbox-runtime](https://github.com/anthropics/sandbox-runtime)、[OpenAI Codex 沙箱](https://github.com/openai/codex)、[gVisor](https://gvisor.dev/)、[Firecracker](https://firecracker-microvm.github.io/)、[E2B](https://e2b.dev/)、[Modal Sandboxes](https://modal.com/docs/guide/sandboxes) |
| 身份与凭据 | 第 1、7 步 | 确定性：令牌的范围与受众 | [SPIFFE/SPIRE](https://spiffe.io/)、[Keycloak](https://www.keycloak.org/)、Auth0 for AI Agents、Okta、[HashiCorp Vault](https://developer.hashicorp.com/vault)、1Password |
| 可观测性 | 会话事件日志 | 事后：追踪与审计 | [OpenTelemetry 生成式 AI 语义约定](https://opentelemetry.io/docs/specs/semconv/gen-ai/)（开发中）、[Langfuse](https://github.com/langfuse/langfuse)、[Arize Phoenix](https://github.com/Arize-ai/phoenix)、LangSmith |
| 评测与红队 | 验证阶段 | 发现问题，不防止问题 | 见上文「红队测试与安全评估」 |

## 安全框架与指南

### 标准与框架

| 名称 | 描述 | 链接 |
|------|------|------|
| OWASP LLM Top 10 (2026) | LLM 十大安全风险 | [OWASP](https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/) |
| NIST AI RMF | AI 风险管理框架 | [NIST](https://www.nist.gov/itl/ai-risk-management-framework) |
| NIST AI 600-1 (GenAI Profile) | 生成式 AI 风险管理配置文件 | [NIST](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) |
| MITRE ATLAS | AI 对抗威胁矩阵 | [MITRE ATLAS](https://atlas.mitre.org/) |
| ISO/IEC 42001 | AI 管理体系标准 | [ISO](https://www.iso.org/standard/81230.html) |
| CycloneDX ML-BOM | 模型与数据集的机读物料清单格式（1.5 版起），配套 OWASP《Authoritative Guide to AI/ML-BOM》 | [CycloneDX](https://cyclonedx.org/guides/OWASP_CycloneDX-Authoritative-Guide-to-AI-ML-BOM-en.pdf) |

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
| Prompt Engineering | DeepLearning.AI | 提示工程最佳实践 | [DeepLearning.AI](https://www.deeplearning.ai/courses/chatgpt-prompt-eng) |

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

## 通用可观测性与运营基础设施

以下为通用基础设施，不针对 LLM 或智能体；智能体追踪的专用工具见上文「智能体安全工具」中的可观测性一行。

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

### 模型工件安全

| 工具 | 功能 | 状态 | 链接 |
|------|------|------|------|
| ModelScan（Protect AI） | 扫描模型文件中的反序列化攻击载荷 | 活跃维护 | [protectai/modelscan](https://github.com/protectai/modelscan) |
| picklescan | 针对 pickle 文件的恶意导入扫描 | 活跃维护 | [mmaitre314/picklescan](https://github.com/mmaitre314/picklescan) |
| ML Guard | ML 流水线安全与合规扫描器：pickle、safetensors、ONNX、密钥、CVE 五类扫描，输出 SARIF、CycloneDX SBOM 与合规报告 | v0.1.0 首个公开版，Apache 2.0 | [ml-guard/ml-guard](https://github.com/ml-guard/ml-guard) |
| model-signing（Sigstore / OpenSSF） | 为模型目录生成逐文件摘要清单并签名验签，支持 Sigstore 无密钥签名、传统密钥与证书 | 1.1.1，活跃维护 | [sigstore/model-transparency](https://github.com/sigstore/model-transparency) |

### 数据安全

| 工具 | 功能 |
|------|------|
| Great Expectations | 数据质量验证 |
| Apache Atlas | 数据治理 |

## 核心工具与 OWASP/生命周期映射索引（速查字典）

下表按开发生命周期阶段列出应对的 OWASP Top 10 风险、推荐工具与章节指引，供安全评审人员与研发工程师速查：

| 开发生命周期阶段 | 防御的核心 OWASP 风险 | 推荐部署的开源工具/基线 | 典型落地场景与章节指引 |
|------------------|-----------------------|-------------------------|------------------------|
| **模型训练/微调** | LLM04（供应链风险）<br>LLM05（数据与模型投毒）| Great Expectations<br>ModelScan / picklescan<br>model-signing | 数据清洗质量强制校验、第三方模型权重扫描与签名验签（第 6、8 章） |
| **应用架构设计** | LLM03（过度自主权）<br>LLM08（隐藏上下文暴露）| OPA / Cedar / OpenFGA（策略网关）<br>Google SAIF（框架） | 会话分层架构设计、工具调用在模型外做确定性授权、人工审核（HITL）审批流预发设计（第 8、13 章） |
| **知识检索 (RAG)** | LLM09（向量与嵌入弱点）<br>LLM07（错误信息）| 向量库自带的认证、租户隔离与前置权限过滤（Qdrant、Milvus、Weaviate 等）<br>SafeRAG 基准 | 摄取前校验与来源标记、检索前按租户与权限过滤、定期用基准加自适应攻击测试（[第 7 章](../07_rag_security/README.md)） |
| **网关边界拦截** | LLM01（提示注入）<br>LLM06（无边界消耗）| Meta Llama Prompt Guard 2 / Llama Guard 4<br>NeMo Guardrails | 部署于最外层 API 代理作为低延迟分类器探测注入与越狱，并实施 Token 熔断限流（第 4、9 章） |
| **输出校验与脱敏**| LLM02（敏感信息泄露）<br>LLM10（输出处理不当）| Presidio<br>Guardrails AI | 双向 PII 实体检测与掩码还原，强制输出转为受控 Schema 并严格阻断执行链（[第 9 章](../09_io_protection/README.md)） |
| **CI/CD 安全门禁** | LLM01（注入绕过）<br>通用安全性回归 | promptfoo<br>Garak<br>HarmBench<br>AgentDojo | 迭代上线前构建自动化对抗评估，将最新漏洞固化为集成测试中的强制拦截门禁（第 10、13 章） |

---

*状态说明：开源工具、研究项目与云服务的状态可能随时变化，建议在选型前检查项目的最近更新日期、官方说明和社区活跃度。*
