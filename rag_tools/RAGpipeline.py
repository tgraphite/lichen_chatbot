import openai
import chromadb
import requests


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

        self.api_config = {
            "key": "sk-jezwsedghloykbmyohheidckgiybkzglubelvrqqvwmjkerh",
            "chat_url": "https://api.siliconflow.cn/v1/chat/completions",
            "model": "Qwen/Qwen2.5-32B-Instruct",
            "system_prompt": "你是一个专业的分类学家，擅长回答植物分类学问题，你已经配备了检索增强搜索机制，可以参考上下文回答问题。\
                请注意，context可能与问题无关或低价值，注意辨别与忽略。作为服务端智能体，不要提及任何与context相关的信息，包括\
                是否使用context、哪里参考了context、context的来源、context的检索结果等一切相关信息。",
        }

    def generate_response(self, query, top_k=10, max_context=6000, no_context=False):
        # 1. 检索相关上下文
        chunks = self.retriever.query(query, top_k)

        # 2. 构建提示词
        context = "\n".join([c["content"] for c in chunks])
        truncated_context = context[:max_context]  # 防止超出token限制

        system_prompt = self.api_config["system_prompt"]

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

            # print(f"RAG外挂上下文：{truncated_context}")

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        # 3. 调用LLM API

        response = requests.post(
            self.api_config["chat_url"],
            json={
                "model": self.api_config["model"],
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 4096,
            },
            headers={"Authorization": f"Bearer {self.api_config['key']}"},
        )
        response.raise_for_status()
        output = response.json()["choices"][0]["message"]["content"]
        return output


# # 使用示例

Persist_directory = "vector_db"
Collection_name = "lichen-540"

pipeline = RAGPipeline(Persist_directory, Collection_name)

questions = ["王立松采集了哪些梅衣科的地衣？多说几个"]

for q in questions:
    print("问题")
    print(q)
    print("-" * 100)

    print("无RAG")
    answer = pipeline.generate_response(q, no_context=True)
    print(answer)
    print("-" * 100)

    print("有RAG")
    answer = pipeline.generate_response(q)
    print(answer)
    print("-" * 100)
