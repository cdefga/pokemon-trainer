import torch
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import imgaug as ia
from imgaug import augmenters as iaa
mpl.rcParams['axes.grid'] = False
mpl.rcParams['image.interpolation'] = 'nearest'
mpl.rcParams['figure.figsize'] = 5, 10


def calc_norm(dataset):
    dataloader = torch.utils.data.DataLoader(dataset, batch_size=1147, shuffle=False, num_workers=4)
    pop_mean = []
    pop_std0 = []
    pop_std1 = []

    for i, data in enumerate(dataloader, 0):
        numpy_image = data['image'].numpy()
        
        batch_mean = np.mean(numpy_image, axis=(0,2,3))
        batch_std0 = np.std(numpy_image, axis=(0,2,3))
        batch_std1 = np.std(numpy_image, axis=(0,2,3), ddof=1)
        
        pop_mean.append(batch_mean)
        pop_std0.append(batch_std0)
        pop_std1.append(batch_std1)

    pop_mean = np.array(pop_mean).mean(axis=0)
    pop_std0 = np.array(pop_std0).mean(axis=0)
    pop_std1 = np.array(pop_std1).mean(axis=0)
    
    print(pop_mean) # [0.6855248  0.68901044 0.6142709 ] mean
    print(pop_std0) # [0.32218283 0.27970755 0.31340986] std0
    print(pop_std1) # [0.32218322 0.27970782 0.3134101 ] std1


def show_dataset(dataset, n=6):
    img = np.vstack((np.hstack((np.asarray(dataset[i][0]) for _ in range(n))) for i in range(5)))
    plt.imshow(img)
    plt.axis('off')
    plt.show()


class ImgAugmenter:
  def __init__(self):
    self.aug = iaa.Sequential([
        iaa.Sometimes(0.4, iaa.GaussianBlur(sigma=(0, 3.0))),
        iaa.Sometimes(0.3, iaa.OneOf([iaa.Dropout(p=(0, 0.1)), iaa.CoarseDropout(0.1, size_percent=0.5)])),
        iaa.AddToHueAndSaturation(value=(-10, 10), per_channel=True)
    ])
      
  def __call__(self, img):
    img = np.array(img)
    return self.aug.augment_image(img)


if __name__ == '__main__':
    from dataloader import dataloader
    from torchvision import transforms
    from torchvision.datasets import ImageFolder
    import PIL

    transform = {
        'train': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            ImgAugTransform(),
            lambda x: PIL.Image.fromarray(x),
            transforms.ColorJitter(hue=.05, saturation=.05),
            transforms.RandomHorizontalFlip(),
            transforms.RandomAffine(15),
            transforms.RandomRotation(20, resample=PIL.Image.BILINEAR),
            transforms.ToTensor(),
        ]),
        'test': transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
        ])
    }

    train_data = ImageFolder(root='../pkm/train/', transform=transform['train'])
    # show_dataset(train_data)
    data, labels = train_data[888]
    plt.imshow(data.permute(1,2,0))
    plt.show()