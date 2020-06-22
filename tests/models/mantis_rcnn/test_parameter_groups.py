import pytest
from mantisshrimp.imports import nn
from mantisshrimp import *


@pytest.fixture()
def simple_backbone():
    class SimpleBackbone(nn.Module):
        def __init__(self):
            super().__init__()
            self.c1 = nn.Conv2d(3, 8, 3, 2)
            self.c2 = nn.Conv2d(8, 16, 3, 2)
            self.out_channels = 16

        def forward(self, x):
            return self.c2(self.c1(x))

    return SimpleBackbone()


@pytest.mark.parametrize("model_class", [MantisFasterRCNN, MantisMaskRCNN])
def test_simple_backbone_default_param_groups(model_class, simple_backbone):
    model = model_class(num_classes=2, backbone=simple_backbone)
    assert model.param_groups == [
        simple_backbone,
        model.model.rpn,
        model.model.roi_heads,
    ]


@pytest.mark.parametrize("model_class", [MantisFasterRCNN, MantisMaskRCNN])
def test_simple_backbone_custom_param_groups(model_class, simple_backbone):
    backbone_param_groups = [simple_backbone.c1, simple_backbone.c2]
    model = model_class(
        num_classes=16, backbone=simple_backbone, param_groups=backbone_param_groups
    )
    expected = backbone_param_groups + [model.model.rpn, model.model.roi_heads]
    assert model.param_groups == expected


@pytest.mark.parametrize("model_class", [MantisFasterRCNN, MantisMaskRCNN])
def test_default_backbone_default_param_groups(model_class):
    model = model_class(num_classes=42)
    backbone_param_groups = resnet_fpn_backbone_param_groups(model.model.backbone)
    expected = backbone_param_groups + [model.model.rpn, model.model.roi_heads]
    assert len(model.param_groups) == len(expected)
    # check by weight values, not layer reference
    for pg1, pg2 in zip(backbone_param_groups, expected):
        assert list(pg1.parameters()) == list(pg2.parameters())
