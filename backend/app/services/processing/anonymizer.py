import re
import logging
from typing import Dict, Any, Set

logger = logging.getLogger(__name__)


class PIIAnonymizer:

    def __init__(self):
        self.patterns = self._compile_patterns()
        logger.info("PII Anonymizer initialized")

    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        return {
            "cpf": re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"),
            "phone": re.compile(r"\(?\d{2}\)?\s?\d{4,5}-?\d{4}\b"),
            "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
            "rg": re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}-?\d{1}\b"),
            "address": re.compile(
                r"\b(Rua|Avenida|Av\.|R\.|Travessa|Trav\.|Alameda)\s+[A-Z][a-zA-Z\s]+,?\s*\d+",
                re.IGNORECASE,
            ),
            "cep": re.compile(r"\b\d{5}-?\d{3}\b"),
            "credit_card": re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),
            "possible_name": re.compile(
                r"\b(?:Sr\.|Sra\.|Dr\.|Dra\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"
            ),
        }

    def anonymize_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Anonymizing summary")

        anonymizations_found = set()
        anonymized_summary = self._anonymize_recursive(summary, anonymizations_found)

        if anonymizations_found:
            logger.warning(
                f"PII found and anonymized: {', '.join(anonymizations_found)}"
            )
        else:
            logger.info("No PII detected in summary")

        return anonymized_summary

    def _anonymize_recursive(self, obj: Any, anonymizations_found: Set[str]) -> Any:
        if isinstance(obj, dict):
            return {
                key: self._anonymize_recursive(value, anonymizations_found)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [
                self._anonymize_recursive(item, anonymizations_found) for item in obj
            ]
        elif isinstance(obj, str):
            return self._anonymize_string(obj, anonymizations_found)
        else:
            return obj

    def _anonymize_string(self, text: str, anonymizations_found: Set[str]) -> str:
        original_text = text

        replacements = {
            "cpf": "[CPF REMOVIDO]",
            "phone": "[TELEFONE REMOVIDO]",
            "email": "[EMAIL REMOVIDO]",
            "rg": "[RG REMOVIDO]",
            "address": "[ENDEREÇO REMOVIDO]",
            "cep": "[CEP REMOVIDO]",
            "credit_card": "[CARTÃO REMOVIDO]",
            "possible_name": "Paciente",
        }

        for pattern_name, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                anonymizations_found.add(pattern_name)
                replacement = replacements[pattern_name]
                text = pattern.sub(replacement, text)

        text = self._replace_potential_names(text, anonymizations_found)

        if text != original_text:
            logger.debug(f"Anonymized: {original_text[:50]}... -> {text[:50]}...")

        return text

    def _replace_potential_names(
        self, text: str, anonymizations_found: Set[str]
    ) -> str:
        common_words = {
            "Paciente",
            "Terapeuta",
            "Janeiro",
            "Fevereiro",
            "Março",
            "Abril",
            "Maio",
            "Junho",
            "Julho",
            "Agosto",
            "Setembro",
            "Outubro",
            "Novembro",
            "Dezembro",
            "Segunda",
            "Terça",
            "Quarta",
            "Quinta",
            "Sexta",
            "Sábado",
            "Domingo",
            "Brasil",
            "Natal",
            "Páscoa",
        }

        pattern = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2})\b")

        def replace_if_name(match):
            phrase = match.group(1)
            words = phrase.split()

            if any(word in common_words for word in words):
                return phrase

            anonymizations_found.add("potential_name")
            return "Paciente"

        return pattern.sub(replace_if_name, text)

    def validate_anonymization(self, summary: Dict[str, Any]) -> bool:
        anonymizations_found = set()
        self._check_for_pii_recursive(summary, anonymizations_found)

        if anonymizations_found:
            logger.error(
                f"Validation failed: PII still present: {', '.join(anonymizations_found)}"
            )
            return False

        logger.info("Validation passed: No PII detected")
        return True

    def _check_for_pii_recursive(self, obj: Any, pii_found: Set[str]):
        if isinstance(obj, dict):
            for value in obj.values():
                self._check_for_pii_recursive(value, pii_found)
        elif isinstance(obj, list):
            for item in obj:
                self._check_for_pii_recursive(item, pii_found)
        elif isinstance(obj, str):
            self._check_string_for_pii(obj, pii_found)

    def _check_string_for_pii(self, text: str, pii_found: Set[str]):
        for pattern_name, pattern in self.patterns.items():
            if pattern.search(text):
                pii_found.add(pattern_name)
