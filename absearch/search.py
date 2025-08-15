from __future__ import annotations

from typing import List, Sequence

from .models import AntibodyRecord
from .providers import AbcamProvider, AntibodyProvider, MockProvider


def get_providers(names: Sequence[str] | None) -> List[AntibodyProvider]:
	if not names:
		return [AbcamProvider()]

	providers: List[AntibodyProvider] = []
	for n in names:
		use_headless = False
		name = n
		if ":" in n:
			name, _, mode = n.partition(":")
			use_headless = (mode.lower() == "headless")

		if name.lower() == "abcam":
			providers.append(AbcamProvider(use_headless=use_headless))
		elif name.lower() == "mock":
			providers.append(MockProvider())
	return providers


def search_all_sync(target: str, providers: Sequence[AntibodyProvider] | None = None) -> List[AntibodyRecord]:
	if providers is None or len(providers) == 0:
		providers = [AbcamProvider()]

	results: List[AntibodyRecord] = []
	for provider in providers:
		results.extend(list(provider.search(target)))
	return results
