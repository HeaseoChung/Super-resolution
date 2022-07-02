import os
import random
import torchvision.transforms as transforms
from torch.utils.data import Dataset
from PIL import Image

from degradation import Degradation
from utils import check_image_file


class Dataset(Dataset):
    def __init__(self, cfg):
        self.patch_size = cfg.patch_size
        self.scale = cfg.scale
        self.rotate = [0, 90, 180, 270]
        self.degradation = Degradation(cfg)

        self.hrfiles = [
            os.path.join(cfg.train_dir, x)
            for x in os.listdir(cfg.train_dir)
            if check_image_file(x)
        ]

        self.len = len(self.hrfiles)
        self.to_tensor = transforms.ToTensor()

    def __getitem__(self, index):
        # Read input data and output data

        hr = Image.open(self.hrfiles[index]).convert("RGB")

        width, height = hr.size

        # crop
        crop_w = random.randint(0, width - self.patch_size)
        crop_h = random.randint(0, height - self.patch_size)

        hr = hr.crop(
            (crop_w, crop_h, crop_w + self.patch_size, crop_h + self.patch_size)
        )

        # rotate
        rotate = self.rotate[random.randint(0, len(self.rotate) - 1)]
        hr = hr.rotate(rotate)

        # Degradation
        lr, hr = self.degradation.degradation_pipeline(hr)

        return self.to_tensor(lr), self.to_tensor(hr)

    def __len__(self):
        return self.len
