import cv2
import torch
import torchvision.transforms as transforms
import torchvision.models as models
import torch.nn.functional as F
from PIL import Image

# 1. Load a pre-trained AI Brain (ResNet18) just once when the server starts
print("🧠 Booting up Signature Verification AI...")
resnet = models.resnet18(pretrained=True)

# 2. Perform Brain Surgery: Remove the final "guessing" layer so it just outputs raw features
resnet = torch.nn.Sequential(*list(resnet.children())[:-1])
resnet.eval() # Set to evaluation mode

# 3. Setup the strict image requirements for the AI
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def extract_features(image_array):
    """Converts an OpenCV image into a mathematical AI Vector"""
    # Convert OpenCV BGR to RGB, then to a PIL Image
    image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(image_rgb)
    
    # Run it through the preprocessing rules
    input_tensor = preprocess(pil_image)
    input_batch = input_tensor.unsqueeze(0) # Create a mini-batch as expected by the model
    
    # Run it through the AI
    with torch.no_grad():
        features = resnet(input_batch)
    
    return features.flatten()

def verify_signature(scanned_crop, reference_image_path):
    """Compares the scanned ink against the official file on record"""
    print("🕵️ Verifying signature authenticity...")
    
    # 1. Load the official reference image from your laptop
    reference_img = cv2.imread(reference_image_path)
    if reference_img is None:
        return False, "Reference signature missing!"

    # 2. Extract vectors for both images
    scanned_vector = extract_features(scanned_crop)
    reference_vector = extract_features(reference_img)
    
    # 3. Calculate how mathematically similar they are (Cosine Similarity)
    similarity = F.cosine_similarity(scanned_vector.unsqueeze(0), reference_vector.unsqueeze(0))
    match_score = similarity.item() * 100
    
    print(f"📊 AI Match Score: {match_score:.2f}%")
    
    # 4. The Decision Threshold (You can adjust this!)
    if match_score > 55.0:
        return True, f"Verified ({match_score:.1f}% Match)"
    else:
        return False, f"Forgery Detected ({match_score:.1f}% Match)"