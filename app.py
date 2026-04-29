import streamlit as st
from agent.react_agent import ReactAgent

# streamlit run app.py

st.title("智扫通机器人智能客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()
if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])

prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    response_placeholder = st.chat_message("assistant").write("")

    with st.spinner("智能客服思考中..."):
        res_stream = st.session_state["agent"].execute_stream(prompt)

        full_response = ""
        for delta in res_stream:
            full_response += delta
            response_placeholder.write(full_response)

    st.session_state["messages"].append({"role": "assistant", "content": full_response})
    st.rerun()
