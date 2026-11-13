"""
Interactive CLI Runner for Enterprise AI Video Workbench (Phase 1 MVP).
Demonstrates end-to-end pipeline execution with live logs, status transitions,
and FinOps balance accounting.
"""

import sys
import io
import os
from pathlib import Path

# Force UTF-8 stdout
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from workbench.orchestrator import WorkbenchOrchestrator
from workbench.mock_gateway import Mock302AIGateway


def run_demo():
    console = Console()
    console.print(Panel.fit(
        "[bold cyan]企业级AI短视频制作工作台 (Phase 1 MVP)[/bold cyan]\n"
        "[dim]基于首尾帧空间锁定与事前算力熔断的工业化管道[/dim]",
        border_style="cyan"
    ))

    # 初始化仿真网关（具备完整计费与多模型生命周期）
    mock_api = Mock302AIGateway(initial_balance=5.0)
    orchestrator = WorkbenchOrchestrator(api_client=mock_api, user_balance=5.0)

    # 1. 创意输入
    screenplay = "上古祭坛破晓，饕餮自浓雾中昂首苏醒，金色晨曦刺破苍穹，巨兽发出震天长啸。"
    console.print(f"\n[bold yellow]步骤 1: 创意剧本输入[/bold yellow]\n> {screenplay}")
    project = orchestrator.create_project(title="饕餮神话·破晓篇", screenplay_raw=screenplay)

    # 2. 智能分镜拆解
    console.print("\n[bold yellow]步骤 2: F-01 智能分镜拆解 (Gemini 3.8 Flash)[/bold yellow]")
    project = orchestrator.step_decompose(project)
    console.print(f"[green][SUCCESS] 成功拆解出 {len(project.shots)} 个分镜镜头[/green]")
    for s in project.shots:
        console.print(f"  - 镜号 #{s.sequence_index}: {s.scene_summary} (运镜: {s.camera_motion})")

    # 3. 算力熔断与双关键帧生成
    console.print("\n[bold yellow]步骤 3: F-05 事前算力核验 + F-02 双关键帧生成[/bold yellow]")
    project = orchestrator.step_generate_keyframes_batch(project)
    shot_1 = project.shots[0]
    console.print(f"[green][SUCCESS] FinOps 熔断校验通过 (账户余额: ${mock_api.get_balance():.4f})[/green]")
    console.print(f"[green][SUCCESS] 镜号 #1 生成起幅 2 张候选 + 落幅 2 张候选[/green]")
    for cand in shot_1.start_candidates + shot_1.end_candidates:
        console.print(f"  - [{cand.frame_type.value} Slot {cand.candidate_slot.value}] URL: {cand.image_url} (成本: ${cand.cost_usd:.4f})")

    # 4. 人工评审与局部打回修复
    console.print("\n[bold yellow]步骤 4: F-03 人工评审与局部缺陷涂抹打回 (Inpainting)[/bold yellow]")
    console.print("  [dim]编导发现落幅候选 A 的右角略有断裂，使用画布画笔涂抹缺陷生成掩码，提交重绘要求...[/dim]")
    shot_1 = orchestrator.step_inpaint_shot(
        shot=shot_1,
        candidate_id=shot_1.end_candidates[0].id,
        mask_url="https://mock-oss.302.ai/masks/defect_mask_01.png",
        feedback_prompt="将断裂处修复为威严黑金巨角，补齐金色微光脉络"
    )
    console.print(f"[green][SUCCESS] 局部 Inpainting 修复完成 (重绘版本: v{shot_1.inpaint_retry_count})[/green]")
    console.print(f"  - 修复后新候选帧: {shot_1.selected_end_frame_id}")

    # 5. 核准确认与首尾帧视频合成
    console.print("\n[bold yellow]步骤 5: F-04 首尾帧插值视频渲染 (Kling I2V)[/bold yellow]")
    console.print("  [dim]编导核准通过起幅 A 与修复后的落幅 A+，触发首尾帧插值异步渲染任务...[/dim]")
    ready_shot = orchestrator.step_approve_and_synthesize(
        shot=shot_1,
        selected_start_id=shot_1.start_candidates[0].id,
        selected_end_id=shot_1.selected_end_frame_id
    )
    console.print(f"[bold green][SUCCESS] 视频合成渲染就绪! 状态: {ready_shot.video_status.value}[/bold green]")
    console.print(f"  - 最终成品视频 URL: [cyan]{ready_shot.video_url}[/cyan]")

    # 6. FinOps 账本与指标审计报告
    table = Table(title="\n[FinOps 算力账本与单镜成本审计]")
    table.add_column("工序阶段", style="cyan")
    table.add_column("调用模型", style="magenta")
    table.add_column("任务类型", style="white")
    table.add_column("花费 (USD)", style="green")

    for entry in orchestrator.finops.ledger:
        if entry.shot_id == shot_1.id:
            table.add_row("Shot #1", entry.model_name, entry.task_type, f"${entry.cost_usd:.4f}")

    shot_1_cost = orchestrator.finops.get_shot_accumulated_cost(shot_1.id)
    table.add_row("---", "---", "[bold]镜头 1 实际耗费[/bold]", f"[bold green]${shot_1_cost:.4f}[/bold green]")
    console.print(table)

    ceiling = 0.35
    if shot_1_cost <= ceiling:
        console.print(f"\n[bold green][PASSED] 业务闭环与质量门禁验收通过! 镜头 1 实际成本 ${shot_1_cost:.4f} <= PRD 上限 ${ceiling:.2f}[/bold green]\n")
    else:
        console.print(f"\n[bold red][FAILED] 成本超标: ${shot_1_cost:.4f} > ${ceiling:.2f}[/bold red]\n")


if __name__ == "__main__":
    run_demo()
