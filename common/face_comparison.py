# import numpy as np
# import cv2
# import requests
# from io import BytesIO
# from PIL import Image
# import numpy as np
# from PIL import Image
# import numpy as np
# from deepface import DeepFace
# from rest_framework.response import Response
# import torch
# import torch.nn as nn
# from torchvision import models
# from passporteye import read_mrz
# from torch import no_grad
# import albumentations as A
# from albumentations.pytorch import ToTensorV2


# class DeepFaceVerifier:

#     @staticmethod
#     def convert_to_color_scheme(image1, image2):
#         try:
#             print("pppppppppp")
#             image1 = requests.get(image1)
#             image2 = requests.get(image2)
#             print("vvvvv")

#             if image1.status_code == 200 and image2.status_code == 200:
#                 image1_response = Image.open(BytesIO(image1.content))
#                 image2_response = Image.open(BytesIO(image2.content))
#                 print("xxxxx")
                
#                 # Convert PIL image to OpenCV format (BGR)
#                 image1_cv = cv2.cvtColor(np.array(image1_response), cv2.COLOR_RGB2BGR)
#                 image2_cv = cv2.cvtColor(np.array(image2_response), cv2.COLOR_RGB2BGR)
#                 print("aqaqaq")
#                 return (image1_cv, image2_cv)
            
#         except Exception as e:
#             return {"message": "Invalid image provided. Kindly provide a valid image"}

#     @staticmethod
#     def detect_face(image):
#         print("ppp")
#         face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#         print("assaaaaa")
#         faces = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
#         print(faces)
#         return faces
    
#     @staticmethod
#     def compare_faces(image_path1, image_path2):

#         image1, image2 = DeepFaceVerifier.convert_to_color_scheme(image_path1, image_path2)
#         face_detect_secondary = DeepFaceVerifier.detect_face(image1)
#         if not isinstance(face_detect_secondary, np.ndarray) or face_detect_secondary.size == 0:
#             return {"status": False, "message": "No face detected. Ensure that your face is clearly visible."}
#         face_detect_video = DeepFaceVerifier.detect_face(image2)
#         if not isinstance(face_detect_video, np.ndarray) or face_detect_video.size == 0:
#             return {"status": False, "message": "No face detected in video. Ensure that your face is clearly visible"}
#         print("jjjjjjjjjj")
#         comparison = DeepFace.verify(image1, image2, threshold=0.68, model_name="ArcFace")
#         if comparison is None or not isinstance(comparison, dict):
#             return {"status": False, "message": "An error ocurred while verifying your biometrics"}           
#         if comparison and "threshold" in comparison and "distance" in comparison and "model" in comparison:
#             spoof = DeepFace.extract_faces(image2, anti_spoofing=True)
#             if not spoof or not isinstance(spoof, list) or len(spoof) == 0:
#                 return {"status": False, "message": "An error ocurred while verifying your biometrics"}      
#             for sp in spoof:
#                 spoof_data = {
#                     "is_real": sp["is_real"],
#                     "antispoof_score": round(sp["antispoof_score"] * 100, 2),
#                     "confidence": sp["confidence"] * 100,
#                 }

#             return {
#                 "status": True,
#                 "spoof": spoof_data,
#                 "comparison": {
#                     "verified": comparison["verified"],
#                     "threshold": comparison["threshold"],
#                     "time_taken": comparison["time"],
#                 }
#             }


#     @staticmethod
#     def create_model(num_classes=5):
#         model = models.resnet50(weights=None)
#         num_ftrs = model.fc.in_features
#         model.fc = nn.Sequential(
#             nn.Dropout(0.5),
#             nn.Linear(num_ftrs, num_classes)
#         )
#         return model
    
#     @staticmethod
#     def predict_image(image_path, model, device):

#         image1 = requests.get(image_path)
#         if not image1.status_code == 200:
#         # if not os.path.exists(image_path):
#             raise FileNotFoundError(f"Error: The image at path {image_path} does not exist.")
        
#         # Image transformations
#         transform = A.Compose([
#             A.Resize(224, 224),
#             A.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
#             ToTensorV2()
#         ])
        
