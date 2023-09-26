import torch
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
from BLIP.models.blip import blip_decoder


def load_demo_image(img, image_size): 

    w,h = img.size
    # display(img.resize((w//5,h//5)))
    
    transform = transforms.Compose([
        transforms.Resize((image_size,image_size),interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
        ]) 
    image = transform(img).unsqueeze(0)
    return image

def caption(img):
    image_size = 384
    image = load_demo_image(img, image_size=image_size)

    # model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_capfilt_large.pth'
    path = 'model_base_capfilt_large.pth'
    model = blip_decoder(pretrained=path, image_size=image_size, vit='base')
    model.eval()
    # model = model.to(device)

    with torch.no_grad():
        # beam search
        caption = model.generate(image, sample=False, num_beams=3, max_length=20, min_length=5) 
        # nucleus sampling
        # caption = model.generate(image, sample=True, top_p=0.9, max_length=20, min_length=5) 
        # print('caption: '+caption[0])
        return caption[0]