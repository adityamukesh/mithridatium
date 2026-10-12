# Repair

## Commands at a Glance

| Command | Purpose |
|---|---|
| `mithridatium audit` | **Detect** whether a model is backdoored. Runs a defense (e.g. FreeEagle, STRIP) and writes a verdict report. |
| `mithridatium detect` | **Input-level** poisoning detection (e.g. SCALE-UP). See [Detect](detect.md). |
| `mithridatium repair` | **Repair** a backdoored model. Runs a repair method (LMR) and writes a modified checkpoint plus a report. |

## When to use repair vs audit

- Run `audit` first to find out **if** your model is compromised.
- Run `repair` after to **fix** a model that audit flagged as backdoored.

## Supported repair methods

Currently supported:
- 'lmr' - Logit-Margin Repulsion based repair

The repair command is designed so additional repair methods can be added in the future through the `--method` option.

## LMR Requirements

LMR is a white-box repair method, meaning Mithridatium must have access to the model parameters.

LMR also requires:

- a small set of clean samples
- a target class specified with `--lmr-target-class`
- a pruning ratio specified with `--lmr-prune-ratio`

The clean samples are used during the repair and fine-tuning process.

## Example command

```bash
mithridatium repair \
  --model models/resnet18_poison.pth \
  --method lmr \
  --data cifar10 \
  --clean-samples 500 \
  --seed 42 \
  --lmr-target-class 0 \
  --lmr-prune-ratio 0.10 \
  --out models/resnet18_repaired.pth \
  --report reports/repair_report.json
```

## Useful flags

| Flag | Role |
|---|---|
| `--model` / `-m` | Local checkpoint (`.pth` / `.pt`) to repair. |
| `--method` / `-M` | Repair method (`lmr` today). |
| `--data` / `-d` | Dataset name for clean samples (e.g. `cifar10`). |
| `--clean-samples` / `-c` | Maximum number of clean samples to use (positive integer; default `500`). |
| `--seed` / `-s` | Random seed for reproducibility. |
| `--out` / `-o` | Path for the repaired output checkpoint (`.pth` / `.pt`). |
| `--report` / `-r` | Path for the JSON report, or `-` for stdout. Defaults to a sidecar beside `--out`. |
| `--force` / `-f` | Overwrite the checkpoint or report if it already exists. |
| `--lmr-target-class` | LMR: zero-based target class to repair (required; must be below the model's class count). |
| `--lmr-prune-ratio` | LMR: fraction of most-moved columns to prune (required; at least `0` and less than `1`). |

## Caveats

- This is a reduced version of LMR: 20 optimization steps plus 10 fine-tune steps, versus the paper's ~50 epochs.

- The target class has to come from the user, for example from a prior audit. Upstream's automatic localization isn't implemented.

- The pruning heuristic is simplified.

- The output is a research signal; it doesn't certify the model as clean.

## Future Work

- Make this the actual LMR implementation from the repo

- Add --lmr-repair-steps (default 20) and --lmr-fine-tune-steps (default 10) options to repair, following the pattern of --lmr-prune-ratio

More copy-paste examples: [Sample commands](testing/sample-commands.md).
