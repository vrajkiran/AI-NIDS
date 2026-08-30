# Data Folder

Place your local CICIDS2017 CSV files in this folder.

Do not download the dataset automatically from this project.

The training script reads:

```bash
python ml/train.py
```

By default, it loads all `.csv` files found in this `data/` folder.

The labels are converted into binary classes:

- `BENIGN` becomes `0`
- Every other attack label becomes `1`
