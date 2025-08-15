from __future__ import annotations

import json
from typing import List, Optional

import typer
from rich import box
from rich.console import Console
from rich.table import Table

from .filters import filter_records
from .models import Criteria
from .search import get_providers, search_all_sync
from .ordering import sort_records_by_priority, normalize_applications
from .selection import pick_best_package

console = Console()


def _render_table(records) -> None:
	table = Table(show_lines=False, box=box.SIMPLE_HEAVY)
	table.add_column("Vendor", style="bold")
	table.add_column("Catalog")
	table.add_column("Name")
	table.add_column("Target")
	table.add_column("Host")
	table.add_column("Clonality")
	table.add_column("Clone")
	table.add_column("Apps")
	table.add_column("Reactivity")
	table.add_column("Conj")
	table.add_column("Formulation")
	table.add_column("BSA-free")
	table.add_column("Gelatin-free")
	table.add_column("Ascites-free")
	table.add_column("Amount (ug)")
	table.add_column("Conc (mg/mL)")
	table.add_column("Vol (uL)")
	table.add_column("Best Amount (ug)")
	table.add_column("Best Price")
	table.add_column("Citations")

	for r in records:
		price_str = "" if r.price is None else f"{r.price:.2f} {r.currency or ''}".strip()
		apps_str = ",".join(normalize_applications(r.applications))
		react_str = ",".join(r.validated_reactivity)
		cit_str = "" if r.citations_count is None else str(r.citations_count)
		bsa_str = "Yes" if r.is_bsa_free else ("No" if r.is_bsa_free is not None else "")
		gel_str = "Yes" if r.is_gelatin_free else ("No" if r.is_gelatin_free is not None else "")
		asc_str = "Yes" if r.is_ascites_free else ("No" if r.is_ascites_free is not None else "")
		form_str = r.formulation or ""
		amt_str = "" if r.amount_ug is None else f"{r.amount_ug:.0f}"
		conc_str = "" if r.concentration_mg_per_ml is None else f"{r.concentration_mg_per_ml:g}"
		vol_str = "" if r.volume_ul is None else f"{r.volume_ul:g}"

		best = pick_best_package(r)
		best_amt_str = best_price_str = ""
		if best is not None:
			best_amt, best_price, best_currency, _ = best
			best_amt_str = f"{best_amt:.0f}"
			best_price_str = f"{best_price:.2f} {best_currency or ''}".strip()

		table.add_row(
			r.vendor,
			r.catalog_number,
			r.name,
			r.target,
			r.host_species or "",
			r.clonality or "",
			r.clone or "",
			apps_str,
			react_str,
			r.conjugation or "",
			form_str,
			bsa_str,
			gel_str,
			asc_str,
			amt_str,
			conc_str,
			vol_str,
			best_amt_str,
			best_price_str,
			cit_str,
		)

	console.print(table)


def main(
	target: str = typer.Argument(..., help="Protein or gene name to search for (e.g., TP53)"),
	applications: Optional[List[str]] = typer.Option(None, "--applications", help="Required applications, e.g., WB IHC IF"),
	clonality: Optional[List[str]] = typer.Option(None, "--clonality", help="Monoclonal/Polyclonal"),
	host_species: Optional[List[str]] = typer.Option(None, "--host-species", help="Required host species (Rabbit, Mouse, etc.)"),
	species_reactivity: Optional[List[str]] = typer.Option(None, "--species-reactivity", help="Required validated reactivity (Human, Mouse, etc.)"),
	conjugation: Optional[List[str]] = typer.Option(None, "--conjugation", help="Required conjugations (HRP, Alexa488, etc.)"),
	min_citations: Optional[int] = typer.Option(None, "--min-citations", help="Minimum number of citations"),
	max_price: Optional[float] = typer.Option(None, "--max-price", help="Maximum price in vendor currency"),
	min_amount_ug: Optional[float] = typer.Option(10.0, "--min-amount-ug", help="Minimum amount of antibody in micrograms (default: 10)"),
	providers: Optional[List[str]] = typer.Option(None, "--providers", help="Provider names (default: abcam). Options: abcam, mock. Suffix ':headless' to enable headless for abcam."),
	headless: bool = typer.Option(False, "--headless", help="Enable headless browser rendering for supported providers"),
	json_out: bool = typer.Option(False, "--json", help="Output JSON instead of table"),
	csv_out: Optional[str] = typer.Option(None, "--csv", help="Write CSV to the given filepath"),
):
	"""Search antibody vendors and filter results by criteria."""
	# Default species reactivity to Human if not provided
	if not species_reactivity or len(species_reactivity) == 0:
		species_reactivity = ["Human"]

	criteria = Criteria(
		applications=applications or None,
		clonality=clonality or None,
		host_species=host_species or None,
		species_reactivity=species_reactivity or None,
		conjugation=conjugation or None,
		min_citations=min_citations,
		max_price=max_price,
		min_amount_ug=min_amount_ug,
	)

	provider_args = providers or ["abcam"]
	if headless:
		provider_args = [p if not p.lower().startswith("abcam") else "abcam:headless" for p in provider_args]
		if providers is None:
			provider_args = ["abcam:headless"]

	provider_instances = get_providers(provider_args)
	records: List = []
	for p in provider_instances:
		records.extend(search_all_sync(target, providers=[p]))

	filtered = filter_records(records, criteria)

	# Apply priority sorting with formulation bonuses and application priority
	sorted_records = sort_records_by_priority(filtered)

	if json_out:
		console.print_json(data=[r.model_dump(mode="json") for r in sorted_records])
		return

	if csv_out:
		import csv
		from pathlib import Path

		path = Path(csv_out)
		with path.open("w", newline="") as f:
			writer = csv.DictWriter(
				f,
				fieldnames=list(sorted_records[0].model_dump(mode="json").keys()) if sorted_records else ["vendor", "catalog_number"],
			)
			writer.writeheader()
			for r in sorted_records:
				writer.writerow(r.model_dump(mode="json"))
			console.print(f"Wrote {len(sorted_records)} records to {path}")
		return

	_render_table(sorted_records)


if __name__ == "__main__":
	typer.run(main)
