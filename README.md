# ChromaField

**Beneath the Pigment and the Pen: Dual-Inversion Implicit Boundary Fields for Tone-Robust, Annotator-Aware and Calibrated Skin Lesion Segmentation**

Reproduction package for the manuscript. One notebook runs the method end to end
— four training stages, three seeds — and writes every file a reviewer is likely
to ask for: logs, checkpoints, per-image predictions, calibration records,
runnable evaluation and statistics scripts, baseline configurations and a
de-duplication audit. A complete run is committed under [`artifacts/`](artifacts/)
so the package can be read without executing anything.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Codebase1157/ChromaField/blob/main/notebooks/chromafield_artifacts.ipynb)

---

## Quick start

Open the notebook in Colab with the badge above and run it top to bottom.

```bash
# or locally
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute notebooks/chromafield_artifacts.ipynb
```

| Environment variable | Purpose |
|---|---|
| `CF_IMAGE_DIR` | folder of dermoscopic images to use instead of the synthetic cohort |
| `CF_MASK_DIR` | reference masks, matching file stems |
| `CF_FAST=1` | ~8-minute run that exercises every cell and produces the archive in miniature |
| `CF_ARTIFACT_ROOT` | where the run directory is written |

With no images supplied the notebook renders a cohort through the paper's own
forward model (Eqs. 1–3), with known masks, structure masks and diagnosis
labels, so every artefact is still genuine output of the committed code.

Runtime: about 5 minutes on a Colab T4, roughly 90 minutes on a Colab CPU.
Select a GPU runtime.

## What is in the box

```
notebooks/chromafield_artifacts.ipynb   the whole pipeline, 52 cells
artifacts/20261107-103638/              one complete three-seed run
verify_artifact.py                      checks every SHA-256 in the manifest
requirements.txt                        direct dependencies
```

Inside a run directory:

| Path | Contents |
|---|---|
| `logs/` | per-epoch loss terms, validation Dice, learning rate and gradient norm, one CSV per stage per seed, plus `run.log` |
| `checkpoints/` | Stage I–IV weights for every seed, `selection.json` (selection metric, selected epoch and its value), `sha256_checkpoints.csv` |
| `predictions/` | `per_image.parquet`/`.csv` — native-resolution scores, band statistics, structure presence, class posteriors; `cases/*.npz` — the arrays themselves |
| `calib/` | conformal scores, quantiles, stratum sizes, certifiability flags for Eqs. (28) and (29), the `eta` fit, `score_definition.json` |
| `eval/` | Dice, IoU, HD95, ASSD, NSD at native resolution; GED and matched Dice; border and diagnosis-set coverage; Wilson intervals; `aggregate.py` |
| `stats/` | paired BCa bootstrap, Wilcoxon signed-rank, paired permutation, Holm, all with fixed seeds; `run_all.py` |
| `baselines/` | one protocol record per baseline (see `baselines/README.md`) |
| `audit/` | de-duplication audit with every flagged pair and its decision, duplicate groups, post-hoc leakage check |
| `data/` | partitions, SHA-256 and perceptual-hash manifests, ITA and contrast strata |
| `configs/`, `architecture/`, `env/` | every constant with the paper's value beside any reduced for runtime; parameter counts and shape trace; lockfile and platform |
| `results/` | `seed_results.csv`, coverage tables, `script_verification.json`, `SCOPE.txt` |
| `figures/` | 600 dpi qualitative panels computed on the original image bytes |

## Recomputing the numbers without retraining

The evaluation and statistics scripts are standalone and operate on the
committed prediction files:

```bash
cd artifacts/20261107-103638
python eval/aggregate.py .     # every headline aggregate
python stats/run_all.py .      # every interval and p-value
python ../../verify_artifact.py .   # every SHA-256 in MANIFEST.json
```

The notebook runs both scripts against its own output and records the
comparison in `results/script_verification.json`. For the committed run they
agree with the notebook to `0.00e+00`.

A GitHub Actions workflow re-runs all three on every push, so the claim is
machine-checked rather than asserted.

## Results from the committed run

