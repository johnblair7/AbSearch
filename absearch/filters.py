from __future__ import annotations

from typing import Iterable, List

from .models import AntibodyRecord, Criteria


def _computed_amount_ug(record: AntibodyRecord) -> float | None:
	if record.amount_ug is not None:
		return record.amount_ug
	if record.concentration_mg_per_ml is not None and record.volume_ul is not None:
		# mg/mL * uL = (mg/mL) * (uL) = mg * (uL/mL)
		# 1 mL = 1000 uL, so multiply by (uL / 1000) to get mg, then *1000 to ug → net: mg/mL * uL = ug
		return record.concentration_mg_per_ml * record.volume_ul
	return None


def record_matches_criteria(record: AntibodyRecord, criteria: Criteria) -> bool:
	if criteria.species_reactivity:
		if not set(x.lower() for x in (record.validated_reactivity or [])).intersection(
			set(x.lower() for x in criteria.species_reactivity)
		):
			return False

	if criteria.host_species:
		if record.host_species is None or record.host_species.lower() not in (
			x.lower() for x in criteria.host_species
		):
			return False

	if criteria.clonality:
		if record.clonality is None or record.clonality.lower() not in (
			x.lower() for x in criteria.clonality
		):
			return False

	if criteria.applications:
		if not set(x.lower() for x in (record.applications or [])).issuperset(
			set(x.lower() for x in criteria.applications)
		):
			return False

	if criteria.conjugation:
		if record.conjugation is None or record.conjugation.lower() not in (
			x.lower() for x in criteria.conjugation
		):
			return False

	if criteria.min_citations is not None:
		if record.citations_count is None or record.citations_count < criteria.min_citations:
			return False

	if criteria.max_price is not None:
		if record.price is not None and record.price > criteria.max_price:
			return False

	if criteria.min_amount_ug is not None:
		amt = _computed_amount_ug(record)
		if amt is None or amt < criteria.min_amount_ug:
			return False

	return True


def filter_records(records: Iterable[AntibodyRecord], criteria: Criteria) -> List[AntibodyRecord]:
	return [r for r in records if record_matches_criteria(r, criteria)]
