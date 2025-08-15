from __future__ import annotations

from typing import Optional, Tuple

from .models import AntibodyRecord, PackageOption


def _amount_ug_from(concentration_mg_per_ml: Optional[float], volume_ul: Optional[float], fallback_amount_ug: Optional[float]) -> Optional[float]:
	if fallback_amount_ug is not None:
		return fallback_amount_ug
	if concentration_mg_per_ml is not None and volume_ul is not None:
		# mg/mL * uL = ug
		return concentration_mg_per_ml * volume_ul
	return None


def pick_best_package(record: AntibodyRecord, min_amount_ug: float = 10.0) -> Optional[Tuple[float, float, Optional[str], Optional[str]]]:
	"""Return (amount_ug, price, currency, label) for the smallest package meeting the minimum.
	Falls back to the record-level fields when no package options are present.
	"""
	candidates: list[Tuple[float, float, Optional[str], Optional[str]]] = []

	# Consider package options
	for pkg in record.package_options or []:
		amt = _amount_ug_from(pkg.concentration_mg_per_ml, pkg.volume_ul, pkg.amount_ug)
		if amt is None or amt < min_amount_ug:
			continue
		if pkg.price is None:
			continue
		candidates.append((amt, float(pkg.price), pkg.currency, pkg.label))

	# Consider the primary record as a candidate
	rec_amt = _amount_ug_from(record.concentration_mg_per_ml, record.volume_ul, record.amount_ug)
	if rec_amt is not None and rec_amt >= min_amount_ug and record.price is not None:
		candidates.append((rec_amt, float(record.price), record.currency, record.size))

	if not candidates:
		return None

	# Choose smallest amount >= min; if tie on amount, choose lower price
	candidates.sort(key=lambda x: (x[0], x[1]))
	return candidates[0]
