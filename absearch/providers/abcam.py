from __future__ import annotations

import re
from typing import Iterable, List, Optional

import httpx
from bs4 import BeautifulSoup

from ..models import AntibodyRecord
from ..headless import fetch_html


_ABCAM_PRIMARY_URLS = [
	"https://www.abcam.com/primary-antibodies",
	"https://www.abcam.com/products/primary-antibodies",
]

_APP_PATTERNS = [
	("ICFC", [r"intracellular flow", r"icfc", r"permeabil(ized|isation|ization) flow"]),
	("ICC", [r"immunocytochemistry", r"\bicc\b", r"icc\s*\/\s*if", r"if-?icc"]),
	("IHC", [r"immunohistochemistry", r"\bihc\b", r"ihc-?p", r"ihc-?fr"]),
	("WB", [r"western blot", r"\bwb\b"]),
	("IF", [r"immunofluorescence", r"\bif\b"]),
	("FC", [r"flow cytometry", r"\bfacs\b", r"\bfcm\b"]),
]


class AbcamProvider:
	name = "abcam"

	def __init__(self, timeout_seconds: float = 20.0, use_headless: bool = False) -> None:
		self._client = httpx.Client(timeout=timeout_seconds, headers={
			"User-Agent": "AbSearch/0.1 (+https://github.com/johnblair7/AbSearch)",
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
		})
		self._use_headless = use_headless

	def _build_candidate_urls(self, target: str) -> List[str]:
		params = [
			("keywords", target),
			("q", target),
			("Keywords", target),
		]
		urls: List[str] = []
		for base in _ABCAM_PRIMARY_URLS:
			for key, val in params:
				urls.append(f"{base}?{key}={httpx.QueryParams({key: val})[key]}")
		return urls

	def _extract_catalog(self, text: str, href: Optional[str]) -> Optional[str]:
		patterns = [r"\bab\d{3,6}\b", r"/ab\d{3,6}\b"]
		for pat in patterns:
			if text:
				m = re.search(pat, text, flags=re.IGNORECASE)
				if m:
					return m.group(0).lstrip("/")
			if href:
				m = re.search(pat, href, flags=re.IGNORECASE)
				if m:
					return m.group(0).lstrip("/")
		return None

	def _parse_reactivity(self, item_text: str) -> List[str]:
		reactivity = []
		for sp in ["Human", "Mouse", "Rat", "Monkey", "Zebrafish", "Chicken", "Pig", "Dog"]:
			if re.search(rf"\b{re.escape(sp)}\b", item_text, re.IGNORECASE):
				reactivity.append(sp)
		return reactivity

	def _parse_clonality(self, item_text: str) -> Optional[str]:
		if re.search(r"\bmono\w*clonal\b", item_text, re.IGNORECASE):
			return "Monoclonal"
		if re.search(r"\bpoly\w*clonal\b", item_text, re.IGNORECASE):
			return "Polyclonal"
		return None

	def _parse_clone(self, item_text: str) -> Optional[str]:
		m = re.search(r"\[\s*([A-Za-z0-9\-]+)\s*\]", item_text)
		if m:
			return m.group(1)
		return None

	def _parse_apps(self, element: BeautifulSoup) -> List[str]:
		text = element.get_text(" ", strip=True)
		apps: List[str] = []
		lower = text.lower()
		for label, pats in _APP_PATTERNS:
			for pat in pats:
				if re.search(pat, lower):
					apps.append(label)
		for small in element.select("small, span, .badge, .chip"):
			lt = (small.get_text(" ", strip=True) or "").lower()
			for label, pats in _APP_PATTERNS:
				for pat in pats:
					if re.search(pat, lt):
						apps.append(label)
		return list(dict.fromkeys(apps))

	def _parse_formulation(self, text: str) -> tuple[Optional[str], Optional[bool], Optional[bool], Optional[bool]]:
		formulation = None
		is_bsa_free: Optional[bool] = None
		is_gel_free: Optional[bool] = None
		is_asc_free: Optional[bool] = None
		lower = text.lower()
		if "bsa-free" in lower or "bsa free" in lower or "without bsa" in lower:
			is_bsa_free = True
		if "gelatin-free" in lower or "gelatin free" in lower or "without gelatin" in lower:
			is_gel_free = True
		if "ascites-free" in lower or "ascites free" in lower or "without ascites" in lower:
			is_asc_free = True
		if "bsa" in lower and is_bsa_free is None:
			is_bsa_free = False
		if "gelatin" in lower and is_gel_free is None:
			is_gel_free = False
		if "ascites" in lower and is_asc_free is None:
			is_asc_free = False
		m = re.search(r"(pbs|tris|glycine|azide|glycerol|gelatin|bsa)[^|,;]*", lower)
		if m:
			formulation = m.group(0)
		return formulation, is_bsa_free, is_gel_free, is_asc_free

	def _parse_listings(self, html: str, target: str) -> List[AntibodyRecord]:
		soup = BeautifulSoup(html, "html.parser")
		results: List[AntibodyRecord] = []

		for card in soup.select("a, div"):
			text = card.get_text(" ", strip=True)
			href = card.get("href") if card.name == "a" else None
			if not text:
				continue
			if href is None:
				link = card.select_one("a[href]")
				href = link.get("href") if link else None
			if not href:
				continue
			if "/products/" not in href and "/ab" not in href.lower():
				continue

			catalog = self._extract_catalog(text, href)
			if not catalog:
				continue

			url = href
			if url.startswith("/"):
				url = f"https://www.abcam.com{url}"

			name = text.split("|")[0][:200]
			reactivity = self._parse_reactivity(text)
			clonality = self._parse_clonality(text)
			clone = self._parse_clone(text) if clonality == "Monoclonal" else None
			apps = self._parse_apps(card)
			formulation, is_bsa_free, is_gel_free, is_asc_free = self._parse_formulation(text)

			record = AntibodyRecord(
				vendor="Abcam",
				catalog_number=catalog,
				name=name,
				target=target,
				url=url,
				validated_reactivity=reactivity,
				clonality=clonality,
				clone=clone,
				applications=apps,
				formulation=formulation,
				is_bsa_free=is_bsa_free,
				is_gelatin_free=is_gel_free,
				is_ascites_free=is_asc_free,
			)
			results.append(record)

		return results

	def _fetch_listing_html(self, url: str) -> Optional[str]:
		try:
			if self._use_headless:
				return fetch_html(url, wait_selector="body")
			resp = self._client.get(url)
			if resp.status_code == 200:
				return resp.text
		except Exception:
			return None
		return None

	def search(self, target: str) -> Iterable[AntibodyRecord]:
		urls = self._build_candidate_urls(target)
		seen_catalogs = set()
		collected: List[AntibodyRecord] = []
		for url in urls:
			html = self._fetch_listing_html(url)
			if not html:
				continue
			records = self._parse_listings(html, target)
			for r in records:
				if r.catalog_number.lower() in seen_catalogs:
					continue
				seen_catalogs.add(r.catalog_number.lower())
				collected.append(r)
		return collected
