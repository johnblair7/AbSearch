from __future__ import annotations

from typing import Iterable, Protocol

from ..models import AntibodyRecord


class AntibodyProvider(Protocol):
	name: str

	def search(self, target: str) -> Iterable[AntibodyRecord]:
		...
