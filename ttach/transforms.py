from functools import partial
from . import functional as F
from .base import DualTransform, ImageOnlyTransform


class HorizontalFlip(DualTransform):
    identity_param = False

    def __init__(self):
        super().__init__("apply", [False, True])

    def apply_aug_image(self, image, apply=False, **kwargs):
        if apply:
            image = F.hflip(image)
        return image

    def apply_deaug_mask(self, mask, apply=False, **kwargs):
        if apply:
            mask = F.hflip(mask)
        return mask

    def apply_deaug_label(self, label, apply=False, **kwargs):
        return label


class VerticalFlip(DualTransform):
    identity_param = False

    def __init__(self):
        super().__init__("apply", [False, True])

    def apply_aug_image(self, image, apply=False, **kwargs):
        if apply:
            image = F.vflip(image)
        return image

    def apply_deaug_mask(self, mask, apply=False, **kwargs):
        if apply:
            mask = F.vflip(mask)
        return mask

    def apply_deaug_label(self, label, apply=False, **kwargs):
        return label


class Rotate90(DualTransform):
    identity_param = 0

    def __init__(self, angles: list):
        if self.identity_param not in angles:
            angles = [self.identity_param] + list(angles)

        super().__init__("angle", angles)

    def apply_aug_image(self, image, angle=0, **kwargs):
        k = angle // 90 if angle >= 0 else (angle + 360) // 90
        return F.rot90(image, k)

    def apply_deaug_mask(self, mask, angle=0, **kwargs):
        return self.apply_aug_image(mask, -angle)

    def apply_deaug_label(self, label, angle=0, **kwargs):
        return label


class Scale(DualTransform):
    identity_param = 1

    def __init__(self, scales: list, interpolation="nearest", align_corners=None):

        if self.identity_param not in scales:
            scales = [self.identity_param] + list(scales)
        self.interpolation = interpolation
        self.align_corners = align_corners

        super().__init__("scale", scales)

    def apply_aug_image(self, image, scale=1, **kwargs):
        if scale != self.identity_param:
            image = F.scale(
                image,
                scale,
                interpolation=self.interpolation,
                align_corners=self.align_corners,
            )
        return image

    def apply_deaug_mask(self, mask, scale=1, **kwargs):
        if scale != self.identity_param:
            mask = F.scale(
                mask,
                1 / scale,
                interpolation=self.interpolation,
                align_corners=self.align_corners,
            )
        return mask

    def apply_deaug_label(self, label, angle=1, **kwargs):
        return label


class Add(ImageOnlyTransform):
    identity_param = 0

    def __init__(self, values: list):
        if self.identity_param not in values:
            values = [self.identity_param] + list(values)
        super().__init__("value", values)

    def apply_aug_image(self, image, value=0, **kwargs):
        if value != self.identity_param:
            image = F.add(image, value)
        return image


class Multiply(ImageOnlyTransform):
    identity_param = 1

    def __init__(self, factors: list):
        if self.identity_param not in factors:
            factors = [self.identity_param] + list(factors)
        super().__init__("factor", factors)

    def apply_aug_image(self, image, factor=1, **kwargs):
        if factor != self.identity_param:
            image = F.multiply(image, factor)
        return image


class FiveCrops(ImageOnlyTransform):
    def __init__(self, crop_height, crop_width):
        crop_functions = (
            partial(F.crop_lt, crop_h=crop_height, crop_w=crop_width),
            partial(F.crop_lb, crop_h=crop_height, crop_w=crop_width),
            partial(F.crop_rb, crop_h=crop_height, crop_w=crop_width),
            partial(F.crop_rt, crop_h=crop_height, crop_w=crop_width),
            partial(F.center_crop, crop_h=crop_height, crop_w=crop_width),
        )
        super().__init__("crop_fn", crop_functions)

    def apply_aug_image(self, image, crop_fn=None, **kwargs):
        return crop_fn(image)

    def apply_deaug_mask(self, mask, **kwargs):
        raise ValueError("`FiveCrop` augmentation is not suitable for mask!")
