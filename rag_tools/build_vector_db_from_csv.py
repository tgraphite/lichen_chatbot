import json
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import chromadb
import hashlib
import pandas as pd


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

    def import_data(self, jsonl_files, collection):
        all_chunks = []

        for file in jsonl_files:
            with open(file, "r") as f:
                chunks = [json.loads(line) for line in f]
                all_chunks.extend(chunks)

        ids = [chunk["id"] for chunk in all_chunks]
        documents = []
        for chunk in all_chunks:
            doc = ";".join([str(v) for v in chunk.values()])
            documents.append(doc)

        # documents = [" ".join(chunk.values()) for chunk in all_chunks]
        # metadatas = [
        #     {
        #         "type": chunk["metadata"]["type"],
        #         "source": chunk["metadata"]["source"],
        #         "language": chunk["metadata"].get("language", "en"),
        #     }
        #     for chunk in all_chunks
        # ]

        collection.add(ids=ids, documents=documents)


def convert_data_from_csv(csv_file, jsonl_file):
    df = pd.read_csv(csv_file, encoding="utf-8")
    columns = df.columns.tolist()
    chunks = []
    salt = "202502061736".encode()

    for row_id in range(len(df)):
        chunk = df.iloc[row_id].to_dict()
        string = " ".join(df.iloc[row_id].to_string()).encode() + salt
        hash = hashlib.sha256(string).hexdigest()
        chunk["id"] = hash
        chunks.append(chunk)

    with open(jsonl_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"√ JSONL文件已生成: {jsonl_file}")

    return jsonl_file


if __name__ == "__main__":
    persist_directory = "vector_db"
    collection_name = "lichen-540"

    # convert_data_from_csv("lichen-540.csv", "lichen-540.jsonl")

    builder = VectorDBBuilder(
        persist_directory=persist_directory, collection_name=collection_name
    )
    collection = builder.create_collection()
    builder.import_data(["lichen-540.jsonl"], collection)
