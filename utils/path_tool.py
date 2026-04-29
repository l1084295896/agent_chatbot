import os


def get_abs_path(relative_path: str) -> str:
    """获取基于项目目录的绝对路径

    Args:
        relative_path (str): 相对于项目根目录的路径

    Returns:
        str: 绝对路径
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)

if __name__=="__main__":
    print(get_abs_path("cofig.json"))
