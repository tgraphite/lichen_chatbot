import openai
import chromadb
import requests
from call_ai import call_siliconflow_qwen_32b


class RAGRetriever:

    def __init__(self, persist_directory, collection_name):
        self.client = chromadb.PersistentClient(persist_directory)
        self.collection = self.client.get_collection(collection_name)

    def query(self, question, top_k=3, filters=None):
        # 元数据过滤条件示例: {"type": "code", "source": "example.html"}
        results = self.collection.query(
            query_texts=[question], n_results=top_k, where=filters
        )

        return [
            {"content": doc, "metadata": meta, "distance": dist}
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]


class RAGPipeline:
    def __init__(self, persist_directory, collection_name):
        self.retriever = RAGRetriever(persist_directory, collection_name)

    def generate_response(self, query, top_k=10, max_context=3800, no_context=False):
        # 1. 检索相关上下文
        retrieved = self.retriever.query(query, top_k)
        context = "\n".join([c["content"] for c in retrieved])
        truncated_context = context[:max_context]

        system_prompt = "你是一个专业的分类学家，擅长回答植物分类学问题，你已经配备了检索增强搜索机制，可以参考上下文回答问题。\
            请注意，context可能与问题无关或低价值，注意辨别与忽略。作为服务端智能体，不要提及任何与context相关的信息，包括\
            是否使用context、哪里参考了context、context的来源、context的检索结果等一切相关信息。"

        if no_context:
            prompt = f"""
            仅基于你的知识，回答问题：
            问题：{query}
            答案："""
        else:
            prompt = f"""
            基于你的知识，以及以下搜索到的context回答问题，请注意，context可能与问题无关或低价值，注意辨别与忽略：
            {truncated_context}

            问题：{query}
            答案："""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 3. 调用LLM API

        output = call_siliconflow_qwen_32b(system_prompt, prompt)
        return output


# # 使用示例

Persist_directory = "vector_db"
Collection_name = "test_db"


pipeline = RAGPipeline(Persist_directory, Collection_name)

questions = ["王立松在云南发现了哪些地衣?"]

for q in questions:
    print("问题")
    print(q)
    print("-" * 100)

    print("无RAG")
    answer = pipeline.generate_response(q, no_context=True)
    print(answer)
    print("-" * 100)

    print("有RAG")
    answer = pipeline.generate_response(q, top_k=50)
    print(answer)
    print("-" * 100)
