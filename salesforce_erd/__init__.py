import json
from typing import List

import pandas as pd
from simple_salesforce import Salesforce


def read_config(config_file) -> dict:
    with open(config_file, "r") as file:
        config_data = json.load(file)
        return config_data


def get_instance(user: str, password: str, token: str) -> Salesforce:
    return Salesforce(
        username=user,
        password=password,
        security_token=token,
    )


def fields_of(
    table_name: str, session: Salesforce, metadata: bool = False
) -> List[str]:
    # Column discovery for a salesforce table
    # Note: no `*` for selection in salesforce, you must know columns in advance.
    table_meta = session.__getattr__(table_name).describe()
    if metadata:
        metaframe = pd.DataFrame.from_records(
            [
                {k: column_meta[k] for k in column_meta.keys()}
                for column_meta in table_meta["fields"]
            ]
        )
        return metaframe.fillna(value=pd.NA)
    else:
        return [column_meta["name"] for column_meta in table_meta["fields"]]


def show_tables(sf) -> pd.DataFrame:
    db_meta = sf.describe()
    tables_meta = db_meta.pop("sobjects")
    tables_meta = pd.DataFrame(tables_meta).fillna(value=pd.NA)
    return tables_meta


def filter_tables(tables: pd.DataFrame, names=List[str]) -> pd.DataFrame:
    return tables[tables["name"].isin(names)]
