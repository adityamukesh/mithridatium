# Repair

## Commands at a Glance

| Command | Purpose |
|---|---|
| `mithridatium audit` | **Detect** whether a model is backdoored. Runs a defense (e.g. FreeEagle, STRIP) and writes a verdict report. |
| `mithridatium detect` | **Input-level** poisoning detection (e.g. SCALE-UP). See [Detect](detect.md). |
| `mithridatium repair` | **Repair** a backdoored model. Copies the checkpoint to a new path and writes a report. |

## When to use repair vs audit

- Run `audit` first to find out **if** your model is compromised.
- Run `repair` after to **fix** a model that audit flagged as backdoored.

## Example command

```bash
mithridatium repair \
  --model models/resnet18_poison.pth \
  --method lmr \
  --data cifar10 \
  --out models/resnet18_repaired.pth \
  --report reports/repair_report.json
```

## CLP (Channel Lipschitzness-based Pruning)

CLP is a **white-box, data-free** model repair method (Zheng et al., ECCV 2022).
It examines convolution and BatchNorm weights to find channels with unusually
high Lipschitzness scores, then suppresses those channels by setting the
corresponding BatchNorm scale and bias to zero. It does **not** require clean
examples, a CIFAR download, or retraining.

For each supported convolution/BatchNorm pair, the threshold is:

`mean(channel_scores) + u * std(channel_scores)`

The `--clp-threshold-mult` option controls `u` (default: `3.0`). A higher
multiplier generally prunes fewer channels.

### Run CLP

```bash
mithridatium repair \
  --model models/resnet18_poison.pth \
  --method clp \
  --clp-threshold-mult 3.0 \
  --out models/resnet18_clp.pth \
  --report reports/repair_clp.json
```

This saves a new `.pth` checkpoint and a JSON report. The report's `results`
include `method: "clp"`, the threshold multiplier, `total_channels_pruned`,
a per-layer breakdown, and a status message. By default, existing output files
are protected; use `--force` if overwriting is intentional. You can omit
`--report` for a JSON sidecar or use `--report -` to print the JSON to stdout.

### Limitations and interpretation

- The current loader builds a **ResNet-18 with 10 output classes**. Checkpoint
  weights and the supported Conv2d/BatchNorm2d structure must be compatible.
  This is not a generic method for arbitrary neural-network architectures.
- CLP inspects model parameters rather than clean training data, but pruning
  channels may also affect the model's normal accuracy.
- **A successful CLP run is a research signal, not certification that the model
  is clean or that a backdoor was removed.** Validate clean accuracy and attack
  success rate separately if labeled evaluation data are available.
- CLP does not change the `audit` or `detect` commands. The existing `lmr`
  method remains a stub.

### Quick tests (no full ResNet training)

```bash
python3 -m pytest tests/unit/test_clp.py -v
python3 -m pytest tests/smoke/test_cli_smoke.py -v
```

The unit tests use a small fake ResNet-like module to check scoring, pruning,
and report/checkpoint output. The CLI smoke tests exercise command dispatch
and overwrite protection. Neither test requires a 60-epoch training run.
