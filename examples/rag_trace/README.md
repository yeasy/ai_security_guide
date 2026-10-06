# 实验三：RAG 轨迹与授权

本实验只使用 Python 标准库、合成文档、固定分数和确定性的生成替身。它把检索条件与生成条件分开，验证正文交付前的 ACL、同租户缓存隔离与权限撤销。没有向量库、嵌入模型、真实生成模型、网络请求或延迟测量；这里的分数、输出与比率都是 fixture 的规定或运行结果，不能外推为真实投毒攻击成功率、HNSW 召回率或产品性能。

源码：[`examples/rag_trace/lab.py`](lab.py)；测试：[`tests/test_rag_trace.py`](../../tests/test_rag_trace.py)。

在仓库根目录运行：

```bash
python3 examples/rag_trace/lab.py
python3 -m unittest discover -s tests -p test_rag_trace.py -v
```

第一条命令输出可读 JSON，正常完成时退出码为 0。轨迹依次包含 `raw_candidates` 的 ID、score、rank，可信身份对应的 `allowed_ids`，本次搜索考虑的 `considered_ids`，`top_k_ids`，实际 `context_ids` 与上下文正文，生成替身的 `output`，以及独立 `checks`。所有 ID 与正文均为合成数据；真实系统的候选 ID 与诊断日志也要受访问控制保护。

## 两个条件分别测

`fixed_context` 固定同一份 `poison、clean` 上下文，只改变生成替身策略。`naive` 遇到投毒标记就输出 `TARGET_42`，`isolated` 只读取 fixture 中的事实字段并输出 `FACT_7`。这演示两种定义好的处理规则，不是测试真实模型能否抵抗提示注入。

`attack_trials` 保持投毒正文不变，通过明确给定的分数与目标文档测试三种情形：授权投毒进入上下文、授权投毒排名落后、未授权投毒排名第一却被拒绝。分数不会从正文计算，因此这只能验证排名之后的控制逻辑，不能证明某种 payload 可以改变真实嵌入或排名。

`metrics` 输出每个指标的分子、分母与比率：

| 指标 | 本组固定试次 | 含义 |
|------|-------------|------|
| retrieval_success | 1 / 3 | 目标投毒文档实际进入上下文 |
| conditional_generation_success | 0 / 1 | 在已进入上下文的试次中输出目标答案 |
| total_asr | 0 / 3 | 全部攻击试次中输出目标答案 |
| normal_utility | 1 / 1 | 正常授权查询仍输出 `FACT_7` |

这些值只属于固定 fixture。条件生成分母为零时，`fraction` 返回 `rate: null`，避免把没有暴露机会说成 0% 成功。oracle 对照预先规定的答案与禁止出现的文档 ID，不调用 `authorized()` 来证明它自身正确。

## 候选截断与权限是两件事

`filter_comparison` 去掉授权投毒文档，保留 `private=0.99、clean=0.80、clean2=0.70`，当前用户只能读后两份，`k=2`。`pre` 从授权集合取两个结果；`post` 先截断前两个候选再授权，只留下 `clean`。以授权 top-2 `{clean, clean2}` 为独立参考集合，其召回分别为 2/2 与 1/2，两条路径都拒绝 `private` 正文。

这只是单列表的截断模拟，**没有实现 Azure 的分片合并或 HNSW 遍历**。Azure 的 `preFilter` 在各分片遍历期间过滤，`postFilter` 在各分片候选形成后过滤，`strictPostFilter` 在全局 top-k 后过滤。算法选择会改变召回与计算成本；安全不变量仍是未授权正文不能越过内容交付边界。[Azure 官方过滤机制](https://learn.microsoft.com/en-us/azure/search/vector-search-filters)

## 缓存撤销与变异验收

缓存键为 `(user, tenant, scope, acl_version, query)`，只存 ID。用户 bob 在版本 1 能读取 `private`；撤销其权限并将可信版本更新为 2 后，旧键仍保留，但新请求不得命中它，并且任何命中都按当前 ACL 重新检查。其他用户、租户或 scope 也使用独立键。fixture 把 ACL 更新与版本更新视为同步完成；真实部署还需处理源权限、组成员与索引同步的窗口。[Azure 权限同步说明](https://learn.microsoft.com/en-us/azure/search/search-document-level-access-overview)

移除控制的命令应退出 1，JSON 中的 `passed` 为 false：

```bash
python3 examples/rag_trace/lab.py --remove-control acl
python3 examples/rag_trace/lab.py --remove-control cache_version
```

第一种故障让未授权合成正文进入 context，违反 ACL oracle。第二种故障移除缓存键的版本区分，撤销后命中版本 1 的条目，违反版本与失效 oracle；当前 ACL 复核仍会阻止 `private` 正文，不能把这个结果宣称为已经发生泄露。这两种故障用于证明验收能拒绝失效控制，不能代替真实检索与模型的端到端测试。

机制与评测定义对应 [7.2 投毒双条件](../../07_rag_security/7.2_knowledge_base_poisoning.md)、[7.3 检索链](../../07_rag_security/7.3_retrieval_manipulation.md)、[7.5 缓存边界](../../07_rag_security/7.5_vector_database_security.md)、[7.6 授权边界](../../07_rag_security/7.6_retrieval_access_control.md)和 [7.8 评测](../../07_rag_security/7.8_rag_evaluation_best_practices.md)。双条件来源为 [PoisonedRAG 原论文](https://arxiv.org/html/2402.07867v3)，本实验没有复现论文攻击。
