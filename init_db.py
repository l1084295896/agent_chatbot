"""
初始化脚本 - 向量知识库初始化模块

功能：
    首次部署或添加新文档后，运行本脚本将 data/external/ 目录下的文档
    加载到 Chroma 向量库。

使用方法：
    python init_db.py

说明：
    - 本脚本仅负责初始化，不参与应用运行时逻辑
    - 支持 TXT 和 PDF 格式的文档
    - 使用 MD5 去重机制，已加载的文档不会重复添加
    - 向量库持久化到 chroma_db/ 目录

应用启动流程：
    1. 首次部署：python init_db.py（初始化知识库）
    2. 正常运行：streamlit run app.py（仅连接已有向量库）
"""

from rag.vector_store import VectorStoreService
from utils.logger_handler import setup_logger


def init_vector_store():
    """
    初始化向量知识库

    流程：
    1. 创建 VectorStoreService 实例（建立与 Chroma 的连接）
    2. 调用 load_document() 将 data 目录下的文档加载到向量库
    3. 输出加载结果统计

    注意：
        VectorStoreService.__init__() 仅连接已有向量库，
        实际的文档加载由 load_document() 方法完成。
        这样设计是为了保持"初始化"和"运行"的职责分离。
    """
    logger = setup_logger("init_vector_store")

    logger.info("=" * 50)
    logger.info("开始初始化向量知识库...")
    logger.info("=" * 50)

    # 步骤1：创建向量库服务实例
    # - 建立与 Chroma 持久化向量库的连接
    # - 配置文本分割器
    vs_service = VectorStoreService()
    logger.info("向量库服务初始化完成")

    # 步骤2：加载文档到向量库
    # - 遍历 data/external/ 目录
    # - 跳过已加载的文档（MD5 去重）
    # - 支持 TXT 和 PDF 格式
    vs_service.load_document()
    logger.info("文档加载完成")

    # 步骤3：输出检索器验证
    # - 获取检索器用于验证向量库状态
    # - 如果能正常获取检索器，说明初始化成功
    retriever = vs_service.get_retriever()
    logger.info("检索器验证通过")

    logger.info("=" * 50)
    logger.info("向量知识库初始化完成！")
    logger.info("现在可以启动应用：streamlit run app.py")
    logger.info("=" * 50)


if __name__ == "__main__":
    init_vector_store()
