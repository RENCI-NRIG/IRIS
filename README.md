# IRIS
This is the repository for software and products from the NSF CICI Integrity 
Introspection for Scientific Workflows (IRIS) project.

## Project Layout

```
IRIS/
├── README.md
├── analysis
├── doc
├── emulation
├── es
├── exogeni-rdf
├── experiments
├── infrastructure
├── orchestra
└── saltstack

```
- `IRIS/analysis` contains the scripts for data analysis.

- `IRIS/doc` contains IRIS papers/documents.

- `IRIS/emulation` contains emulation scripts.

- `IRIS/es` contains the script used to pull data from Elasticsearch. See
    [usage instructions](es/README.md).

- `IRIS/exogeni-rdf` contains Exogeni recipe files

- `IRIS/experiments` contains a `run.py` script that will sequentially execute 
    each workflow in `IRIS/experiments/workflows`. All workflows used for
    experimental purposes are placed in this directory. Each workflow is self
    contained such that they will produce the same results whether they are run
    with the `run.py` script or invoked individually. Refer to these
    [run instructions](experiments/README.md) for instructions on how to run these 
    workflows.

- `IRIS/infrastructure` contains any software infrastructure services deployed onto
    the ExoGENI slice. 
  - [http proxy](infrastructure/http-proxy/README.md)

- `IRIS/orchestra` contains the scripts to run on control node to orchestrate the experiment.

- `IRIS/saltstack` contains configuration management scripts for our 
    infrastructure (apache, http-proxy, HTCondor, etc. setup)

