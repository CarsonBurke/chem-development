from __future__ import annotations

from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from .client import ChebiClient


mcp = FastMCP("chebi-mcp")
client = ChebiClient()


@mcp.tool()
def chebi_es_search(term: str, page: int = 1, size: int = 15) -> Any:
    """Search ChEBI by name, synonym, ID, formula, InChI, SMILES, CAS, cross-reference, or definition text."""
    return client.es_search(term=term, page=page, size=size)


@mcp.tool()
def chebi_get_compound(
    chebi_id: str,
    only_ontology_parents: bool = False,
    only_ontology_children: bool = False,
) -> Any:
    """Retrieve full ChEBI compound details for a ChEBI identifier."""
    return client.get_compound(
        chebi_id,
        only_ontology_parents=only_ontology_parents,
        only_ontology_children=only_ontology_children,
    )


@mcp.tool()
def chebi_get_compounds(chebi_ids: list[str]) -> Any:
    """Retrieve full ChEBI compound details for multiple ChEBI identifiers."""
    return client.get_compounds(chebi_ids)


@mcp.tool()
def chebi_advanced_search(
    specification: dict[str, Any],
    three_star_only: bool = True,
    has_structure: bool | None = None,
    page: int = 1,
    size: int = 15,
    download: bool = False,
) -> Any:
    """Run a ChEBI advanced search using ontology, formula, mass, charge, database-name, or text specifications."""
    return client.advanced_search(
        specification,
        three_star_only=three_star_only,
        has_structure=has_structure,
        page=page,
        size=size,
        download=download,
    )


@mcp.tool()
def chebi_sources_list() -> Any:
    """Return source names supported by ChEBI advanced search."""
    return client.sources_list()


@mcp.tool()
def chebi_ontology_parents(chebi_id: str) -> Any:
    """Return direct ontology parents for a ChEBI compound."""
    return client.ontology_parents(chebi_id)


@mcp.tool()
def chebi_ontology_children(chebi_id: str) -> Any:
    """Return direct ontology children for a ChEBI compound."""
    return client.ontology_children(chebi_id)


@mcp.tool()
def chebi_ontology_all_children_in_path(
    relation: Literal[
        "has_functional_parent",
        "has_parent_hydride",
        "has_part",
        "has_role",
        "is_a",
        "is_conjugate_acid_of",
        "is_conjugate_base_of",
        "is_enantiomer_of",
        "is_part_of",
        "is_substituent_group_from",
        "is_tautomer_of",
    ],
    entity: str,
    three_star_only: bool = True,
    has_structure: bool | None = None,
    page: int = 1,
    size: int = 15,
    download: bool = False,
) -> Any:
    """Find all compounds connected to an ontology entity through a relation path."""
    return client.ontology_all_children_in_path(
        relation,
        entity,
        three_star_only=three_star_only,
        has_structure=has_structure,
        page=page,
        size=size,
        download=download,
    )


@mcp.tool()
def chebi_structure_search(
    smiles: str,
    search_type: Literal["connectivity", "similarity", "substructure"],
    similarity: float | None = None,
    three_star_only: bool = True,
    page: int = 1,
    size: int = 15,
    download: bool = False,
) -> Any:
    """Search ChEBI by molecular structure using connectivity, similarity, or substructure mode."""
    return client.structure_search(
        smiles,
        search_type,
        similarity=similarity,
        three_star_only=three_star_only,
        page=page,
        size=size,
        download=download,
    )


@mcp.tool()
def chebi_compound_structure_svg(chebi_id: str) -> str:
    """Return raw SVG for a compound's default ChEBI structure."""
    return client.compound_structure_svg(chebi_id)


@mcp.tool()
def chebi_structure_svg(structure_id: int) -> str:
    """Return raw SVG for a ChEBI structure primary key."""
    return client.structure_svg(structure_id)


@mcp.tool()
def chebi_molfile(compound_id: int) -> str:
    """Return the molfile for a ChEBI compound primary key."""
    return client.molfile(compound_id)


@mcp.tool()
def chebi_avg_mass(molfile_or_structure: str) -> str:
    """Calculate average mass from a molfile or structure string."""
    return client.structure_calculation("/structure-calculations/avg-mass/", molfile_or_structure)


@mcp.tool()
def chebi_avg_mass_from_formula(formula: str) -> str:
    """Calculate average mass from a formula."""
    return client.structure_calculation("/structure-calculations/avg-mass/from-formula/", formula)


@mcp.tool()
def chebi_monoisotopic_mass(molfile_or_structure: str) -> str:
    """Calculate monoisotopic mass from a molfile or structure string."""
    return client.structure_calculation("/structure-calculations/monoisotopic-mass/", molfile_or_structure)


@mcp.tool()
def chebi_monoisotopic_mass_from_formula(formula: str) -> str:
    """Calculate monoisotopic mass from a formula."""
    return client.structure_calculation("/structure-calculations/monoisotopic-mass/from-formula/", formula)


@mcp.tool()
def chebi_mol_formula(molfile_or_structure: str) -> str:
    """Calculate molecular formula from a molfile or structure string."""
    return client.structure_calculation("/structure-calculations/mol-formula/", molfile_or_structure)


@mcp.tool()
def chebi_net_charge(molfile_or_structure: str) -> str:
    """Calculate net charge from a molfile or structure string."""
    return client.structure_calculation("/structure-calculations/net-charge/", molfile_or_structure)


@mcp.tool()
def chebi_depict_indigo_png(
    molfile_or_structure: str,
    width: int = 300,
    height: int = 300,
    transbg: bool = False,
) -> dict[str, str]:
    """Render a molfile or structure string to a PNG returned as base64."""
    return client.depict_indigo_png(molfile_or_structure, width=width, height=height, transbg=transbg)


@mcp.tool()
def chebi_chemical_card(query_or_chebi_id: str) -> dict[str, Any]:
    """Build a normalized ChEBI chemical card from a name, synonym, CAS, formula, SMILES, InChIKey, or ChEBI ID."""
    return client.chemical_card(query_or_chebi_id)


@mcp.tool()
def chebi_role_alternatives(
    role_chebi_id: str,
    page: int = 1,
    size: int = 25,
    three_star_only: bool = True,
) -> Any:
    """Find compounds sharing a ChEBI role, such as food acidity regulator CHEBI:64049."""
    return client.ontology_all_children_in_path(
        "has_role",
        role_chebi_id,
        page=page,
        size=size,
        three_star_only=three_star_only,
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()

