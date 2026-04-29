from langchain.agents import create_agent
from model.factory import chat_model
from utils.prompt_loader import load_system_prompt
from agent.tools.agent_tools import (
    rag_summarize,
    get_weather,
    get_user_id,
    get_current_month,
    get_user_location,
    fetch_external_data,
    fill_context_for_report,
)
from agent.tools.middleware import monitor_tool, log_before_model, report_prompt_switch


class ReactAgent:
    def __init__(self):
        self.agent = create_agent(
            model=chat_model,
            tools=[
                rag_summarize,
                get_weather,
                get_user_id,
                get_current_month,
                get_user_location,
                fetch_external_data,
                fill_context_for_report,
            ],
            system_prompt=load_system_prompt(),
            middleware=[monitor_tool, log_before_model, report_prompt_switch],
        )

    def execute_stream(self,query:str):
        input_dict = {"messages": [{"role": "user",'content':query},]}

        #第三个参数context 就是hi做提示词切换时的标记
        last_content = query
        for chunk in self.agent.stream(input_dict,stream_mode="values",context={"report":False}):
            latest_mes=chunk["messages"][-1]
            if latest_mes.content:
                new_content = latest_mes.content.strip()
                # 只返回增量部分，避免重复累积内容导致流式输出闪烁
                if new_content.startswith(last_content):
                    delta = new_content[len(last_content):]
                    last_content = new_content
                    if delta:
                        yield delta + "\n"
                else:
                    # 内容完全改变（非累积），直接返回
                    last_content = new_content
                    yield new_content + "\n"


if __name__ == "__main__":
    agent = ReactAgent()
    mes=agent.execute_stream('扫地机器人在我所在的地区的气温下如何保养')
    for chunk in mes:
        print(chunk,end="",flush=True)
# end main