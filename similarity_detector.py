import re
import jieba
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Tuple, Dict, Optional, Set


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
        self.question_numbers: List[Set[str]] = []
        self.question_operators: List[Set[str]] = []
        self.tfidf_matrix = None
        self._fitted = False
        self._superscript_map = {'²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁰': '0', '¹': '1'}
        self._subscript_map = {'₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9', '₀': '0', '₁': '1'}
        self._number_pattern = re.compile(r'\d+\.?\d*')
        self._operator_pattern = re.compile(r'[+\-*/×÷=<>≠≤≥]')

    def _normalize_text(self, text: str) -> str:
        normalized = text
        for sup, num in self._superscript_map.items():
            normalized = normalized.replace(sup, num)
        for sub, num in self._subscript_map.items():
            normalized = normalized.replace(sub, num)
        return normalized

    def _extract_numbers(self, text: str) -> Set[str]:
        normalized = self._normalize_text(text)
        numbers = self._number_pattern.findall(normalized)
        return set(numbers)

    def _extract_numbers_with_order(self, text: str) -> List[str]:
        normalized = self._normalize_text(text)
        return self._number_pattern.findall(normalized)

    def _extract_operators(self, text: str) -> Set[str]:
        return set(self._operator_pattern.findall(text))

    def _tokenize(self, text: str) -> List[str]:
        numbers = self._number_pattern.findall(text)
        processed = text
        for i, num in enumerate(numbers):
            processed = processed.replace(num, f' NUM{i} ', 1)
        words = jieba.lcut(processed)
        result = []
        num_idx = 0
        for w in words:
            w = w.strip()
            if not w or w in self.stop_words:
                continue
            if w.startswith('NUM') and num_idx < len(numbers):
                result.append(f'NUM_{numbers[num_idx]}')
                num_idx += 1
            else:
                result.append(w)
        return result

    def _calculate_number_penalty(
        self,
        input_numbers: Set[str],
        input_operators: Set[str],
        target_numbers: Set[str],
        target_operators: Set[str],
        input_text: str = '',
        target_text: str = ''
    ) -> float:
        has_numbers_input = len(input_numbers) > 0 or len(input_operators) > 0
        has_numbers_target = len(target_numbers) > 0 or len(target_operators) > 0

        if not has_numbers_input and not has_numbers_target:
            return 1.0

        if has_numbers_input != has_numbers_target:
            return 0.1

        number_score = 1.0
        if input_numbers or target_numbers:
            if not input_numbers or not target_numbers:
                number_score = 0.05
            else:
                intersection = input_numbers & target_numbers
                union = input_numbers | target_numbers
                jaccard = len(intersection) / len(union) if union else 0

                if jaccard == 0:
                    number_score = 0.05
                elif jaccard < 0.3:
                    number_score = 0.15
                elif jaccard < 0.5:
                    number_score = 0.25
                elif jaccard < 0.7:
                    number_score = 0.4
                elif jaccard < 1.0:
                    number_score = 0.6
                else:
                    number_score = 1.0

                if input_text and target_text and len(input_numbers) == len(target_numbers) and len(input_numbers) > 0:
                    input_order = self._extract_numbers_with_order(input_text)
                    target_order = self._extract_numbers_with_order(target_text)
                    if input_order == target_order:
                        number_score = min(number_score * 1.2, 1.0)
                    else:
                        position_matches = sum(1 for i in range(min(len(input_order), len(target_order))) if input_order[i] == target_order[i])
                        position_score = position_matches / max(len(input_order), len(target_order))
                        number_score = number_score * (0.5 + position_score * 0.5)

        operator_score = 1.0
        if input_operators or target_operators:
            if not input_operators or not target_operators:
                operator_score = 0.2
            else:
                if input_operators != target_operators:
                    if len(input_operators & target_operators) == 0:
                        operator_score = 0.1
                    else:
                        operator_score = 0.3

        combined = min(number_score, operator_score)

        if len(input_operators) > 0 and len(target_operators) > 0:
            if combined < 0.5 and number_score < 0.5 and operator_score < 0.5:
                combined = min(combined, 0.1)

        return combined

    def add_questions(self, questions: List[Dict]) -> None:
        for q in questions:
            if q['id'] in self.question_ids:
                continue
            self.questions.append(q['text'])
            self.question_ids.append(q['id'])
            self.question_meta.append({k: v for k, v in q.items() if k != 'text'})
            self.question_numbers.append(self._extract_numbers(q['text']))
            self.question_operators.append(self._extract_operators(q['text']))
        self._rebuild_index()

    def add_question(self, question_id: int, text: str, **kwargs) -> None:
        if question_id in self.question_ids:
            return
        self.questions.append(text)
        self.question_ids.append(question_id)
        self.question_meta.append(kwargs)
        self.question_numbers.append(self._extract_numbers(text))
        self.question_operators.append(self._extract_operators(text))
        self._rebuild_index()

    def remove_question(self, question_id: int) -> bool:
        if question_id not in self.question_ids:
            return False
        idx = self.question_ids.index(question_id)
        self.questions.pop(idx)
        self.question_ids.pop(idx)
        self.question_meta.pop(idx)
        self.question_numbers.pop(idx)
        self.question_operators.pop(idx)
        self._rebuild_index()
        return True

    def update_question(self, question_id: int, text: str, **kwargs) -> bool:
        if question_id not in self.question_ids:
            return False
        idx = self.question_ids.index(question_id)
        self.questions[idx] = text
        self.question_meta[idx] = kwargs
        self.question_numbers[idx] = self._extract_numbers(text)
        self.question_operators[idx] = self._extract_operators(text)
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
        input_numbers = self._extract_numbers(text)
        input_operators = self._extract_operators(text)
        results = []
        for idx, sim in enumerate(similarities):
            penalty = self._calculate_number_penalty(
                input_numbers, input_operators,
                self.question_numbers[idx], self.question_operators[idx],
                text, self.questions[idx]
            )
            adjusted_sim = float(sim * penalty)
            if adjusted_sim >= threshold:
                results.append((
                    self.question_ids[idx],
                    adjusted_sim,
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
        self.question_numbers = []
        self.question_operators = []
        self.tfidf_matrix = None
        self._fitted = False

    def __len__(self) -> int:
        return len(self.questions)
