# 附录 A：术语表

本附录收录 LLM 安全领域的常用术语及其解释。

## A

**Adversarial Example（对抗样本）**  
经过精心设计的输入，对人类来说与正常输入无异，但会导致 AI 系统产生错误输出。

**Agent**  
具备自主决策和操作执行能力的 AI 系统，可以规划任务、调用工具、与环境交互。

**Alignment（对齐）**  
使 AI 系统的行为与人类意图和价值观保持一致的技术和过程。

**API Key**  
用于验证 API 调用者身份的密钥。

## B

**Backdoor Attack（后门攻击）**  
在模型中植入隐藏触发机制，正常使用时正常工作，特定触发条件下执行恶意行为。

**Base64**  
一种将二进制数据编码为文本的方式，有时被用于混淆恶意内容。

## C

**Constitutional AI**  
Anthropic 提出的对齐方法，使用一套"宪法"（规则集）来指导模型行为。

**Context Window（上下文窗口）**  
LLM 一次能处理的最大 Token 数量。

## D

**DAN（Do Anything Now）**  
早期著名的越狱技术，通过角色扮演让模型突破限制。

**Data Poisoning（数据投毒）**  
通过在训练数据中注入恶意样本来影响模型行为的攻击。

**Defense in Depth（纵深防御）**  
通过多层独立安全措施确保整体安全的安全策略。

**Differential Privacy（差分隐私）**  
一种数学框架，用于在保护个人隐私的同时进行数据分析。

**DPO（Direct Preference Optimization）**  
一种直接优化模型偏好的对齐方法。

## E

**Embedding（嵌入）**  
将文本等数据转换为数值向量表示的方法。

**EU AI Act（欧盟人工智能法案）**  
欧盟于 2024 年通过并分阶段生效的 AI 监管法规，对高风险 AI 与通用 AI（GPAI）提出分层合规要求。

## F

**Fine-tuning（微调）**  
在预训练模型基础上使用特定数据进行额外训练。

**Function Calling（函数调用）**  
LLM 调用外部工具和 API 的能力。

## G

**GCG（Greedy Coordinate Gradient）**  
一种通过梯度优化生成对抗性后缀的攻击方法。

**Guardrails（护栏）**  
为 LLM 设置的安全边界和限制。

**GPAI（General-Purpose AI，通用 AI）**  
具备广泛适用能力、可被下游系统复用的基础 AI 模型或系统类别，EU AI Act 对其设置了专门义务。

## H

**Hallucination（幻觉）**  
模型生成看似合理但实际不正确或虚构的内容。

## I

**Indirect Prompt Injection（间接提示注入）**  
恶意指令隐藏在外部数据源中，当 LLM 处理这些数据时被触发。

## J

**Jailbreak（越狱）**  
绕过 LLM 安全对齐机制，使其生成被禁止内容的攻击技术。

## L

**LLM（Large Language Model，大语言模型）**  
基于大规模数据训练的语言模型，具备强大的自然语言理解和生成能力。

**LoRA（Low-Rank Adaptation）**  
一种高效的模型微调方法。

## M

**Membership Inference（成员推理）**  
判断特定数据点是否被用于训练模型的攻击技术。

**MoE（Mixture of Experts）**  
一种模型架构，使用多个专家模块处理不同类型的输入。

**MCP（Model Context Protocol）**  
一种用于 LLM 与外部工具/数据源互联的协议规范，用于标准化工具能力声明、调用与上下文传递。

## N

**NER（Named Entity Recognition，命名实体识别）**  
识别文本中的人名、地名等特定实体的技术。

**NIST AI 600-1（GenAI Profile）**  
NIST 针对生成式 AI 场景发布的 AI RMF 配置文件，用于将治理、映射、测量、管理原则具体化到 GenAI 风险控制。

## O

**OWASP LLM Top 10**  
OWASP 发布的 LLM 应用十大安全风险清单；条目会迭代更新，实践中应以官方最新版本为准。

## P

**PII（Personally Identifiable Information，个人身份信息）**  
可用于识别个人身份的信息，如姓名、身份证号等。

**Prompt Injection（提示注入）**  
通过恶意输入改变 LLM 行为的攻击技术。

**Pre-training（预训练）**  
在大规模数据上训练模型的初始阶段。

## R

**RAG（Retrieval-Augmented Generation，检索增强生成）**  
结合外部知识检索来增强 LLM 生成能力的技术。

**Red Team（红队）**  
模拟攻击者进行安全测试的专业团队。

**RLHF（Reinforcement Learning from Human Feedback）**  
基于人类反馈的强化学习，用于对齐 LLM 行为。

## S

**SBOM（Software Bill of Materials，软件物料清单）**  
记录软件组件构成的清单。

**SDL（Security Development Lifecycle，安全开发生命周期）**  
将安全融入软件开发全过程的方法论。

**SFT（Supervised Fine-Tuning，监督微调）**  
使用标注数据对模型进行微调的方法。

**SIEM（Security Information and Event Management）**  
安全信息和事件管理系统。

**System Prompt（系统提示）**  
定义 LLM 角色和行为规则的配置提示。

## T

**Token（令牌）**  
LLM 处理文本的基本单位，通常是词或子词。

**Transformer**  
一种神经网络架构，是现代 LLM 的基础。

## V

**Vector Database（向量数据库）**  
专门存储和检索向量数据的数据库，常用于 RAG 系统。

## W

**Watermark（水印）**  
嵌入内容中可追踪的标记，用于证明来源或所有权。

## Z

**Zero Trust（零信任）**  
不预设信任任何组件的安全架构原则。
