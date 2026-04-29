"""
向量库服务模块

功能：
1. 将本地文档(txt/pdf)加载并分割为文本块
2. 通过嵌入模型将文本块转换为向量,存入 Chroma 向量库
3. 提供基于语义相似度的文档检索能力
"""

from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
from utils.path_tool import get_abs_path
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from utils.file_handler import (
    text_loader,
    pdf_loader,
    listdir_with_allowed_type,
    get_file_md5,
)
from utils.logger_handler import setup_logger
from langchain_core.documents import Document


class VectorStoreService:
    """向量库服务类,封装文档加载、分割、存储和检索功能"""

    def __init__(self):
        """
        初始化向量库服务
        - 建立与 Chroma 持久化向量库的连接
        - 配置文本分割器(分块大小、重叠量、分隔符)
        """
        # 连接 Chroma 向量库,collection_name 指定库名称,persist_directory 指定持久化存储路径
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,  # 嵌入模型,将文本转为向量
            persist_directory=get_abs_path(chroma_conf["persist_directory"]),
        )
        # 配置文本分割器：按 separator 列表顺序递归分割,直到每个块 <= chunk_size
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],  # 分割后每个文本块的最大字符数
            chunk_overlap=chroma_conf[
                "chunk_overlap"
            ],  # 相邻文本块之间的重叠字符数,保持语义连贯
            separators=chroma_conf["separators"],  # 分割符列表,按优先级顺序尝试分割
            length_function=len,  # 用 Python 内置 len 计算文本长度
        )

    def get_retriever(self):
        """
        获取检索器(Retriever)
        用于在向量库中根据语义相似度搜索最相关的 Top-K 文档块
        """
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})

    def load_document(self):
        """
        加载 data 目录下的所有文档(txt/pdf),分割后存入向量库

        流程：
        1. 遍历 data 目录,获取所有允许类型的文件路径
        2. 计算每个文件的 MD5,若已处理过(记录在 md5.txt)则跳过
        3. 用 text_loader 或 pdf_loader 读取文件内容
        4. 用 RecursiveCharacterTextSplitter 将文档分割为文本块
        5. 将文本块通过嵌入模型转为向量,存入 Chroma 向量库
        6. 将文件 MD5 写入 md5.txt,避免下次重复加载
        """
        logger = setup_logger("load_document")

        def check_md5_hex(md5_for_check: str) -> bool:
            """
            检查目标 MD5 是否已记录在 md5.txt 中
            若文件不存在则创建空文件,返回 False(表示未记录)
            """
            md5_path = get_abs_path(chroma_conf["md5_hex_store"])
            if not os.path.exists(md5_path):
                # 不存在则创建空文件
                open(file=md5_path, mode="w", encoding="utf-8").close()
                return False
            with open(file=md5_path, mode="r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                        return True  # 命中,已记录
                return False  # 未命中,未记录

        def save_md5_hex(md5_for_check: str):
            """
            将已处理文件的 MD5 追加写入 md5.txt
            使用追加模式,不会覆盖已有记录
            """
            md5_path = get_abs_path(chroma_conf["md5_hex_store"])
            with open(md5_path, "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")

        def get_file_documents(read_path: str) -> list[Document]:
            """
            根据文件扩展名调用对应的加载器读取文件
            返回 langchain Document 对象列表
            """
            if read_path.endswith("txt"):
                return text_loader(read_path)
            elif read_path.endswith("pdf"):
                return pdf_loader(read_path)
            else:
                # 不支持的类型返回空列表
                return []

        # 获取 data 目录下所有允许类型的文件路径列表
        allowed_file_path = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        for path in allowed_file_path:
            md5_hex = get_file_md5(path)
            # 检查 MD5,若已处理过则跳过
            if check_md5_hex(md5_hex):
                logger.info(
                    f"[load_document] {path} is already in knowledge base. SKIP"
                )
                continue

            try:
                # 加载文件内容为 Document 列表
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[load_document] {path} has no valid content. SKIP")
                    continue

                # 将长文档分割为短文本块
                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(
                        f"[load_document] {path} has no valid content after split. SKIP"
                    )
                    continue

                # 将文本块转为向量,存入 Chroma 向量库
                self.vector_store.add_documents(split_document)

                # 记录已处理文件的 MD5,避免下次重复加载
                save_md5_hex(md5_hex)

                logger.info(f"[load_document] {path} content loaded successfully")
            except Exception as e:
                # exc_info=True 记录完整堆栈,便于排查问题
                logger.error(
                    f"[load_document] {path} loading failed: {str(e)}", exc_info=True
                )
                continue


if __name__ == "__main__":
    # 初始化向量库服务
    vs = VectorStoreService()

    # 将 data 目录下的文档加载到向量库
    vs.load_document()

    # 获取检索器
    retriever = vs.get_retriever()

    # 用语义查询搜索相关文档块
    res = retriever.invoke("迷路")

    for r in res:
        print(r.page_content)
        print("=" * 20)
