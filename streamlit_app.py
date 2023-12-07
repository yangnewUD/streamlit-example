# -*- encoding: utf-8 -*-
# @Author: yangwei
# @Contact: 1521506204@qq.com
import importlib
import shutil
import time
import uuid
from pathlib import Path
from typing import Dict
import numpy as np
import streamlit as st
import os
from data_scan.utils import read_yaml

config = read_yaml("data_scan/config.yaml")

st.set_page_config(
    page_title=config.get("title"),
    page_icon=":robot:",
)
st.session_state["params"] = {}

def init_parameters():
    print(st.session_state)
    if "params" not in st.session_state:
        st.session_state['params'] = {}
    if "params" not in st.session_state:
        print(st.session_state)
    param = config.get("Parameter")
    st.session_state["params"]["max_length"] = param.get("max_length").get("default")
    st.session_state["params"]["top_p"] = param.get("top_p").get("default")
    st.session_state["params"]["temperature"] = param.get("temperature").get("default")



def predict(text, model):
    params_dict = st.session_state["params"]
    response = model(text, history=None, **params_dict)
    print_response(response)


def print_response(content, avatar: str = "🤖"):
    find = False
    with st.chat_message("assistant", avatar=avatar):
        message_placeholder = st.empty()
        full_response = ""
        for chunk in content.split():
            full_response += chunk + " "
            time.sleep(0.05)
            #message_placeholder.markdown(full_response + "▌")
        #message_placeholder.markdown(full_response)
        for item in leibie:
            if item in full_response:
                find = True
                message_placeholder.markdown(item)
                break
        if find == False:
            message_placeholder.markdown("暂不支持该分类")



leibie = ["姓名","银行账号","身份证号","年龄","性别","地址","职业","宗教信仰","民族","国籍","电话号码"
          ,"邮箱地址","车牌号","VIN码","MAC地址","车辆品牌","车辆型号","身份证件","驾驶证号","驾驶证","护照","位置信息"
          ,"生活服务信息","发动机号","SIM卡信息","车辆类型","消费记录","里程信息","驾驶行为信息","前进方向信息","转向角信息","道路情况"
          ,"气候环境","行驶路线"]
def get_prompt(name: str, desc: str, sample: str):
    return f"""你现在要进行数据分类的工作，根据数据库的字段名、注释和样例数据对数据进行分类，类别包含：
    '姓名'
    '银行账号'
    '身份证号'
    '年龄'
    '性别'
    '地址'
    '职业'
    '宗教信仰'
    '民族'
    '国籍'
    '电话号码'
    '邮箱地址'
    '车牌号'
    'VIN码'
    'MAC地址'
    '车辆品牌'
    '车辆型号'
    '身份证件'
    '驾驶证号'
    '驾驶证'
    '护照'
    '位置信息'
    '生活服务信息'
    '发动机号'
    'SIM卡信息'
    '车辆类型'
    '消费记录'
    '生活习惯'
    '车门状态信息'
    '灯光状态信息'
    '胎压状态信息'
    '车窗状态信息'
    '空调状态信息'
    '发动机转速信息'
    '加速度信息'
    '档位使用信息'
    '平均速度信息'
    '里程信息'
    '驾驶行为信息'
    '前进方向信息'
    '转向角信息'
    '道路情况'
    '气候环境'
    '行驶路线'，
    输出的答案只能是上述类别中的一个，不需要多余的回复，若无法识别则返回'不支持字段'，
    例如，待分类数据如下:'字段:wsd 注释: 样例数据:张三,李四'
    输出:姓名
    请对下面数据进行分类
    '字段:{name} 注释:{desc} 样例数据{sample}'
    """
    
if __name__ == "__main__":
    title = config.get("title")
    version = config.get("version", "0.0.1")
    init_parameters()
    st.markdown(
        f"<h3 style='text-align: center;'>{title} v{version}</h3><br/>",
        unsafe_allow_html=True,
    )
    llm_module = importlib.import_module("data_scan.llm")
    llm_params: Dict[str, Dict] = config.get("LLM_API")
    llm_params["ERNIEBot"]["access_token"] = st.secrets["LLM_TOKEN"]
    MODEL_OPTIONS = {
        name: getattr(llm_module, name)(**params) for name, params in llm_params.items()
    }
    llm = MODEL_OPTIONS["ERNIEBot"]
    st.sidebar.markdown("### 🛶 类别设置", help="依据相应行业标准/企标定义")
    with st.sidebar.container(border=True):
        col1, col2 = st.columns(2)
        for item in leibie:
            col1.text(item)
    st.header('请输入数据: :red[字段名] 、字段注释和样例数据', divider='rainbow',help="字段名必填;注释和样例数据选填")
    menu_col1, menu_col2, menu_col3 = st.columns([1, 1, 1])
    col_name = menu_col1.text_input("字段名*")
    col_des = menu_col2.text_input("字段注释")
    col_sample = menu_col3.text_input("样例数据")
    if st.button("提交"):
        if col_name == '':
            st.toast(":heavy_exclamation_mark:字段名不能为空，请查看填写提示")
        else:
            predict(get_prompt(col_name, col_des, col_sample), llm)

    
