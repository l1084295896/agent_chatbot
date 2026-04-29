"""
Agent 工具中间件模块

职责：
1. 工具执行监控（monitor_tool）— 记录工具调用入参、结果、异常
2. 模型调用前日志（log_before_model）— 记录每次模型调用前的状态
3. 动态提示词切换（report_prompt_switch）— 根据运行时上下文动态切换 System Prompt
"""

from langchain.agents.middleware import (
    wrap_tool_call,   # 装饰器：包装工具调用，插入监控逻辑
    before_model,    # 装饰器：在模型调用前执行钩子
    dynamic_prompt,  # 装饰器：动态生成每次模型调用前的提示词
    ModelRequest,
)
from langchain.tools.tool_node import ToolCallRequest
from typing import Callable
from langchain_core.messages import ToolMessage
from langgraph.types import Command
from utils.logger_handler import setup_logger
from langchain.agents import AgentState
from langgraph.runtime import Runtime
from utils.prompt_loader import load_system_prompt, load_report_prompt


@wrap_tool_call
def monitor_tool(
    request: ToolCallRequest,
    # handler 是被包装的原始工具执行器，调用它才会真正执行业务逻辑
    handler: Callable[[ToolCallRequest], ToolMessage | Command],
) -> ToolMessage | Command:
    """
    工具执行的监控装饰器

    工作流程：
    1. 记录入参日志（INFO）
    2. 调用原始 handler 执行工具
    3. 成功后记录成功日志；若工具名为 fill_context_for_report，
       设置 runtime.context["report"] = True，告知后续流程当前为报告生成模式
    4. 若有异常，记录错误日志并向上抛出（不压制异常）

    注意：
    - context["report"] 一旦设为 True，后续所有模型调用都会使用报告专用提示词，
      直至手动重置或重启会话。如果报告生成完毕后 Agent 继续普通对话，
      提示词仍会保持报告模式，需确认业务逻辑是否有配套重置机制
    """
    logger = setup_logger("monitor_tool")
    logger.info(f"[monitor_tool] 执行工具: {request.tool_call['name']}")
    logger.info(f"[monitor_tool] 传入参数: {request.tool_call['args']}")

    try:
        result = handler(request)
        logger.info(f"[monitor_tool] 工具 {request.tool_call['name']} 调用成功，返回类型: {type(result).__name__}")

        # 若当前工具是报告上下文填充，则标记报告模式，供 report_prompt_switch 使用
        if request.tool_call["name"] == "fill_context_for_report":
            request.runtime.context["report"] = True

        return result
    except Exception as e:
        logger.error(
            f"[monitor_tool] 工具 {request.tool_call['name']} 调用失败\n  原因: {str(e)}"
        )
        raise e  # 异常继续抛出，不压制，以便上层处理


@before_model
def log_before_model(
    state: AgentState,  # Agent 当前状态，包含 messages（对话历史）等
    runtime: Runtime,  # 运行时全局上下文
):
    """
    在模型调用前输出日志（仅负责记录，不拦截模型调用流程）

    注意：
    - 此钩子在每次模型调用前都会触发，INFO 日志量较大，建议生产环境设为 WARNING
    - DEBUG 日志打印最后一条消息的完整 content，可能非常长，已做截断保护
    """
    logger = setup_logger("log_before_model")
    logger.info(f"[log_before_model] 即将调用模型，当前带有 {len(state['messages'])} 条消息")

    # 截断过长内容，避免日志刷屏
    last_msg = state["messages"][-1]
    content = str(last_msg.content)
    if len(content) > 200:
        content = content[:200] + "..."
    logger.debug(
        f"[log_before_model] 最新消息 | 类型: {type(last_msg).__name__} | 内容: {content}"
    )
    return None


@dynamic_prompt
def report_prompt_switch(request: ModelRequest):
    """
    动态切换提示词

    每次生成模型提示词前调用，根据运行时上下文 context["report"] 的值
    决定加载普通系统提示词还是报告专用提示词

    工作逻辑：
    - context["report"] == True（由 monitor_tool 的 fill_context_for_report 工具触发）
      → 加载报告专用提示词（load_report_prompt）
    - context["report"] == False（默认）
      → 加载普通系统提示词（load_system_prompt）

    注意：
    - dynamic_prompt 装饰器要求返回的是提示词文件路径字符串，
      load_system_prompt() / load_report_prompt() 应返回路径而非内容
    - 若 prompt_loader 实现有变化，需确保返回值类型与装饰器要求匹配
    """
    is_report = request.runtime.context.get("report", False)
    if is_report:
        return load_report_prompt()   # 报告生成模式 → 报告专用提示词
    return load_system_prompt()       # 普通模式 → 普通系统提示词