Three seeds, 96-image synthetic cohort, Tesla T4. Seed-wise values are in
[`artifacts/20261107-103638/results/seed_results.csv`](artifacts/20261107-103638/results/seed_results.csv).

**Segmentation**, Dice % against the consensus reference, mean ± sd over seeds:

| Arm | Dice | HD95 | NSD |
|---|---|---|---|
| ChromaField | 96.84 ± 0.24 | 3.03 | 89.03 |
| U-Net trained here | **97.99 ± 0.15** | 2.73 | 95.78 |
| − illumination removal (Eq. 12) | 96.64 ± 0.42 | 3.18 | 87.25 |
| − chromophore ratio features | 64.55 ± 51.57 | 26.81 | 45.87 |

**The annotation operator**, each protocol head against that protocol's own
annotation, with and without the operator of Eq. (6):

| Protocol | Dice with | Dice without | NSD with | NSD without |
|---|---|---|---|---|
| polygon | 96.23 | 92.19 | 79.18 | 29.23 |
| flood fill | 94.72 | 89.75 | 73.85 | 24.08 |
| semi-automatic | 95.73 | 95.05 | 75.24 | 69.13 |

**Calibration**, border band at α = 0.1, seed 0:

| Stratum | n calib | quantile | coverage | Wilson 95% | band area | status |
|---|---|---|---|---|---|---|
| dark | 9 | 8.25 | 1.000 | 0.61–1.00 | 0.173 | marginal only |
| intermediate | 1 | ∞ | 1.000 | 0.51–1.00 | 0.176 | uncertifiable |
| light | 11 | 10.16 | 0.833 | 0.44–0.97 | 0.173 | marginal only |
| all | 21 | 9.94 | 0.938 | 0.72–0.99 | 0.174 | marginal only |

Generalised energy distance 0.0586 ± 0.0021.

## Read this before quoting any of it

`artifacts/*/results/SCOPE.txt` states the scope inside the archive. The short
version:

- **These are  the manuscript's tables.** The comparison tables retrain 18
  segmentation and 13 detection-and-diagnosis baselines from official code on
  licensed dermoscopic archives. This notebook retrains none of them.
  `baselines/` records their protocol with null commit hashes and an explicit
  `status: not_run_in_this_notebook`, rather than inventing provenance for runs
  that did not happen.
- **The committed run uses .** The images are renders from
  the paper's own forward model. The structure masks and diagnosis labels are
  generated with them and are learnable by construction, which is what makes
  Stage IV exercisable. They say nothing about clinical accuracy. Point
  `CF_IMAGE_DIR` at real data and the same pipeline produces the same files
  from it.
- **A plain U-Net beats ChromaField on this cohort**, by about 1.2 Dice points.
  That is consistent with the paper's own caveat: large, smooth, high-contrast
  lesions at modest resolution are where a grid model should win. The
  resolution-free field is not the right tool for this particular data, and the
  package reports that rather than hiding it.
- **Stage IV is under-trained at this scale.** Mean structure Jaccard is ~0.04%
  and the notebook logs a warning saying the field has not separated the five
  structures. Diagnosis BMCA is 19.1 ± 5.1% over seven classes of which four
  appear. Both are reported as measured.
- **One ablation is unstable.** Removing the chromophore ratio features
  collapses one seed of three to 5.0 Dice, which is why its standard deviation
  is 51.6. The mean alone would be misleading.

## One departure from the manuscript

`calib/score_definition.json` records a correction to Eq. (27). As printed, the
score divides by `σ_tot + σ₀` while the band of Eq. (26) is `q·σ_tot + σ₀`, so
the stated equivalence — `s_i ≤ q` exactly when `Core_q ⊆ y ⊆ Env_q` — holds
only at `q = 1`. Proposition 3 converts the rank statement on scores into a
coverage statement about the band through exactly that equivalence. The
implemented score is

```
s_i = max_u [ ((2 y_i(u) − 1) φ̄(u) − σ₀) / σ_tot(u) ]₊
```

which restores the equivalence for every `q` against the band as Eq. (26)
prints it. Both forms are in the file.

## Citation

See [`CITATION.cff`](CITATION.cff).

## License

Code and artefacts are released under the MIT License — see [`LICENSE`](LICENSE).
