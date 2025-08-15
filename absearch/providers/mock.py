from __future__ import annotations

from typing import Iterable, List

from ..models import AntibodyRecord


class MockProvider:
	name = "mock"

	def search(self, target: str) -> Iterable[AntibodyRecord]:
		results: List[AntibodyRecord] = [
			AntibodyRecord(
				vendor="MockVendor",
				catalog_number="MV-TP53-003",
				name=f"Anti-{target} monoclonal antibody [ICFC-1]",
				target=target,
				url="https://example.com/antibody/mv-tp53-003",
				host_species="Mouse",
				clonality="Monoclonal",
				clone="ICFC-1",
				applications=["ICFC", "ICC", "IHC"],
				validated_reactivity=["Human"],
				conjugation=None,
				price=399.0,
				currency="USD",
				citations_count=10,
				formulation="PBS with 0.05% BSA",
				is_bsa_free=False,
				concentration_mg_per_ml=0.5,
				volume_ul=50,
			),
			AntibodyRecord(
				vendor="MockVendor",
				catalog_number="MV-TP53-004",
				name=f"Anti-{target} monoclonal antibody [ICFC-2] BSA-free",
				target=target,
				url="https://example.com/antibody/mv-tp53-004",
				host_species="Mouse",
				clonality="Monoclonal",
				clone="ICFC-2",
				applications=["ICFC"],
				validated_reactivity=["Human"],
				conjugation=None,
				price=420.0,
				currency="USD",
				citations_count=5,
				formulation="PBS, 0.02% sodium azide",
				is_bsa_free=True,
				amount_ug=15,
			),
			AntibodyRecord(
				vendor="MockVendor",
				catalog_number="MV-TP53-001",
				name=f"Anti-{target} monoclonal antibody [DO-7]",
				target=target,
				url="https://example.com/antibody/mv-tp53-001",
				host_species="Rabbit",
				clonality="Monoclonal",
				clone="DO-7",
				applications=["WB", "IHC", "IF"],
				validated_reactivity=["Human", "Mouse"],
				conjugation=None,
				price=349.0,
				currency="USD",
				citations_count=125,
				formulation="Tris-glycine with gelatin",
				is_bsa_free=False,
				concentration_mg_per_ml=1.0,
				volume_ul=5,  # only 5 ug equivalent
			),
			AntibodyRecord(
				vendor="MockVendor",
				catalog_number="MV-TP53-002",
				name=f"Anti-{target} polyclonal antibody",
				target=target,
				url="https://example.com/antibody/mv-tp53-002",
				host_species="Mouse",
				clonality="Polyclonal",
				clone=None,
				applications=["WB"],
				validated_reactivity=["Human"],
				conjugation="HRP",
				price=279.0,
				currency="USD",
				citations_count=32,
				formulation="PBS with 0.1% gelatin",
				is_bsa_free=False,
				amount_ug=8,
			),
		]
		return results
