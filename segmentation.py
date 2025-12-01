from transformers import SegformerImageProcessor, AutoModelForSemanticSegmentation
from PIL import Image
import torch
import torch.nn as nn
import numpy as np

class ClothingSegmenter:
    def __init__(self):
        self.processor = SegformerImageProcessor.from_pretrained("mattmdjaga/segformer_b2_clothes")
        self.model = AutoModelForSemanticSegmentation.from_pretrained("mattmdjaga/segformer_b2_clothes")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        
    def get_tshirt_mask(self, image):
        """
        Returns a boolean numpy mask where True = T-Shirt/Upper Clothes.
        """
        # Ensure RGB
        image = image.convert("RGB")
        
        # Prepare input
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        
        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits.cpu()
            
        # Upsample logits to original image size
        upsampled_logits = nn.functional.interpolate(
            logits,
            size=image.size[::-1], # H, W
            mode="bilinear",
            align_corners=False,
        )
        
        # Get label map
        pred_seg = upsampled_logits.argmax(dim=1)[0]
        
        # The model 'mattmdjaga/segformer_b2_clothes' usually maps:
        # 0: Background, 4: Upper-clothes, 5: Skirt, 6: Pants, 7: Dress...
        # We'll target 'Upper-clothes' (4) and 'Dress' (7) to cover all torso garments.
        mask = np.isin(pred_seg.numpy(), [4, 7])
        
        return mask
