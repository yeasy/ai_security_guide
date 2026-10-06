# 附录 A：术语表

本附录收录 LLM 安全领域的常用术语及其解释。

## A

**Adversarial Example（对抗样本）**
经过精心设计的输入，对人类来说与正常输入无异，但会导致 AI 系统产生错误输出。

**Adaptive Attack（自适应攻击）**
攻击者了解防御的设计并针对它调整策略的攻击。评估防御时应以自适应攻击为准；仅在固定攻击样本上测得的低攻击成功率不能说明真实鲁棒性。

**智能体（Agent）**
具备自主决策和操作执行能力的 AI 系统，可以规划任务、调用工具、与环境交互。

**Agent-to-Agent Protocol（A2A 协议）**
智能体间的通信协议，如 Google 提出的 A2A，引入新的信任边界和攻击面。

**AI Control（AI 控制）**
在不假设模型已对齐的前提下设计监督与约束机制的研究方向。其评估方法是让红队扮演有意规避监督的模型，检验可信监控、可信编辑、重采样等协议是否仍然有效。

**Alignment（对齐）**
使 AI 系统的行为与人类意图和价值观保持一致的技术和过程。

**API Key**
用于验证 API 调用者身份的密钥。

**Approved Scalar（获准标量）**
隔离模型交回的结构化结果中，取值限定在有限集合（如枚举）之内的字段，例如一封邮件被归入哪一类。经代码校验后可交给规划模型，来源标记照旧保留（[13.2.2](../13_agent_architecture/13.2_architectural_defenses.md)、[14.5](../14_agent_practice/14.5_security_panorama.md)）。

## B

**Backdoor Attack（后门攻击）**
在模型中植入隐藏触发机制，正常使用时正常工作，特定触发条件下执行恶意行为。

**Base64**
一种将二进制数据编码为文本的方式，有时被用于混淆恶意内容。

## C

**CaMeL**
一种提示注入的架构级防御：由特权模型把用户请求翻译成程序，自定义解释器在执行时跟踪每个值的来源，并在工具调用处执行安全策略，使不可信数据无法改变控制流、敏感数据无法流向未授权出口。

**CAS Principle（CAS 原理）**
笔者提出的智能体安全不可能原理：通用性（任务范围不预先限定）、自主性（有后果的决定只靠读到不可信内容之前写定的规则放行）、安全性（不可信内容引发的后果不超出可信方核准的范围，可信方是规则或人在运行中的确认，由模型之外的机制强制执行）三者不可兼得。限定任务的专用智能体可以既安全又自主；通用智能体要安全，就得由人确认；通用而又自主，只剩概率性的防护（[第十一章](../11_agent_foundations/README.md)）。

**Confused Deputy（混淆代理）**
高权限的一方在替他人办事时，没有核对请求最初代表谁、是否在其授权范围内，从而被低权限的一方借用了权限。常见于 MCP 代理服务与多智能体委托。

**Constitutional AI**
Anthropic 提出的对齐方法，使用一套“宪法”（规则集）来指导模型行为。

**Context Engineering（上下文工程）**
系统性地管理 LLM 上下文窗口中的信息组织、优先级和安全边界的工程实践。

**Context Window（上下文窗口）**
LLM 一次能处理的最大 Token 数量。

## D

**DAN（Do Anything Now）**
早期著名的越狱技术，通过角色扮演让模型突破限制。

**Data Poisoning（数据投毒）**
通过在训练数据中注入恶意样本来影响模型行为的攻击。

**Deceptive Alignment（欺骗性对齐）**
模型在评估/测试期间表现出对齐行为，但在部署后偏离对齐目标的假设性风险。

**Defense in Depth（纵深防御）**
叠加相互独立的多层防护，使单层失效不致造成损失。概率性的层只降低频率，后果的上界由确定性的一层给出。

**Differential Privacy（差分隐私）**
一种数学框架，用于在保护个人隐私的同时进行数据分析。

**Delegation（委托授权）**
主体授权另一主体在限定范围内代表自己行动。与冒充不同，委托令牌同时记录被代表者和实际行动者；每经过一级委托，权限只能收窄。

**DPO（Direct Preference Optimization）**
一种直接优化模型偏好的对齐方法。

**Dual LLM Pattern（双 LLM 模式）**
把智能体拆成两个模型实例的设计模式：特权模型只接触可信输入并负责规划与调用工具，隔离模型处理不可信内容但没有任何工具，两者之间由普通程序以符号变量传递结果。