#         # Load and transform the image
#         try:
#             image = Image.open(BytesIO(image1.content))
#         except Exception as e:
#             raise ValueError(f"Error: Could not open image. Details: {e}")
        
#         image = np.array(image)
#         image = transform(image=image)["image"]
#         image = image.unsqueeze(0).to(device)
#         try:
#             with no_grad():
#                 outputs = model(image)
#                 probabilities = torch.sigmoid(outputs)
#         except Exception as e:
#             raise RuntimeError(f"Error during model prediction: Invalid image provided")
        
#         return probabilities.cpu().numpy()[0]
    
    
#     @staticmethod
#     def interpret_predictions(probabilities, threshold=0.7):
#         class_names = ["ECOWAS Logo", "Ghana Coat of Arms", "Ghana Flag", "Ghana Map", "Valid Ghana Card"]
#         predictions = (probabilities > threshold).astype(int)
#         detected_features = []
#         detected_probs = []
#         for i, (name, prob) in enumerate(zip(class_names, probabilities)):
#             if prob > threshold:
#                 detected_features.append(name)
#                 detected_probs.append(prob)
#         return detected_features, detected_probs, predictions

#     @staticmethod
#     def validate_ghana_card(image_path, model, device):
#         probabilities = DeepFaceVerifier.predict_image(image_path, model, device)
#         detected_features, detected_probs, predictions = DeepFaceVerifier.interpret_predictions(probabilities)
        
#         is_valid = "Valid Ghana Card" in detected_features
        
#         print(f"Image: {image_path}")
#         print("Detected features and probabilities:")
#         for feature, prob in zip(detected_features, detected_probs):
#             print(f"  {feature}: {prob:.4f}")
#         print("Is Valid Ghana Card:", "Yes" if is_valid else "No")
#         print("--------------------")
        
#         return is_valid, detected_probs

#     @staticmethod
#     def read_mrz_and_card_number(image_path):
#         try:
#             image1 = requests.get(image_path)
#             if image1.status_code != 200:
#                 raise FileNotFoundError(f"Error: The image at path {image_path} does not exist.")
#         except requests.RequestException as e:
#             raise ValueError(f"Error: Unable to fetch image from {image_path}. Details: {e}")
        
#         print("=======================")
        
#         # Try to open the image
#         try:
#             image = Image.open(BytesIO(image1.content))
#             print("Image opened successfully.")
#         except Exception as e:
#             raise ValueError(f"Error: Could not open image. Details: {e}")
        
#         print("Processing image for MRZ...")
        
#         # Try reading MRZ from the image
#         try:
#             mrz = read_mrz(image)
#             if mrz is None:
#                 print("No MRZ found.")
#                 mrz_data = {}
#             else:
#                 print("MRZ Detected!")
#                 mrz_data = mrz.to_dict()

#                 # Remove boolean values from the MRZ data
#                 mrz_data = {key: value for key, value in mrz_data.items() if not isinstance(value, bool)}
            
#             return mrz_data
#         except AttributeError as e:
#             raise ValueError(f"Error: Image is invalid or improperly processed. Details: {e}")
#         except Exception as e:
#             raise ValueError(f"Unexpected error occurred during MRZ reading. Details: {e}")

#     def verify_ghana_card_features(ghana_card_front, ghana_card_back):
#         device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#         model = DeepFaceVerifier.create_model()
#         model.load_state_dict(torch.load("ghana_card_model.pth", map_location=device, weights_only=True))
#         model.eval()
#         model = model.to(device)

#         is_valid, detected_probs = DeepFaceVerifier.validate_ghana_card(ghana_card_front, model, device)

#         if is_valid:
#             # mrz_data = InsightFaceVerifier.read_mrz_and_card_number(ghana_card_back)
#             # print("Extracted Information:")
#             # print(json.dumps(mrz_data, indent=4))
#             return {
#                 "status": True,
#                 # "probabilities": detected_probs,
#             }
#         else:
#             return {
#                 "status": False,
#                 # "probabilities": detected_probs,
#             }



    