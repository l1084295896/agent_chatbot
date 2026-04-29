from langchain_core.tools import tool
from rag.rag_service import RagSummarizeService
import random
import csv
import os
from utils.logger_handler import setup_logger
from utils.path_tool import get_abs_path

rag = RagSummarizeService()
user_ids = ["1234567890", "9876543210", "1111111111", "2222222222", "3333333333"]
month_arr = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
extra_data = {}


def _load_records_csv() -> list[dict]:
    """
    从 ./data/external/records.csv 加载所有记录，并转换为字典列表

    Returns:
        list[dict]: CSV 所有行的字典列表，每行 key 为列名（去除引号）
    """
    logger = setup_logger("records_csv_loader")
    csv_path = get_abs_path("data/external/records.csv")
    # csv_path = os.path.join(".", "data", "external", "records.csv")

    # 检查文件是否存在，若不存在则记录警告并返回空列表
    if not os.path.exists(csv_path):
        logger.warning(f"records.csv 文件不存在，路径: {csv_path}")
        return []

    records = []
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            # csv.DictReader 会自动将每行转换为字典，key 为表头列名
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        logger.info(f"records.csv 加载成功，共 {len(records)} 条记录")
    except Exception as e:
        logger.error(f"加载 records.csv 时发生异常: {str(e)}", exc_info=True)
        return []

    return records


@tool(
    description="获取用户在指定月份的使用记录，以字符串形式返回，未检索到则返回空字符串。参数：user_id 用户ID（如 1001），record_month 目标月份（格式为 YYYY-MM，如 2025-08）"
)
def fetch_external_data(user_id: str, record_month: str) -> str:
    """
    查询指定用户在指定月份的使用记录

    Args:
        user_id: 用户ID，需要与 CSV 中 "用户ID" 列完全匹配
        record_month: 目标月份，格式为 YYYY-MM（如 2025-08），
                      将与 CSV 中 "时间" 列进行完全匹配

    Returns:
        str: 匹配的所有记录拼成的字符串，每条记录用换行符分隔；
             若未检索到任何记录则返回空字符串
    """
    logger = setup_logger("get_user_records")
    logger.info(f"开始查询用户 {user_id} 在 {record_month} 的记录")

    # 调用加载函数获取 CSV 中所有记录
    all_records = _load_records_csv()

    # 若加载失败或文件为空，直接返回空字符串
    if not all_records:
        logger.warning(f"records.csv 无数据或加载失败，直接返回空字符串")
        return ""

    # 筛选出 user_id 和 record_month 同时匹配的行
    matched_records = [
        row
        for row in all_records
        if row.get("用户ID", "").strip() == user_id.strip()
        and row.get("时间", "").strip() == record_month.strip()
    ]

    # 命中有序时记录 INFO 日志
    if matched_records:
        logger.info(
            f"检索到 {len(matched_records)} 条用户 {user_id} 在 {record_month} 的记录"
        )
    else:
        logger.info(f"未检索到用户 {user_id} 在 {record_month} 的任何记录")

    # 将匹配到的记录拼成字符串，每条记录占一行，字段之间用 " | " 分隔
    result = "\n".join(
        f"用户ID: {r['用户ID']} | 特征: {r['特征']} | 清洁效率: {r['清洁效率']} | "
        f"耗材: {r['耗材']} | 对比: {r['对比']} | 时间: {r['时间']}"
        for r in matched_records
    )

    return result


@tool(description="从向量储存中检索参考资料")
def rag_summarize(query: str) -> str:
    return rag.rag_summarize(query)


@tool(description="获取指定城市的天气,以消息字符串的形式返回")
def get_weather(city: str) -> str:
    return f"城市{city}的天气为晴天,气温26摄氏度,空气湿度50%,南风1级"


@tool(description="获取用户所在城市的名称,以纯字符串的形式返回")
def get_user_location() -> str:
    return random.choice(["深圳", "郑州", "北京"])


@tool(description="获取用户的ID,以纯字符串形式返回")
def get_user_id() -> str:
    return random.choice(user_ids)


@tool(description="获取当前月份,以纯字符形式返回")
def get_current_month() -> str:
    return random.choice(month_arr)


@tool(
    description="无入参，无返回值，调用后触发中间件自动为报告生成的场景动态注入上下文信息，为后续提示词切换提供上下文信息"
)
def fill_context_for_report():
    return "fill_context_for_report已调用"


if __name__ == "__main__":
    # 测试 get_user_records 工具函数
    print("=== 测试 get_user_records ===\n")

    # 案例1：正常查询，有匹配结果
    result1 = fetch_external_data.invoke({"user_id": "1001", "record_month": "2025-01"})
    print(f"【用户 1001 / 2025-01】\n{result1}\n")

    # 案例2：正常查询，无匹配结果（用户不存在）
    result2 = fetch_external_data.invoke({"user_id": "9999", "record_month": "2025-01"})
    print(f"【用户 9999 / 2025-01】（不存在）\n{repr(result2)}\n")

    # 案例3：正常查询，无匹配结果（月份不存在）
    result3 = fetch_external_data.invoke({"user_id": "1001", "record_month": "2025-12"})
    print(f"【用户 1001 / 2025-12】（无该月份）\n{repr(result3)}\n")
