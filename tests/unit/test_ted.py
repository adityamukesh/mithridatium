"""TED unit tests. Tiny model and synthetic data, no checkpoint."""

import pytest
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset

from mithridatium import report as rpt
from mithridatium.detect.ted import ted

pytestmark = pytest.mark.unit


class Tiny(nn.Module):
    def __init__(self, num_classes=3):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 4, 3, padding=1)
        self.conv2 = nn.Conv2d(4, 4, 3, padding=1)
        self.relu = nn.ReLU()
        self.fc = nn.Linear(4 * 8 * 8, num_classes)

    def forward(self, x):
        x = self.relu(self.conv1(x))
        x = self.relu(self.conv2(x))
        return self.fc(x.flatten(1))


def _data(model, n, seed):
    """Random images labelled with the model's own predictions, keeping only
    classes with at least two samples (upstream's TED code assumes this)."""
    x = torch.randn(n, 3, 8, 8, generator=torch.Generator().manual_seed(seed))
    with torch.no_grad():
        y = model(x).argmax(1)
    keep = torch.bincount(y, minlength=3)[y] >= 2
    return TensorDataset(x[keep], y[keep])


def test_ted_output_validates_and_removes_hooks():
    torch.manual_seed(0)
    model = Tiny().eval()
    ref = _data(model, 60, 0)
    sus = TensorDataset(*ref[:10])   # suspects from the reference set, so every predicted class has neighbours
    r = ted(model, ref, sus, reference_size=len(ref), contamination=0.1, seed=0)


    assert (r["mode"], r["method"]) == ("input-level", "ted")
    assert r["num_inputs"] == len(r["per_sample"]) == 10
    assert 0 <= r["num_flagged"] <= 10
    rpt.validate_report_data(rpt.build_report("m.pth", "ted", "cifar10", "0.0.0", r))
    assert not any(m._forward_hooks for m in model.modules())
