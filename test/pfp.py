from PIL import Image
from diffusers import AutoPipelineForText2Image
import torch

pipe = AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float32, variant="fp16")
#pipe.to("cuda")

prompt = "A magical brown and gold story book flying up into a purple sky with bright beautiful stars, while its pages flip onto a page with magical text"

image = pipe(prompt=prompt, num_inference_steps=1, guidance_scale=0.0).images[0]

# Save the image
image.save('generated_image.png')