**Dynamic Taint Analysis（动态污点分析）**
把来自不可信来源的数据标为污点、跟踪其传播，污点到达敏感汇点时判定的技术，源自 2005 年的 TaintCheck。用于智能体时，模型读过带污点的输入，输出就整体带污点；推广到模块，读过不可信数据的模块此后的全部输出（包括写入的记忆与文件）都按不可信处理，对应 Biba 的主体低水位策略（[13.2.4](../13_agent_architecture/13.2_architectural_defenses.md)）。

## E

**Embedding（嵌入）**
将文本等数据转换为数值向量表示的方法。

**EU AI Act（欧盟人工智能法案）**
欧盟于 2024 年通过并分阶段生效的 AI 监管法规，对高风险 AI 与通用 AI（GPAI）提出分层合规要求。

**Extraction Contract（抽取契约）**
先于原文锁定的字段清单，规定隔离模型抽取哪些字段及其类型与取值范围，内容无权修改；按契约抽出的字段称契约字段（[14.5](../14_agent_practice/14.5_security_panorama.md)）。

## F

**Fine-tuning（微调）**
在预训练模型基础上使用特定数据进行额外训练。

**Function Calling（函数调用）**
LLM 调用外部工具和 API 的能力。

## G

**Gate（闸）**
模型之外、决定一个动作能否执行的检查点，可以是代码规则，也可以是由代码强制的人工确认。检测器、护栏和第二个模型只降低频率，不是闸（[第十一章](../11_agent_foundations/README.md)、[14.5](../14_agent_practice/14.5_security_panorama.md)）。

**GCG（Greedy Coordinate Gradient）**
一种通过梯度优化生成对抗性后缀的攻击方法。

**GPAI（General-Purpose AI，通用 AI）**
具备广泛适用能力、可被下游系统复用的基础 AI 模型或系统类别，EU AI Act 对其设置了专门义务。

**Guardrails（护栏）**
检测并拦截可疑输入、输出或工具调用的组件。本书所说的护栏多指基于分类器或模型的检测，属概率性防御：只降低频率，不构成边界（[13.5.2](../13_agent_architecture/13.5_tooling_selection.md)）；用代码写定的规则校验（如收件人白名单）是确定性的，属于闸。

## H

**Hallucination（幻觉）**
模型生成看似合理但实际不正确或虚构的内容。

**HITL（Human-in-the-Loop，人工审核）**
在 AI 决策或输出流程中引入人工审核/确认环节，对高风险或不可逆动作设置人工把关。本书统一译为「人工审核（HITL）」；针对具体动作的确认称人工确认。按 CAS 原理，读到不可信内容之后有人工确认，就不再是自主的。

## I

**Indirect Prompt Injection（间接提示注入）**
恶意指令隐藏在外部数据源中，当 LLM 处理这些数据时被触发。

## J

**Information Flow Control（信息流控制）**
为数据打上机密性与完整性标签，并在数据流动时确定性地执行策略的安全机制。用于智能体时，可保证低完整性数据不决定高影响动作、高机密性数据不流向低权限出口。

**Jailbreak（越狱）**
绕过 LLM 安全对齐机制，使其生成被禁止内容的攻击技术。

## L

**Lethal Trifecta（致命三要素）**
访问私有数据、接触不可信内容、具备对外通信能力这三项的组合。智能体同时具备三项时，攻击者可以通过注入诱使它窃取数据。

**LLM（Large Language Model，大语言模型）**
基于大规模数据训练的语言模型，具备强大的自然语言理解和生成能力。

**LoRA（Low-Rank Adaptation）**
一种高效的模型微调方法。

## M

**MCP（Model Context Protocol）**
Anthropic 提出的标准化协议，用于连接 LLM 与外部数据源和工具。

**Membership Inference（成员推理）**
判断特定数据点是否被用于训练模型的攻击技术。

**MoE（Mixture of Experts）**
一种模型架构，使用多个专家模块处理不同类型的输入。

**Multimodal LLM（多模态大语言模型）**
能够同时处理文本、图像、音频等多种输入模态的大语言模型，能力更广但也引入了跨模态注入等新的安全威胁面。

## N

**NER（Named Entity Recognition，命名实体识别）**
识别文本中的人名、地名等特定实体的技术。

**NIST AI 600-1（GenAI Profile）**
NIST 针对生成式 AI 场景发布的 AI RMF 配置文件，用于将治理、映射、测量、管理原则具体化到 GenAI 风险控制。

## O

**Opaque Value（不透明值）**
由代码保管在值存储中、模型看不到内容、只能按名字引用的值，例如抽不成字段的自由文本；由代码代填进参数，或交给答复模型阅读（[14.5](../14_agent_practice/14.5_security_panorama.md)）。

