import click
import pandas as pd
from tqdm import tqdm

from salesforce_erd import (
    fields_of,
    filter_tables,
    get_instance,
    read_config,
    show_tables,
)


@click.command()
@click.option(
    "--config-file",
    "-c",
    default="config.json",
    help="Path to the JSON configuration file",
)
def build_erd(config_file):
    conf = read_config(config_file)

    # Read Salesforce metadata
    sf = get_instance(conf.get("user"), conf.get("password"), conf.get("token"))
    tables_meta = show_tables(sf)

    # Filter tables
    tables = conf.get("tables", [])
    if len(tables) > 0:
        tables_meta = filter_tables(tables_meta, names=tables)

    # Generate PlantUML text for class diagram
    plantuml_code = write_header(conf.get("diagram_name"))

    for table in tqdm(tables_meta.name):
        # Get entity attributes
        columns_meta = fields_of(table, sf, metadata=True)
        columns_meta.soapType = columns_meta.soapType.str[4:]

        # Extract relations
        relation_meta = get_relations(columns_meta)

        # Entity
        plantuml_code += write_entity(table, columns_meta, relation_meta)

        # Relationship
        plantuml_code += write_relationship(tables, table, relation_meta)

        # Close E-R loop
        plantuml_code += "\n"

    # Footer
    plantuml_code += "@enduml"

    # Write output to file
    with open("salesforce_erd.puml", "w") as file:
        file.write(plantuml_code)


def write_relationship(tables, table, relation_meta) -> str:
    plantuml_code = ""
    relation_meta = (
        relation_meta.groupby("referenceTo")["relationshipName"]
        .agg(list)
        .str.join(", ")
        .reset_index()
    )  # Aggregate relations targetting same entity
    for _, relation in relation_meta.explode("referenceTo").iterrows():
        # Drop recursive relation and only specified table
        if (table != relation["referenceTo"]) and (
            relation["referenceTo"] in tables if len(tables) > 0 else True
        ):
            plantuml_code += f"{table} -left-> {relation['referenceTo']}\n"
    return plantuml_code


def write_entity(table, columns_meta, relation_meta) -> str:
    plantuml_code = f"class {table} {{\n"

    # Attributes loop
    for _, attribute in columns_meta.sort_values(by="name").iterrows():
        method_or_field = "{method} #" if attribute["calculated"] else "{field} +"
        bold_open_if_ID = "<b>" if attribute["soapType"] == "ID" else ""
        attribute_type = (
            attribute["soapType"]
            if attribute["type"].lower() == attribute["soapType"].lower()
            else f"{attribute['type']}<{attribute['soapType']}>"
        )
        bold_close_if_ID = "</b>" if attribute["soapType"] == "ID" else ""
        references = relation_meta.loc[
            relation_meta["name"] == attribute["name"], "referenceTo"
        ]
        if len(references) == 0:
            references = ["No reference found."]
        reference_to = (
            ":\n" + ", \n".join(map(lambda r: f"<b>{r}</b>", references))
            if attribute["type"].lower() == "reference"
            else ""
        )
        plantuml_code += f"  {method_or_field}{bold_open_if_ID}{attribute['name']}: {attribute_type}{bold_close_if_ID}{reference_to}\n"

    plantuml_code += f"}}\n"
    return plantuml_code


def get_relations(columns_meta) -> pd.DataFrame:
    relation_meta = columns_meta.loc[
        columns_meta.referenceTo.apply(len) > 0,
        ["name", "relationshipName", "referenceTo"],
    ]
    # Drop relationship with no name
    relation_meta = relation_meta.dropna(subset="relationshipName")
    # Flatten polymorphic relations
    relation_meta = relation_meta.explode("referenceTo")
    return relation_meta


def write_header(diagram_name) -> str:
    plantuml_code = (
        f"@startuml {diagram_name} - {pd.Timestamp.now().isoformat()[:10]}\n"
    )
    plantuml_code += "skinparam linetype ortho\n"  # °90 degree angle only for arrows
    plantuml_code += "hide empty methods\n"
    return plantuml_code


if __name__ == "__main__":
    build_erd()
