from langchain_core.documents.compressor import BaseDocumentCompressor
from src.core.base import LamBotDocument
from typing import List


class SemanticReranker(BaseDocumentCompressor):

    @staticmethod
    def _get_score(documents: LamBotDocument) -> float:
        """Get the reranker score from the document metadata.

        Args:
            documents (LamBotDocument): LamBot Documents

        Returns:
            float: Reranker score
        """
        return documents.metadata["@search.rerankerScore"]

    def compress_documents(
        self, documents: List[LamBotDocument]
    ) -> List[LamBotDocument]:
        """Reranks the documents based on the reranker score.

        Args:
            documents (List[LamBotDocument]): List of LamBotDocuments to rerank

        Returns:
            List[LamBotDocument]: Reranked LamBotDocuments
        """
        reranked_lambot_documents = sorted(documents, key=self._get_score, reverse=True)

        return reranked_lambot_documents