**OWASP LLM Top 10**
OWASP 发布的 LLM 应用十大安全风险清单；条目会迭代更新，实践中应以官方最新版本为准。

**OWASP Agentic Top 10（ASI01–ASI10）**
OWASP 智能体安全倡议（Agentic Security Initiative）发布的智能体应用十大风险清单，正式名称为 *OWASP Top 10 For Agentic Applications 2026*。与 OWASP LLM Top 10 **并行存在而非替代**：LLM Top 10 面向模型驱动的应用，智能体十大风险面向会规划、会行动、会跨系统调用的智能体。对照表见[附录 D](D_owasp_agentic_crosswalk.md)。

## P

**PII（Personally Identifiable Information，个人身份信息）**
可用于识别个人身份的信息，如姓名、身份证号等。

**Pre-training（预训练）**
在大规模数据上训练模型的初始阶段。

**Prompt Injection（提示注入）**
通过恶意输入改变 LLM 行为的攻击技术。

## Q

**Quantization（量化）**
将模型参数从高精度（如 FP32）转换为低精度（如 INT8/INT4）的优化技术，用于减少模型体积和加速推理，但可能改变模型的安全行为特性。

## R

**RAG（Retrieval-Augmented Generation，检索增强生成）**
结合外部知识检索来增强 LLM 生成能力的技术。

**Reasoning Model（推理模型）**
具备链式推理能力的模型（如 OpenAI o 系列、DeepSeek-R1），通过显式推理步骤提升复杂问题求解能力，但推理过程也可能被攻击者利用。

**Red Team（红队）**
模拟攻击者进行安全测试的专业团队。

**RLHF（Reinforcement Learning from Human Feedback）**
基于人类反馈的强化学习，用于对齐 LLM 行为。

**Rule of Two（Agents Rule of Two）**
Meta 提出的智能体安全设计原则：单个会话内，智能体最多同时满足“处理不可信输入、访问敏感系统或私有数据、改变状态或对外通信”三项中的两项；三项都需要时，Meta 要求不得自主运行，须有人工确认或其他可靠验证；按本书 CAS 原理的定义，只靠确定性校验放行仍属自主，代价是限定任务。它只针对提示注入的最高影响后果（[13.1](../13_agent_architecture/13.1_agents_rule_of_two.md)）。

## S

**Sandbox（沙箱）**
在操作系统或虚拟化层面限制进程可访问的文件、网络与系统资源的隔离环境。对智能体而言，有效的沙箱需要同时隔离文件系统与网络，并把凭据留在沙箱之外。

**SBOM（Software Bill of Materials，软件物料清单）**
记录软件组件构成的清单。

**SDL（Security Development Lifecycle，安全开发生命周期）**
将安全融入软件开发全过程的方法论。

**SFT（Supervised Fine-Tuning，监督微调）**
使用标注数据对模型进行微调的方法。

**SIEM（Security Information and Event Management）**
安全信息和事件管理系统。

**Slopsquatting（幻觉包抢注）**
攻击者抢先注册代码生成模型经常幻觉出的、原本并不存在的软件包名，等待开发者或智能体按模型建议安装的供应链攻击。

**Supply Chain Risk（供应链风险）**
在 AI 模型的开发、训练、部署全生命周期中，由第三方依赖、数据源、预训练权重等引入的安全威胁。

**System Prompt（系统提示）**
定义 LLM 角色和行为规则的配置提示。

## T

**Tool Poisoning（工具投毒）**
在工具的描述或参数说明中嵌入对用户不可见、对模型可见的指令，诱导模型在调用时执行额外的恶意动作。上线后才修改描述的变体称为 Rug Pull。

**Token（令牌）**
LLM 处理文本的基本单位，通常是词或子词。

**Transformer**
一种神经网络架构，是现代 LLM 的基础。

## U

**Unreliable Executor Model（不可靠执行者模型）**
本书从系统角度归纳的智能体安全模型：模型会随机出错，也会被操纵，两者后果相同，所以模型只提出请求，会造成损失的动作一律经模型之外的闸决定，即“概率的部分出主意，确定的部分拿主意”（[第十一章](../11_agent_foundations/README.md)）。

## V

**Vector Database（向量数据库）**
专门存储和检索向量数据的数据库，常用于 RAG 系统。

## W

**Watermark（水印）**
嵌入内容中可追踪的标记，用于证明来源或所有权。

## Z

**Zero Trust（零信任）**
不预设信任任何组件的安全架构原则。
