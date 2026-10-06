# 第七章 RAG 与知识库安全

检索增强生成（RAG）把外部知识库接到模型上：先按用户问题从知识库检索相关片段，再把片段连同问题一起交给模型生成答案。它是企业把私有数据用起来的主要方式，也是不可信内容进入模型上下文的第一扇门——谁能向知识库写入内容，谁就能向模型下指令；谁能影响检索排序，谁就能决定模型看到什么。

本章把 RAG 当作一条流水线来分析：内容如何入库（[7.4](7.4_ingestion_pipeline.md)）、如何存储（[7.5](7.5_vector_database_security.md)）、谁有权检索到什么（[7.6](7.6_retrieval_access_control.md)）、如何被召回（[7.2](7.2_knowledge_base_poisoning.md)、[7.3](7.3_retrieval_manipulation.md)）、如何进入上下文（[7.7](7.7_context_window_attacks.md)），每一环各有攻击与防御，最后用基准来检验（[7.8](7.8_rag_evaluation_best_practices.md)）。

- **[7.1](7.1_rag_architecture.md) RAG 架构与攻击面**：典型架构与各组件对应的攻击面
- **[7.2](7.2_knowledge_base_poisoning.md) 知识库投毒攻击**：少量、靶向、可优化的投毒，从 PoisonedRAG 到单文档、拆分式与触发词后门；防御各自的代价；互联网规模的语料投毒
- **[7.3](7.3_retrieval_manipulation.md) 检索结果操纵**：让恶意内容挤进召回结果，以及检索器层面的对抗
- **[7.4](7.4_ingestion_pipeline.md) 文档摄取管线安全**：解析器漏洞、隐藏文本、多模态注入，以及摄取环节的防护清单
- **[7.5](7.5_vector_database_security.md) 向量数据库与嵌入安全**：嵌入可被反演、向量库的漏洞与默认配置、多租户机制的边界
- **[7.6](7.6_retrieval_access_control.md) 检索时的访问控制**：正文交付前的强制授权、云平台的参考设计、过度共享与混淆代理
- **[7.7](7.7_context_window_attacks.md) 上下文窗口攻击**：穿过检索之后，恶意内容在上下文里做什么；生产系统中的实例
- **[7.8](7.8_rag_evaluation_best_practices.md) 评测与最佳实践**：可用的基准，把链路失败拆成检索、授权、生成各自带分母的可测条件，以及入库、检索、生成三层的防护要点

本章与前后章节的关系：间接提示注入的原理见 [4.3 节](../04_prompt_injection/4.3_indirect_injection.md)，长上下文中的投毒见 [4.6 节](../04_prompt_injection/4.6_long_context_risks.md)；智能体的记忆与检索共用同一套机制，其风险在[第十二章](../12_agent_attack_surface/README.md)继续讨论。

> **⚠️ 道德边界**：本章对知识库投毒与检索操纵的剖析用于让 RAG 系统的建设者识别并修复自身系统的弱点；针对未经授权的他方系统执行类似攻击违反法律与服务条款。完整声明见 [§4 章首道德边界与负责任披露说明](../04_prompt_injection/README.md)。
