from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl


class PackageOption(BaseModel):
	label: Optional[str] = None
	amount_ug: Optional[float] = None
	price: Optional[float] = None
	currency: Optional[str] = None
	concentration_mg_per_ml: Optional[float] = None
	volume_ul: Optional[float] = None


class AntibodyRecord(BaseModel):
	vendor: str
	catalog_number: str = Field(description="Vendor catalog or SKU identifier")
	name: str
	target: str

	url: Optional[HttpUrl] = None
	datasheet_url: Optional[HttpUrl] = None

	host_species: Optional[str] = None
	clonality: Optional[str] = Field(default=None, description="monoclonal or polyclonal")
	clone: Optional[str] = None
	isotype: Optional[str] = None

	applications: List[str] = Field(default_factory=list)
	validated_reactivity: List[str] = Field(default_factory=list)

	conjugation: Optional[str] = None
	size: Optional[str] = None
	price: Optional[float] = None
	currency: Optional[str] = None

	# Solution / formulation
	formulation: Optional[str] = None
	is_bsa_free: Optional[bool] = None
	is_gelatin_free: Optional[bool] = None
	is_ascites_free: Optional[bool] = None

	# Amount-related (selected/primary option)
	amount_ug: Optional[float] = None
	concentration_mg_per_ml: Optional[float] = None
	volume_ul: Optional[float] = None

	# Optional package options for multi-size products
	package_options: List[PackageOption] = Field(default_factory=list)

	citations_count: Optional[int] = None
	validation_images: Optional[int] = None

	notes: Optional[str] = None
	meta: Dict[str, str] = Field(default_factory=dict)


class Criteria(BaseModel):
	species_reactivity: Optional[List[str]] = None
	host_species: Optional[List[str]] = None
	clonality: Optional[List[str]] = None
	applications: Optional[List[str]] = None
	conjugation: Optional[List[str]] = None

	min_citations: Optional[int] = None
	max_price: Optional[float] = None
	min_amount_ug: Optional[float] = None
