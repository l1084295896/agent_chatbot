from utils.config_handler import prompt_conf
from utils.path_tool import get_abs_path 
from utils.logger_handler import setup_logger

# try:
#     from utils.config_handler import prompt_conf
#     from utils.path_tool import get_abs_path
#     from utils.logger_handler import setup_logger
# except ImportError:
#     from config_handler import prompt_conf
#     from path_tool import get_abs_path
#     from logger_handler import setup_logger


def load_system_prompt():
    """加载系统提示词

    Returns:
        str: 系统提示词内容
    """
    logger = setup_logger("load_system_prompt")
    try:
        system_prompt_path = get_abs_path(prompt_conf["main_prompt_path"])
    except Exception as e:
        logger.error(
            f"[load_system_prompt] 'main_prompt_path' not found in config"
        )
        raise e
    try:
        with open(system_prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"[load_system_prompt] loaded: {system_prompt_path}")
        return content
    except Exception as e:
        logger.error(f"[load_system_prompt] failed to read file: {str(e)}")
        raise e


def load_rag_prompt():
    """加载 RAG 提示词

    Returns:
        str: RAG 提示词内容
    """
    logger = setup_logger("load_rag_prompt")
    try:
        rag_prompt_path = get_abs_path(prompt_conf["rag_summarize_prompt_path"])
    except Exception as e:
        logger.error(
            f"[load_rag_prompt] 'rag_summarize_prompt_path' not found in config"
        )
        raise e
    try:
        with open(rag_prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"[load_rag_prompt] loaded: {rag_prompt_path}")
        return content
    except Exception as e:
        logger.error(f"[load_rag_prompt] failed to read file: {str(e)}")
        raise e


def load_report_prompt():
    """加载报告提示词

    Returns:
        str: 报告提示词内容
    """
    logger = setup_logger("load_report_prompt")
    try:
        report_prompt_path = get_abs_path(prompt_conf["report_prompt_path"])
    except Exception as e:
        logger.error(
            f"[load_report_prompt] 'report_prompt_path' not found in config"
        )
        raise e
    try:
        with open(report_prompt_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(f"[load_report_prompt] loaded: {report_prompt_path}")
        return content
    except Exception as e:
        logger.error(f"[load_report_prompt] failed to read file: {str(e)}")
        raise e

if __name__=="__main__":
    print(load_system_prompt())
