from dipt.lab1.trycorus import result
import numpy as np
from datasets import Dataset, DatasetDict

gen = np.random.default_rng(42)

ds = Dataset.from_dict(result)
dsd = ds.train_test_split(test_size=0.2, generator=gen)
dsd_temp = dsd["test"].train_test_split(test_size=0.5, generator=gen)
dsd = DatasetDict(
    {"train": dsd["train"], "test": dsd_temp["test"], "valid": dsd_temp["train"]}
)
