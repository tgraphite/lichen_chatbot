import requests
import json
from llm_api.LLMCaller import LLMCaller as LLMCaller
from prompts import prompt_biodiversity_description_generator
import time

workflow_database_retriver = "7475558441509404723"
workflow_request_refinement = "7472194940572778522"
coze_api_key = "pat_EIqiQDu9D4ChGrrBMicYRkq0BHiwRlP9tc8Ndi3M9H5tvZsCQYiuwowzm8Y9VsSH"
coze_base_url = "https://api.coze.cn/v1/workflow/run"
record_file = "record.txt"

proxies = {"http": None, "https": None}
llmcaller = LLMCaller()


def write_record(question, answer):
    with open(record_file, "a") as f:
        f.write(
            f"time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\nquestion: {question}\n answer: {answer}\n\n"
        )


def call_workflow(workflow_id, question):
    headers = {
        "Authorization": f"Bearer {coze_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "parameters": {"input": question},
        "workflow_id": workflow_id,
    }
    result = requests.post(
        coze_base_url, headers=headers, json=payload, proxies=proxies
    )
    result = result.json()
    output = json.loads(result["data"])["output"]
    return output


def call_llm(messages):
    system_prompt = {
        "role": "system",
        "content": "你是一个专业的地衣学家，擅长分析和解释地衣分类学、植物学问题。",
    }
    full_messages = [
        system_prompt,
        *messages,
    ]
    answer = llmcaller.completion("qwen2.5-32b-instruct", messages=full_messages)
    write_record(messages[-1]["content"], answer)
    return answer


def handle_send(messages):
    question = messages[-1]["content"]
    output = call_workflow(workflow_test, question)
    write_record(question, output)
    return output


def handle_lookup(messages):
    question = messages[-1]["content"]
    output = call_workflow(workflow_database_retriver, question)
    write_record(question, output)
    return output


def handle_analysis(messages):
    question = messages[-1]["content"]
    print(f"handle_analysis: {question}")

    messages = [
        {"role": "system", "content": prompt_biodiversity_description_generator},
        {"role": "user", "content": question},
    ]
    output = llmcaller.completion("qwen2.5-32b-instruct", messages=messages)
    write_record(question, output)
    return output
