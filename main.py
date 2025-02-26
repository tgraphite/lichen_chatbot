import streamlit as st
import requests
from functions import handle_lookup, handle_analysis, call_llm
from text_content import *  # 导入所有文本内容

# 设置页面配置
st.set_page_config(layout="wide")

st.title(TITLE)

# 初始化会话状态
if "model" not in st.session_state:
    st.session_state["model"] = DEFAULT_MODEL
if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_message_count" not in st.session_state:
    st.session_state.last_message_count = 0


def process_message(messages, action_type):
    """
    根据指定的操作类型处理消息并返回响应结果。

    参数:
        messages (list): 消息历史记录列表
        action_type (str): 操作类型，可以是查询、分析或发送

    返回:
        str: 处理后的响应文本
    """
    if action_type == BUTTON_LOOKUP:
        return handle_lookup(messages)
    elif action_type == BUTTON_ANALYSIS:
        return handle_analysis(messages)
    elif action_type == BUTTON_SEND:
        return call_llm(messages)
    else:
        return


def set_action(action_type):
    """
    处理用户输入并根据指定的操作类型生成响应。

    参数:
        action_type (str): 操作类型，可以是查询、分析或发送
    """
    # 获取用户输入
    user_message = st.session_state.user_input
    if user_message == "":
        return

    # 添加输入到历史记录
    # 如果不这样处理，此处有意料之外的行为，输入会添加两次。
    if st.session_state.messages == []:
        st.session_state.messages.append({"role": "user", "content": user_message})
    if user_message != st.session_state.messages[-1]["content"]:
        st.session_state.messages.append({"role": "user", "content": user_message})

    # 处理消息并获取回复
    output = process_message(st.session_state.messages.copy(), action_type)

    # 添加回复到历史记录
    st.session_state.messages.append({"role": "assistant", "content": output})

    # 清空输入
    st.session_state.user_input = ""


def clear_chat():
    """
    清除聊天历史记录。
    """
    st.session_state.messages = []
    st.session_state.last_message_count = 0


def handle_enter():
    """
    处理用户按下回车键的事件，触发发送操作。
    """
    if st.session_state.user_input:
        set_action(BUTTON_SEND)


# 创建UI组件
chat_container = st.container(height=500)

# 显示聊天历史
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # 添加底部空白间距
    st.markdown("<br><br>", unsafe_allow_html=True)

# 创建输入区和按钮
st.text_input(
    INPUT_PLACEHOLDER,
    placeholder=INPUT_NOTIFICATION,
    key="user_input",
    on_change=handle_enter,
)

# 创建按钮行
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.button(BUTTON_CLEAR, on_click=clear_chat, use_container_width=True)

with col2:
    st.button(
        BUTTON_LOOKUP,
        on_click=set_action,
        args=(BUTTON_LOOKUP,),
        use_container_width=True,
    )

with col3:
    st.button(
        BUTTON_ANALYSIS,
        on_click=set_action,
        args=(BUTTON_ANALYSIS,),
        use_container_width=True,
    )

with col4:
    st.button(
        BUTTON_SEND, on_click=set_action, args=(BUTTON_SEND,), use_container_width=True
    )

# 在主容器之外添加页脚
st.markdown(
    f"""
    <footer style="position: relative; bottom: 0; left: 0; right: 0; text-align: center; padding: 10px; font-size: 12px; color: #888; margin-top: 30px; width: 100%;">
        <div>{FOOTER_CONTACT}</div>
        {FOOTER_COPYRIGHT} | <a href="{FOOTER_ICP_LINK}" target="_blank">{FOOTER_ICP}</a> 
    </footer>
    """,
    unsafe_allow_html=True,
)
