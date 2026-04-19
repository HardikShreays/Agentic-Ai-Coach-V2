from services import rag_service


class _FakeCollection:
    def __init__(self, count: int = 1):
        self._count = count

    def count(self):
        return self._count

    def query(self, query_texts, n_results, where=None):
        return {
            "documents": [["Use STAR format for HR.", "Practice SQL daily."]],
            "metadatas": [[
                {"title": "Interview strategy", "source": "kb", "role": "general", "topic": "career"},
                {"title": "Data prep", "source": "kb", "role": "data-analyst", "topic": "skills"},
            ]],
            "distances": [[0.21, 0.32]],
        }


def test_format_retrieval_context_empty():
    text = rag_service.format_retrieval_context([])
    assert "No knowledge base matches" in text


def test_retrieve_guidance_context_with_fake_collection(monkeypatch):
    monkeypatch.setattr(rag_service, "_collection", lambda: _FakeCollection())
    rows = rag_service.retrieve_guidance_context("how to prepare", role="general", topic="career", k=2)
    assert len(rows) == 2
    assert rows[0]["title"] == "Interview strategy"
    formatted = rag_service.format_retrieval_context(rows)
    assert "Retrieved guidance context" in formatted
    assert "Interview strategy" in formatted
