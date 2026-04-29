"""
配置文件加载器，支持加载 yaml 格式配置
"""
import yaml
from utils.path_tool import get_abs_path
# try:
#     from .path_tool import get_abs_path
# except ImportError:
#     from path_tool import get_abs_path


def load_rag_config(config_path: str = None, encoding: str = "utf-8"):
    """加载 rag 配置文件

    Args:
        config_path (str): 配置文件路径，默认为 config/rag.yml
        encoding (str): 文件编码，默认 utf-8

    Returns:
        dict: 配置文件内容
    """
    if config_path is None:
        config_path = get_abs_path("config/rag.yml")

    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)

def load_prompt_config(config_path: str = None, encoding: str = "utf-8"):
    """加载 rag 配置文件

    Args:
        config_path (str): 配置文件路径，默认为 config/prompt.yml
        encoding (str): 文件编码，默认 utf-8

    Returns:
        dict: 配置文件内容
    """
    if config_path is None:
        config_path = get_abs_path("config/prompt.yml")

    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_agent_config(config_path: str = None, encoding: str = "utf-8"):
    """加载 agent 配置文件

    Args:
        config_path (str): 配置文件路径，默认为 config/agent.yml
        encoding (str): 文件编码，默认 utf-8

    Returns:
        dict: 配置文件内容
    """
    if config_path is None:
        config_path = get_abs_path("config/agent.yml")

    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def load_chroma_config(config_path: str = None, encoding: str = "utf-8"):
    """加载 agent 配置文件

    Args:
        config_path (str): 配置文件路径，默认为 config/chroma.yml
        encoding (str): 文件编码，默认 utf-8

    Returns:
        dict: 配置文件内容
    """
    if config_path is None:
        config_path = get_abs_path("config/chroma.yml")

    with open(config_path, "r", encoding=encoding) as f:
        return yaml.load(f, Loader=yaml.FullLoader)


rag_conf = load_rag_config()
prompt_conf=load_prompt_config()
agent_conf = load_agent_config()
chroma_conf = load_chroma_config()

if __name__ == "__main__":
    print(rag_conf["chat_model_name"])
