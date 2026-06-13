import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Optional


class SimilarityDetector:
    def __init__(self, stop_words: Optional[List[str]] = None):
        self.stop_words = stop_words or []
        self.vectorizer = TfidfVectorizer(
            tokenizer=self._tokenize,
            stop_words=self.stop_words,
            token_pattern=None
        )
        self.questions: List[str] = []
        self.question_ids: List[int] = []
        self.question_meta: List[Dict] = []
        self.tfidf_matrix = None
        self._fitted = False

    def _tokenize(self, text: str) -> List[str]:
        words = jieba.lcut(text)
        return [w for w in words if w.strip() and w not in self.stop_words]

    def add_questions(self, questions: List[Dict]) -> None:
        for q in questions:
            if q['id'] in self.question_ids:
                continue
            self.questions.append(q['text'])
            self.question_ids.append(q['id'])
            self.question_meta.append({k: v for k, v in q.items() if k != 'text'})
        self._rebuild_index()

    def add_question(self, question_id: int, text: str, **kwargs) -> None:
        if question_id in self.question_ids:
            return
        self.questions.append(text)
        self.question_ids.append(question_id)
        self.question_meta.append(kwargs)
        self._rebuild_index()

    def remove_question(self, question_id: int) -> bool:
        if question_id not in self.question_ids:
            return False
        idx = self.question_ids.index(question_id)
        self.questions.pop(idx)
        self.question_ids.pop(idx)
        self.question_meta.pop(idx)
        self._rebuild_index()
        return True

    def update_question(self, question_id: int, text: str, **kwargs) -> bool:
        if question_id not in self.question_ids:
            return False
        idx = self.question_ids.index(question_id)
        self.questions[idx] = text
        self.question_meta[idx] = kwargs
        self._rebuild_index()
        return True

    def _rebuild_index(self) -> None:
        if not self.questions:
            self._fitted = False
            self.tfidf_matrix = None
            return
        self.tfidf_matrix = self.vectorizer.fit_transform(self.questions)
        self._fitted = True

    def find_similar(
        self,
        text: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Tuple[int, float, Dict]]:
        if not self._fitted:
            return []
        text_vector = self.vectorizer.transform([text])
        similarities = cosine_similarity(text_vector, self.tfidf_matrix)[0]
        results = []
        for idx, sim in enumerate(similarities):
            if sim >= threshold:
                results.append((
                    self.question_ids[idx],
                    float(sim),
                    self.question_meta[idx]
                ))
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def batch_find_similar(
        self,
        texts: List[str],
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[List[Tuple[int, float, Dict]]]:
        return [self.find_similar(text, top_k, threshold) for text in texts]

    def get_all_questions(self) -> List[Dict]:
        return [
            {
                'id': qid,
                'text': text,
                **meta
            }
            for qid, text, meta in zip(
                self.question_ids,
                self.questions,
                self.question_meta
            )
        ]

    def clear(self) -> None:
        self.questions = []
        self.question_ids = []
        self.question_meta = []
        self.tfidf_matrix = None
        self._fitted = False

    def __len__(self) -> int:
        return len(self.questions)
