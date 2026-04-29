"""
文件 MD5 校验工具
"""

import hashlib
import os
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from utils.logger_handler import setup_logger

# try:
#     from .logger_handler import setup_logger
# except ImportError:
#     from logger_handler import setup_logger


def get_file_md5(file_path: str) -> str:
    """获取文件的 MD5 值

    Args:
        file_path (str): 文件路径

    Returns:
        str: 文件的 MD5 值
    """
    logger = setup_logger("md5_handler")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"File not found: {file_path}")

    # 检查是否为文件
    if not os.path.isfile(file_path):
        logger.error(f"Not a valid file: {file_path}")
        raise ValueError(f"Not a valid file: {file_path}")

    md5_hash = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            # 分块读取，避免大文件占用过多内存
            for chunk in iter(lambda: f.read(8192), b""):
                md5_hash.update(chunk)
        md5_value = md5_hash.hexdigest()
        logger.info(f"MD5 calculated: {file_path} -> {md5_value}")
        return md5_value
    except Exception as e:
        logger.error(f"Failed to read file: {file_path}, error: {e}")
        raise


def listdir_with_allowed_type(path: str, allow_types: tuple[str]) -> tuple:
    """读取文件夹中的文件（预设类型）

    Args:
        path (str): 传入文件夹路径
        allow_types (tuple[str]): 传入允许的文件类型

    Returns:
        tuple: 返回一个文件列表的元组
    """
    files = []
    logger = setup_logger("listdir_with_allowed_type")

    # 检查路径是否为文件夹
    if not os.path.isdir(path):
        logger.error(f"{path} is not a directory")
        return ()

    # 遍历文件夹下的文件，筛选符合类型的文件
    for f in os.listdir(path):
        if f.endswith(allow_types):
            files.append(os.path.join(path, f))
    return tuple(files)


def pdf_loader(file_path: str, passwd: str = None) -> list[Document]:
    """加载 PDF 文件为 Document 列表

    Args:
        file_path (str): PDF 文件路径
        passwd (str, optional): PDF 密码，默认无

    Returns:
        list[Document]: Document 对象列表，元数据仅保留 source 和 page
    """
    logger = setup_logger("pdf_loader")
    try:
        loader = PyPDFLoader(file_path=file_path, password=passwd)
        documents = loader.load()
        # 只保留 source（文件路径）和 page（页码），丢弃 PDF 的其他元数据字段
        for doc in documents:
            doc.metadata = {
                "source": doc.metadata.get("source", file_path),
                "page": doc.metadata.get("page"),
            }
        logger.info(f"PDF loaded: {file_path}, pages: {len(documents)}")
        return documents
    except Exception as e:
        logger.error(f"Failed to load PDF: {file_path}, error: {e}")
        raise e


def text_loader(file_path: str) -> list[Document]:
    """加载文本文件为 Document 列表

    Args:
        file_path (str): 文本文件路径

    Returns:
        list[Document]: Document 对象列表
    """
    logger = setup_logger("text_loader")
    try:
        loader = TextLoader(file_path=file_path)
        documents = loader.load()
        logger.info(f"Text file loaded: {file_path}")
        return documents
    except Exception as e:
        logger.error(f"Failed to load text file: {file_path}, error: {e}")
        raise


if __name__ == "__main__":
    # # 测试 get_file_md5
    # test_file = __file__
    # md5_value = get_file_md5(test_file)
    # print(f"[get_file_md5] File: {test_file}")
    # print(f"[get_file_md5] MD5: {md5_value}")

    # 测试 listdir_with_allowed_type
    test_dir = "g:/agent/utils"
    py_files = listdir_with_allowed_type(test_dir, (".py",))
    print(f"[listdir_with_allowed_type] Directory: {test_dir}")
    print(f"[listdir_with_allowed_type] .py files: {py_files}")
