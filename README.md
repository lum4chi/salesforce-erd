# salesforce-erd
A tool to build your Salesforce instance Entity-Relationship Diagram.

## How to use
This tool is designed as a script to produce a [plantuml](https://plantuml.com/) text diagram based on Salesforce metadata. To achieve an actual drawing (an svg/png/pdf file) use the produced txt file as input for [plantuml tool](https://plantuml.com/starting).

## How to run
1. This project use [poetry](https://python-poetry.org/) to organize dependencies. Install it in your system before use.
2. Duplicate `config.json.template` and rename it in `config.json`. Then fill the requested variables:  
    a. `user`, `password`, `token` to connect to your Salesforce instance,  
    b. `diagram_name` is the name that you want to give to the UML diagram,  
    c. `tables` is the subset of entities that you want in your diagram (the full Salesforce instance it will have easily too much entities to be shown).  
3. Run `poetry run python build_erd.py` to execute the script. The first run will be longer because [poetry](https://python-poetry.org/) will create a dedicated environment with the necessary dependencies. Follow the provided instruction in order to build your diagram.
4. Output will be written into `salesforce_erd.puml` file. From here, you can invoke [plantuml](https://plantuml.com/) to transform the diagram in a visual format. 

### Example
Refer to [plantuml](https://plantuml.com/) documentation, but you probably need to tweak some option, like the maximum file size:
```bash
export PLANTUML_LIMIT_SIZE=32767
plantuml -tsvg salesforce_erd.puml
```

## Contributing
This tool is just a POC and needs lot of improvements in testing and usability. If this software do not satisfy you "as-is", consider improve it and send a pull request. Thank you! 