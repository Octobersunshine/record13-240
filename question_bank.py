import json
import os
from typing import List, Dict, Optional
from similarity_detector import SimilarityDetector


class QuestionBank:
    def __init__(self, data_file: str = 'questions.json', stop_words: Optional[List[str]] = None):
        self.data_file = data_file
        self.detector = SimilarityDetector(stop_words=stop_words)
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            self.detector.add_questions(questions)

    def _save(self) -> None:
        questions = self.detector.get_all_questions()
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)

    def add_question(self, question_id: int, text: str, **kwargs) -> bool:
        if question_id in self.detector.question_ids:
            return False
        self.detector.add_question(question_id, text, **kwargs)
        self._save()
        return True

    def add_questions(self, questions: List[Dict]) -> int:
        count = 0
        for q in questions:
            if q['id'] not in self.detector.question_ids:
                self.detector.add_question(q['id'], q['text'], **{k: v for k, v in q.items() if k not in ['id', 'text']})
                count += 1
        if count > 0:
            self._save()
        return count

    def remove_question(self, question_id: int) -> bool:
        result = self.detector.remove_question(question_id)
        if result:
            self._save()
        return result

    def update_question(self, question_id: int, text: str, **kwargs) -> bool:
        result = self.detector.update_question(question_id, text, **kwargs)
        if result:
            self._save()
        return result

    def get_question(self, question_id: int) -> Optional[Dict]:
        if question_id not in self.detector.question_ids:
            return None
        idx = self.detector.question_ids.index(question_id)
        return {
            'id': question_id,
            'text': self.detector.questions[idx],
            **self.detector.question_meta[idx]
        }

    def find_similar_questions(
        self,
        text: str,
        top_k: int = 5,
        threshold: float = 0.7
    ) -> List[Dict]:
        results = self.detector.find_similar(text, top_k, threshold)
        return [
            {
                'id': qid,
                'similarity': sim,
                'text': self.detector.questions[self.detector.question_ids.index(qid)],
                **meta
            }
            for qid, sim, meta in results
        ]

    def find_duplicates(
        self,
        text: str,
        threshold: float = 0.9
    ) -> List[Dict]:
        return self.find_similar_questions(text, top_k=10, threshold=threshold)

    def check_duplicate(
        self,
        text: str,
        threshold: float = 0.9
    ) -> Dict:
        duplicates = self.find_duplicates(text, threshold)
        if duplicates:
            return {
                'is_duplicate': True,
                'duplicates': duplicates
            }
        return {
            'is_duplicate': False,
            'duplicates': []
        }

    def get_all_questions(self) -> List[Dict]:
        return self.detector.get_all_questions()

    def clear(self) -> None:
        self.detector.clear()
        if os.path.exists(self.data_file):
            os.remove(self.data_file)

    def __len__(self) -> int:
        return len(self.detector)
