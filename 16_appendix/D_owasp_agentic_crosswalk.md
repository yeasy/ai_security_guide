# 附录 D：OWASP 智能体清单对照

本附录列出 OWASP 两份智能体安全清单的各条目在本书中的对应章节，供读者按清单自查。两份清单侧重点不同，可配合使用：威胁清单（T1–T17）更细，适合逐条自查；ASI Top 10 更概括，适合向管理层说明风险优先级。ASI 官方文档给出了两套编号的对照。

## 智能体安全威胁清单（T1–T17）

OWASP Gen AI Security Project 的 [Agentic AI – Threats and Mitigations](https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/)（附录 C-77）列出 17 项智能体威胁：v1.0（2025-02）包含 T1–T15，v1.1（2025-12）新增 T16、T17，与 ASI Top 10 对齐。

| OWASP 威胁 | 本书覆盖位置 |
|------------|--------------|
| T1 记忆投毒 | [12.3](../12_agent_attack_surface/12.3_memory_poisoning.md)、[12.7.3](../12_agent_attack_surface/12.7_multi_agent_security.md) |
| T2 工具滥用 | [12.1](../12_agent_attack_surface/12.1_tool_security.md) |
| T3 权限提升 | [11.9](../11_agent_foundations/11.9_design_principles.md)、[12.1.6](../12_agent_attack_surface/12.1_tool_security.md)、[12.1.8](../12_agent_attack_surface/12.1_tool_security.md)、[12.7.2](../12_agent_attack_surface/12.7_multi_agent_security.md)、[13.4.3](../13_agent_architecture/13.4_agent_identity.md) |
| T4 资源过载 | [3.1.7](../03_frameworks/3.1_owasp_top10.md)（LLM06）、[11.2](../11_agent_foundations/11.2_threat_model.md) |
| T5 级联幻觉 | [12.7.5](../12_agent_attack_surface/12.7_multi_agent_security.md)、[11.6](../11_agent_foundations/11.6_hallucinated_tool_calls.md) |
| T6 意图篡改与目标操纵 | [15.3.3](../15_governance/15.3_emerging_threats.md)、[15.3.4](../15_governance/15.3_emerging_threats.md)、[14.3](../14_agent_practice/14.3_agentic_misalignment.md) |
| T7 错位与欺骗行为 | [14.3](../14_agent_practice/14.3_agentic_misalignment.md)、[14.2](../14_agent_practice/14.2_sabotage_ai_control.md)、[15.3.12](../15_governance/15.3_emerging_threats.md) |
| T8 抵赖与不可追溯 | [11.8](../11_agent_foundations/11.8_dark_code.md)、[11.10](../11_agent_foundations/11.10_monitoring_audit.md)、[13.1.5](../13_agent_architecture/13.1_agents_rule_of_two.md)、[13.4.3](../13_agent_architecture/13.4_agent_identity.md) |
| T9 身份伪造与冒充 | [12.7.4](../12_agent_attack_surface/12.7_multi_agent_security.md)、[13.4.4](../13_agent_architecture/13.4_agent_identity.md) |
| T10 淹没人工审核 | [12.6](../12_agent_attack_surface/12.6_human_layer.md) |
| T11 意外远程代码执行 | [6.7](../06_data_model_attacks/6.7_malicious_model_artifacts.md)、[12.1.8](../12_agent_attack_surface/12.1_tool_security.md)、[12.1.10](../12_agent_attack_surface/12.1_tool_security.md)、[13.3](../13_agent_architecture/13.3_sandbox_egress.md)、[14.1](../14_agent_practice/14.1_coding_agents.md) |
| T12 智能体通信投毒 | [12.7.2](../12_agent_attack_surface/12.7_multi_agent_security.md)、[12.7.3](../12_agent_attack_surface/12.7_multi_agent_security.md) |
| T13 失控智能体 | [12.7.5](../12_agent_attack_surface/12.7_multi_agent_security.md)、[14.2](../14_agent_practice/14.2_sabotage_ai_control.md) |
| T14 针对多智能体系统的人为攻击 | [12.7.2](../12_agent_attack_surface/12.7_multi_agent_security.md)、[13.1.3](../13_agent_architecture/13.1_agents_rule_of_two.md) |
| T15 人类操纵 | [12.6](../12_agent_attack_surface/12.6_human_layer.md) |
| T16 智能体间协议滥用 | [12.7.4](../12_agent_attack_surface/12.7_multi_agent_security.md)、[12.1.8](../12_agent_attack_surface/12.1_tool_security.md) |
| T17 供应链攻陷 | [12.2.2](../12_agent_attack_surface/12.2_agent_skills.md)、[12.2.3](../12_agent_attack_surface/12.2_agent_skills.md)、[12.2.4](../12_agent_attack_surface/12.2_agent_skills.md)、[12.1.8](../12_agent_attack_surface/12.1_tool_security.md)、[14.1.5](../14_agent_practice/14.1_coding_agents.md) |

