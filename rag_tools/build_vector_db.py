# 安装核心依赖
# pip install chromadb sentence-transformers

import json
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import chromadb


class VectorDBBuilder:
    def __init__(self, persist_directory, collection_name):
        self.collection_name = collection_name
        self.client = chromadb.PersistentClient(persist_directory)
        self.embed_model = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

    def create_collection(self):
        return self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self.embed_model,
            metadata={"hnsw:space": "cosine"},  # 优化相似度计算
        )

    def load_data(self, jsonl_files, collection):
        all_chunks = []

        for file in jsonl_files:
            with open(file, "r") as f:
                chunks = [json.loads(line) for line in f]
                all_chunks.extend(chunks)

        # 准备数据格式
        ids = [chunk["id"] for chunk in all_chunks]
        documents = [chunk["content"] for chunk in all_chunks]
        metadatas = [
            {
                "type": chunk["metadata"]["type"],
                "source": chunk["metadata"]["source"],
                "language": chunk["metadata"].get("language", "en"),
            }
            for chunk in all_chunks
        ]

        # 批量插入（自动生成向量）
        collection.add(ids=ids, documents=documents, metadatas=metadatas)


# 使用示例
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="向量数据库构建工具")
    parser.add_argument(
        "-f", "--files", nargs="+", required=True, help="要处理的文本文件列表"
    )
    parser.add_argument("-o", "--output-dir", default="./vector_db", help="输出目录")
    parser.add_argument("-n", "--collection-name", default="rag_demo", help="集合名称")

    args = parser.parse_args()

    builder = VectorDBBuilder(
        persist_directory=args.output_dir, collection_name=args.collection_name
    )
    collection = builder.create_collection()
    builder.load_data(args.files, collection)
    print(f"向量数据库{args.collection_name}构建完成，存储到目录{args.output_dir}")
