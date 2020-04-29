### Running Batch Experiments
1. Navigate to `IRIS/experiments/`
2. Run `./run.py`
  - This will run each workflow in the `IRIS/experiments/workflows/` directory
    sequentially.
  - Submit directories for each workflow will be located under:

```
$HOME/workflow-batch-experiment-runs
├── 1588029671             <-- time at which batch run initiated
│   ├── 01-test-workflow   <-- executed workflow directory
│   └── 02-bypass-staging-1-cache-corrupt
└── 1588030368
    ├── 01-test-workflow
    └── 02-bypass-staging-1-cache-corrupt
```

### Running Individual Workflows
1. Navigate to `IRIS/experiments/workflows/<target wf>`
2. Run `./workflow.py`
  - Submit directory for the workflow will be located under:

```
$HOME/workflow-runs
└── <<target wf dir name> + unix timestamp>
```
