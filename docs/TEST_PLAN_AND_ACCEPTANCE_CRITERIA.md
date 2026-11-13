# 企业级AI短视频制作工作台（Phase 1 MVP）验收标准与测试计划说明书

- **文档编号**：QA-TESTPLAN-MVP-001
- **角色标准**：PETL Principal Quality Engineer (微软/谷歌高可靠性工程规范)
- **关联架构**：[AI短视频制作工作台_第一阶段架构设计.md](file:///c:/Users/33046/Desktop/short%20video/AI短视频制作工作台_第一阶段架构设计.md)
- **关联需求**：[AI短视频制作工作台_第一阶段PRD.md](file:///c:/Users/33046/Desktop/short%20video/AI短视频制作工作台_第一阶段PRD.md)
- **状态**：`DECIDED` (执行基准)

---

## 1. 质量风险图谱与测试策略 (Quality Risk Map & Strategy)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 质量风险矩阵与防护层级                                   │
├────────────────────┬──────────────────────┬─────────────┬──────────────────────────────┤
│ 风险域 (Risk Domain)│ 潜在危害             │ 严重等级    │ 防御与验证手段               │
├────────────────────┼──────────────────────┼─────────────┼──────────────────────────────┤
│ **FinOps 资金风险**│ 盲目批处理导致余额击穿 │ P0 (Critical)│ 120% 余额熔断拦截、账本双记账│
│ **视频形变幻觉**   │ 人体肢体异化、镜头漂移 │ P0 (Critical)│ 首尾双帧物理锁定 (I2V)       │
│ **返工死循环**     │ 编导无限局部打回重做   │ P1 (High)   │ 单镜 Inpainting ≤3 次熔断限制│
│ **网络与接口重试** │ 异步长轮询导致重复扣费 │ P1 (High)   │ 强幂等键 (Idempotency Key)   │
│ **提示词结构丢失** │ LLM 输出杂乱不可解析   │ P2 (Medium) │ Pydantic 严格 Schema 强校验  │
└────────────────────┴──────────────────────┴─────────────┴──────────────────────────────┘
```

---

## 2. 严格验收指标矩阵 (Strict Acceptance Criteria)

| 验收编号 | 验收项 | 测量方法与计算公式 | 硬性通过门槛 (Pass Threshold) | 状态 |
| :--- | :--- | :--- | :--- | :---: |
| **AC-01** | **FinOps 余额熔断拦截率** | 模拟账户可用余额低于 $\text{Cost}_{\text{est}} \times 120\%$ 时发起批处理 | **$100\%$ 物理拦截**，抛出 `InsufficientBalanceError`，零外部 API 流量外发 | `VERIFIED` |
| **AC-02** | **单镜头基线成本** | 完整生成一个具备 A/B 候选、0.5次局部重做与首尾帧插值的镜头 | **$\le \$0.35$** (理论基线 $\$0.2933$) | `VERIFIED` |
| **AC-03** | **局部重做防沉迷熔断** | 同一镜头连续发起局部涂抹 Inpainting 打回 | **第 4 次强制阻断**，抛出 `InpaintingExceededError` | `VERIFIED` |
| **AC-04** | **首尾帧插值输入约束** | 提交未确认落幅或仅有单帧的视频生成请求 | **$100\%$ 拦截**，状态机必须处于 `KEYFRAMES_APPROVED` | `VERIFIED` |
| **AC-05** | **接口异步幂等性** | 相同镜头参数在 100ms 内发起 5 次并发合成调用 | 仅产生 1 笔真实扣费与 1 个外部任务，其余返回相同 `job_id` | `VERIFIED` |
| **AC-06** | **分镜 Schema 合规性** | 针对自然语言剧本提取出的镜头字段做 Pydantic 校验 | **$100\%$ 字段合规**，镜头包含运镜、起落幅提示词与时长 | `VERIFIED` |

---

## 3. 测试分级与测试用例集 (Test Traceability Matrix)

### 3.1 单元测试套件 (Unit Tests)
- `test_finops_cost_calculation`: 验证不同镜头数量下的 Token、图像与视频插值成本测算精度。
- `test_finops_breaker_trip`: 验证可用余额处于 119% 阈值时触发熔断，121% 阈值时放行。
- `test_shot_schema_validation`: 验证合法与残缺 JSON 结构在 Pydantic 实体中的解析与错误捕获。
- `test_inpainting_mask_generation`: 验证 Canvas 坐标点转换二值掩码（纯黑 0 / 纯白 255）的准确性。
- `test_state_machine_transitions`: 验证从 `DRAFT` 到 `READY` 的合法跃迁，拦截非法越级状态跃迁。

### 3.2 集成测试套件 (Integration Tests with Mock Gateway)
- `test_external_api_balance_insufficient`: 模拟 302.AI 接口返回 `err_code: -10004` 时系统的优雅降级与异常通知。
- `test_async_task_polling_and_retry`: 模拟 Kling 接口经历 `processing` -> `processing` -> `success` 的退避轮询与超时处理。
- `test_idempotency_deduplication`: 模拟重复任务提交，验证 Redis/本地幂等存储的冲突消除。

### 3.3 端到端业务闭环测试 (E2E Golden & Negative Pipeline)
- **TC-E2E-01 (Golden Path)**:
  1. 输入《山海经·饕餮破晓》故事梗概；
  2. 自动拆解出 3 个结构化分镜；
  3. 为 Shot 1 生成起幅 A/B 与落幅 A/B；
  4. 模拟人工评审，选中起幅 A，对落幅 B 进行 1 次局部涂抹打回修复；
  5. 确认起幅 A 与修复后落幅 B+；
  6. 通过 FinOps 熔断检查，下发首尾帧视频合成；
  7. 视频就绪落盘，验证全流程账本总耗费 $\le \$0.35$。
- **TC-E2E-02 (Negative Path - 余额不足拦截)**:
  1. 账户余额设为 $\$0.10$；
  2. 提交任务预估开销为 $\$0.30$；
  3. 验证任务在进入生成队列前被阻断，未调用生图与生视频 API。

---

## 4. 退出标准 (Exit Criteria)
1. 单元测试与集成测试通过率 $100\%$；
2. 代码覆盖率核心业务逻辑 $\ge 90\%$；
3. 端到端 TC-E2E-01 与 TC-E2E-02 自动化执行通过并出具证据日志。
