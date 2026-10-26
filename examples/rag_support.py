"""教学 RAG 公用数据。依赖版本见 requirements.lock.txt。

关键词向量只为离线演示检索接口，不是训练得到的语义 embedding。
"""

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter


class KeywordEmbeddings(Embeddings):
    vocabulary = ("年假", "报销", "住宿", "VPN", "发票", "审批")

    def embed_query(self, text: str) -> list[float]:
        return [float(text.count(word)) for word in self.vocabulary]

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]


DOCUMENTS = [
    Document(
        page_content="年假制度：正式员工每年享有 10 天年假。年假申请应提前 3 个工作日提交，由直属主管审批。",
        metadata={"tenant": "acme", "doc_id": "leave-v1", "source": "员工手册/年假", "version": 1},
    ),
    Document(
        page_content="报销制度：住宿报销上限为每晚 500 元，报销时必须附发票。超额住宿费用需要主管审批。",
        metadata={"tenant": "acme", "doc_id": "expense-v1", "source": "财务制度/住宿", "version": 1},
    ),
    Document(
        page_content="年假制度：另一家公司的年假为每年 30 天。此文档仅属于 beta 租户。",
        metadata={"tenant": "beta", "doc_id": "beta-leave-v1", "source": "Beta 内部手册", "version": 1},
    ),
]


def build_index(tenant: str) -> tuple[InMemoryVectorStore, list[Document]]:
    if tenant not in {"acme", "beta"}:
        raise PermissionError("未知租户")
    # 身份来自应用鉴权层；模型不可自行选择 tenant。先筛选，再建立租户索引。
    permitted = [doc for doc in DOCUMENTS if doc.metadata["tenant"] == tenant]
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=90,
        chunk_overlap=15,
        separators=["\n\n", "\n", "。", "，", ""],
    )
    chunks = splitter.split_documents(permitted)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = f"{chunk.metadata['doc_id']}:{index}"
    vectorstore = InMemoryVectorStore(KeywordEmbeddings())
    vectorstore.add_documents(chunks, ids=[c.metadata["chunk_id"] for c in chunks])
    return vectorstore, chunks


def retrieve(question: str, tenant: str = "acme", k: int = 2) -> list[Document]:
    embedding = KeywordEmbeddings()
    if not any(embedding.embed_query(question)):
        return []
    # ponytail: 微型语料每次重建；真实服务在启动或索引发布时加载，按租户缓存。
    vectorstore, _ = build_index(tenant)
    hits = vectorstore.similarity_search_with_score(question, k=k)
    return [doc for doc, score in hits if score >= 0.5]


def format_context(documents: list[Document]) -> str:
    return "\n\n".join(
        f"[{doc.metadata['doc_id']}] {doc.page_content}" for doc in documents
    )
