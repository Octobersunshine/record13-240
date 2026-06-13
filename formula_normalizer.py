import re
from typing import Dict, Tuple, List, Optional


class FormulaNormalizer:
    def __init__(self):
        self._superscript_map = {'²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9', '⁰': '0', '¹': '1'}
        self._subscript_map = {'₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9', '₀': '0', '₁': '1'}
        self._operator_map = {'×': '\\times', '÷': '\\div', '≠': '\\neq', '≤': '\\leq', '≥': '\\geq', '±': '\\pm', '·': '\\cdot'}
        self._greek_map = {'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'δ': '\\delta', 'ε': '\\epsilon', 'θ': '\\theta', 'λ': '\\lambda', 'μ': '\\mu', 'π': '\\pi', 'σ': '\\sigma', 'φ': '\\phi', 'ω': '\\omega', 'Δ': '\\Delta', 'Σ': '\\Sigma', 'Ω': '\\Omega'}
        self._function_names = ['sin', 'cos', 'tan', 'log', 'ln', 'sqrt', 'exp']
        self._fraction_pattern = re.compile(r'(\d+)/(\d+)')
        self._sqrt_pattern = re.compile(r'sqrt\(([^)]+)\)')
        self._formula_boundary = re.compile(r'(\$[^$]+\$|\\\[[^\]]+\\\]|\\\([^)]+\\\))')
        self._latex_cmd_pattern = re.compile(r'\\[a-zA-Z]+')

    def _replace_special_chars(self, text: str) -> str:
        result = text
        for char, num in self._superscript_map.items():
            result = result.replace(char, f'^{{{num}}}')
        for char, num in self._subscript_map.items():
            result = result.replace(char, f'_{{{num}}}')
        for char, latex in self._operator_map.items():
            result = result.replace(char, ' ' + latex + ' ')
        for char, latex in self._greek_map.items():
            result = result.replace(char, ' ' + latex + ' ')
        return result

    def _replace_functions(self, text: str) -> str:
        result = text
        for func in self._function_names:
            pattern = re.compile(rf'(?<!\\){func}\b', re.IGNORECASE)
            replacement = lambda m, f=func: '\\' + f
            result = pattern.sub(replacement, result)
        return result

    def _replace_fractions(self, text: str) -> str:
        def replace_frac(match):
            return '\\frac{' + match.group(1) + '}{' + match.group(2) + '}'
        return self._fraction_pattern.sub(replace_frac, text)

    def _replace_sqrt(self, text: str) -> str:
        def replace_sq(match):
            return '\\sqrt{' + match.group(1) + '}'
        return self._sqrt_pattern.sub(replace_sq, text)

    def _normalize_exponents(self, text: str) -> str:
        result = text
        i = 0
        while i < len(result):
            if result[i] == '^' or result[i] == '_':
                char = result[i]
                i += 1
                if i < len(result) and result[i] == '{':
                    i += 1
                    while i < len(result) and result[i] != '}':
                        i += 1
                    i += 1
                else:
                    if i < len(result):
                        content = result[i]
                        result = result[:i-1] + char + '{' + content + '}' + result[i+1:]
                        i += 2
                    else:
                        i += 1
            else:
                i += 1
        return result

    def _normalize_spacing(self, text: str) -> str:
        result = text
        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\s*([+\-*/=<>])\s*', r' \1 ', result)

        def add_space(match):
            return ' ' + match.group(0) + ' '
        result = self._latex_cmd_pattern.sub(add_space, result)

        result = re.sub(r'\s+', ' ', result)
        result = re.sub(r'\(\s*', '(', result)
        result = re.sub(r'\s*\)', ')', result)
        result = re.sub(r'\{\s*', '{', result)
        result = re.sub(r'\s*\}', '}', result)
        return result.strip()

    def _extract_formulas(self, text: str) -> List[Tuple[int, int, str]]:
        formulas = []
        for match in self._formula_boundary.finditer(text):
            formulas.append((match.start(), match.end(), match.group()))
        return formulas

    def _strip_formula_boundaries(self, formula: str) -> str:
        stripped = formula
        if stripped.startswith('$') and stripped.endswith('$'):
            stripped = stripped[1:-1]
        elif stripped.startswith('\\[') and stripped.endswith('\\]'):
            stripped = stripped[2:-2]
        elif stripped.startswith('\\(') and stripped.endswith('\\)'):
            stripped = stripped[2:-2]
        return stripped.strip()

    def _add_formula_boundaries(self, formula: str) -> str:
        return '$' + formula + '$'

    def normalize_formula(self, formula: str, keep_boundaries: bool = True) -> str:
        stripped = self._strip_formula_boundaries(formula)
        normalized = stripped

        normalized = self._replace_sqrt(normalized)
        normalized = self._replace_special_chars(normalized)
        normalized = self._replace_functions(normalized)
        normalized = self._replace_fractions(normalized)
        normalized = self._normalize_exponents(normalized)
        normalized = self._normalize_spacing(normalized)

        if keep_boundaries:
            normalized = self._add_formula_boundaries(normalized)

        return normalized

    def normalize_text(self, text: str) -> str:
        formulas = self._extract_formulas(text)
        if not formulas:
            return text

        result = text
        offset = 0
        for start, end, formula in formulas:
            normalized = self.normalize_formula(formula)
            result = result[:start + offset] + normalized + result[end + offset:]
            offset += len(normalized) - (end - start)

        return result

    def normalize(self, text: str) -> str:
        return self.normalize_text(text)

    def are_formulas_equivalent(self, formula1: str, formula2: str) -> bool:
        norm1 = self.normalize_formula(formula1, keep_boundaries=False)
        norm2 = self.normalize_formula(formula2, keep_boundaries=False)
        return norm1 == norm2

    def formula_similarity(self, formula1: str, formula2: str) -> float:
        norm1 = self.normalize_formula(formula1, keep_boundaries=False)
        norm2 = self.normalize_formula(formula2, keep_boundaries=False)

        if norm1 == norm2:
            return 1.0

        tokens1 = set(norm1.split())
        tokens2 = set(norm2.split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        jaccard = len(intersection) / len(union)

        return jaccard
