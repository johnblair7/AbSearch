from __future__ import annotations

from typing import Iterable, List
import re

from .models import AntibodyRecord


# Phrase-level synonyms searched across the full string (case-insensitive)
_PHRASE_SYNONYMS: list[tuple[re.Pattern, str]] = [
	(re.compile(r"\bintracellular\s*flow\b", re.I), "ICFC"),
	(re.compile(r"\bflow\s*cytometry\s*\(\s*intracellular\s*\)\b", re.I), "ICFC"),
	(re.compile(r"\bflow\s*cytometry,?\s*intracellular\b", re.I), "ICFC"),
	(re.compile(r"\bpermeabil(ized|isation|ization)\s*flow\b", re.I), "ICFC"),
	(re.compile(r"\bICFC\b", re.I), "ICFC"),

	(re.compile(r"\bimmunocytochemistry\b", re.I), "ICC"),
	(re.compile(r"\bICC\b", re.I), "ICC"),
	(re.compile(r"\bICC\s*\/\s*IF\b", re.I), "ICC"),
	(re.compile(r"\bIF-?ICC\b", re.I), "ICC"),

	(re.compile(r"\bimmunohistochemistry\b", re.I), "IHC"),
	(re.compile(r"\bIHC\b", re.I), "IHC"),
	(re.compile(r"\bIHC-?P\b", re.I), "IHC"),
	(re.compile(r"\bIHC-?Fr\b", re.I), "IHC"),

	(re.compile(r"\bwestern\s*blot\b", re.I), "WB"),
	(re.compile(r"\bWB\b", re.I), "WB"),

	(re.compile(r"\bimmunofluorescence\b", re.I), "IF"),
	(re.compile(r"\bIF\b", re.I), "IF"),

	(re.compile(r"\bflow\s*cytometry\b", re.I), "FC"),
	(re.compile(r"\bFACS\b", re.I), "FC"),
	(re.compile(r"\bFCM\b", re.I), "FC"),

	(re.compile(r"\bELISA\b", re.I), "ELISA"),
	(re.compile(r"\bsandwich\s*ELISA\b", re.I), "ELISA"),
	(re.compile(r"\bcompetitive\s*ELISA\b", re.I), "ELISA"),

	(re.compile(r"\bimmunoprecipitation\b", re.I), "IP"),
	(re.compile(r"\bIP\b", re.I), "IP"),

	(re.compile(r"\bChIP(-seq)?\b", re.I), "ChIP"),
	(re.compile(r"\bRIP\b", re.I), "RIP"),
	(re.compile(r"\bdot\s*blot\b", re.I), "DotBlot"),
]

# Priority only affects these; others are ranked below
_PRIORITY = ["ICFC", "ICC", "IHC"]


def normalize_applications(apps: Iterable[str]) -> List[str]:
	codes: list[str] = []
	for app in apps or []:
		text = (app or "").strip()
		if not text:
			continue
		for pat, code in _PHRASE_SYNONYMS:
			if pat.search(text):
				codes.append(code)
		# Also split on common delimiters and re-check small tokens
		for token in re.split(r"[\s,\/]+", text):
			token = token.strip()
			if not token:
				continue
			for pat, code in _PHRASE_SYNONYMS:
				if pat.fullmatch(token):
					codes.append(code)
	# Deduplicate while preserving order
	seen = set()
	ordered: list[str] = []
	for c in codes:
		if c not in seen:
			seen.add(c)
			ordered.append(c)
	return ordered


def compute_application_score(apps: Iterable[str]) -> int:
	norm = set(normalize_applications(apps))
	score = 0
	if "ICFC" in norm:
		score = max(score, 3)
	if "ICC" in norm:
		score = max(score, 2)
	if "IHC" in norm:
		score = max(score, 1)
	return score


def sort_records_by_priority(records: List[AntibodyRecord]) -> List[AntibodyRecord]:
	def sort_key(r: AntibodyRecord):
		bsa_bonus = 1 if r.is_bsa_free else 0 if r.is_bsa_free is not None else 0
		gel_bonus = 1 if r.is_gelatin_free else 0 if r.is_gelatin_free is not None else 0
		ascites_bonus = 1 if r.is_ascites_free else 0 if r.is_ascites_free is not None else 0
		app_score = compute_application_score(r.applications)
		cit = r.citations_count or 0
		price = r.price if r.price is not None else float("inf")
		# Sort: add formulation bonuses (higher is better), then app_score desc, citations desc, price asc
		return (-(bsa_bonus + gel_bonus + ascites_bonus), -app_score, -cit, price, r.vendor, r.catalog_number)

	return sorted(records, key=sort_key)
