"""依赖：langchain==1.2.0 / core==1.2.5 / text-splitters==1.1.0。
完整版本见 requirements.lock.txt；运行：python examples/09_rag_index.py。
"""

from rag_support import build_index, retrieve


def main() -> None:
    vectorstore, chunks = build_index("acme")
    retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
    top = retriever.invoke("年假")
    assert top[0].metadata["doc_id"] == "leave-v1"
    assert all(doc.metadata["tenant"] == "acme" for doc in chunks)
    assert all(len(doc.page_content) <= 90 for doc in chunks)
    assert retrieve("火星天气") == []
    assert retrieve("年假", "beta")[0].metadata["doc_id"] == "beta-leave-v1"
    print(f"已建立 acme 索引：{len(chunks)} 个片段")
    print(f"命中文档：{top[0].metadata['doc_id']}")
    print(top[0].page_content)
    print("长度、无匹配查询与租户边界检查：PASS")


if __name__ == "__main__":
    main()