## OWASP Top 10 for Agentic Applications 2026（ASI01–ASI10）

OWASP 智能体安全倡议（Agentic Security Initiative）于 2025 年 12 月发布 *OWASP Top 10 For Agentic Applications 2026*（附录 C-94），以 `ASI01`–`ASI10` 列出智能体应用的十大风险。它与 [3.1](../03_frameworks/3.1_owasp_top10.md) 的 LLM Top 10（2026）并行，互不替代。按 LLM Top 10 2026 版的界定，模型作为应用组件时，风险归 LLM 清单；模型成为能调用工具、跨会话保留记忆、在下游引发后果的行动者时，风险归 ASI 清单。下表编号与英文名取自官方 PDF，登记于 [`data/framework_crosswalk.json`](../data/framework_crosswalk.json)，由脚本统一校验。

| 官方标识符与英文名 | 中文表述 | 本书覆盖位置 |
|--------------------|----------|--------------|
| ASI01 Agent Goal Hijack | 智能体目标劫持 | [11.4](../11_agent_foundations/11.4_control_flow_hijacking.md)、[13.1](../13_agent_architecture/13.1_agents_rule_of_two.md)、[13.2](../13_agent_architecture/13.2_architectural_defenses.md)、[4.3](../04_prompt_injection/4.3_indirect_injection.md)、[4.1](../04_prompt_injection/4.1_principles.md) |
| ASI02 Tool Misuse and Exploitation | 工具滥用与利用 | [12.1](../12_agent_attack_surface/12.1_tool_security.md)、[11.6](../11_agent_foundations/11.6_hallucinated_tool_calls.md) |
| ASI03 Identity and Privilege Abuse | 身份与权限滥用 | [13.4](../13_agent_architecture/13.4_agent_identity.md)、[11.9](../11_agent_foundations/11.9_design_principles.md)、[12.1.8](../12_agent_attack_surface/12.1_tool_security.md)、[8.3.4](../08_architecture/8.3_access_control.md)、[8.3.6](../08_architecture/8.3_access_control.md) |
| ASI04 Agentic Supply Chain Vulnerabilities | 智能体供应链漏洞 | [12.2](../12_agent_attack_surface/12.2_agent_skills.md)、[12.1.8](../12_agent_attack_surface/12.1_tool_security.md)、[14.1.4](../14_agent_practice/14.1_coding_agents.md)、[14.1.5](../14_agent_practice/14.1_coding_agents.md)、[8.6.5](../08_architecture/8.6_supply_chain.md)、[6.7](../06_data_model_attacks/6.7_malicious_model_artifacts.md) |
| ASI05 Unexpected Code Execution (RCE) | 意外代码执行（RCE） | [13.3](../13_agent_architecture/13.3_sandbox_egress.md)、[14.1](../14_agent_practice/14.1_coding_agents.md)、[6.7](../06_data_model_attacks/6.7_malicious_model_artifacts.md)、[12.1.10](../12_agent_attack_surface/12.1_tool_security.md) |
| ASI06 Memory & Context Poisoning | 记忆与上下文投毒 | [12.3](../12_agent_attack_surface/12.3_memory_poisoning.md)、[7.2](../07_rag_security/7.2_knowledge_base_poisoning.md)、[12.7.3](../12_agent_attack_surface/12.7_multi_agent_security.md)、[4.6](../04_prompt_injection/4.6_long_context_risks.md) |
| ASI07 Insecure Inter-Agent Communication | 智能体间通信不安全 | [12.7.3](../12_agent_attack_surface/12.7_multi_agent_security.md)、[12.7.4](../12_agent_attack_surface/12.7_multi_agent_security.md)、[12.7.2](../12_agent_attack_surface/12.7_multi_agent_security.md) |
| ASI08 Cascading Failures | 级联失效 | [12.7.5](../12_agent_attack_surface/12.7_multi_agent_security.md)、[12.7.2](../12_agent_attack_surface/12.7_multi_agent_security.md)、[4.3.9](../04_prompt_injection/4.3_indirect_injection.md)、[10.5](../10_operations/10.5_fallback_strategy.md) |
| ASI09 Human-Agent Trust Exploitation | 人机信任利用 | [12.6](../12_agent_attack_surface/12.6_human_layer.md) |
| ASI10 Rogue Agents | 失控智能体 | [12.7.5](../12_agent_attack_surface/12.7_multi_agent_security.md)、[14.3](../14_agent_practice/14.3_agentic_misalignment.md)、[14.2](../14_agent_practice/14.2_sabotage_ai_control.md) |
