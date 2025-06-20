import numpy as np
from typing import List, Tuple, Dict, Optional
import streamlit as st
from PIL import Image
import io

# Face recognition libraries (optional for Vercel deployment)
try:
    import cv2
    import face_recognition
    FACE_RECOGNITION_AVAILABLE = True
except ImportError:
    FACE_RECOGNITION_AVAILABLE = False
    cv2 = None
    face_recognition = None

class FaceRecognitionSystem:
    def __init__(self, confidence_threshold: float = 0.6):
        self.confidence_threshold = confidence_threshold
        self.known_face_encodings = {}
        self.known_face_names = {}
        
    def load_known_faces(self, face_encodings_dict: Dict[str, np.ndarray], 
                        teacher_names_dict: Dict[str, str]):
        """Load known face encodings and names"""
        self.known_face_encodings = face_encodings_dict
        self.known_face_names = teacher_names_dict
    
    def detect_faces_in_image(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect face locations in an image"""
        if not FACE_RECOGNITION_AVAILABLE:
            st.warning("Face recognition not available in this deployment. Please use local version for full functionality.")
            return []

        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image

            # Find face locations
            face_locations = face_recognition.face_locations(rgb_image)
            return face_locations
        except Exception as e:
            st.error(f"Error detecting faces: {str(e)}")
            return []
    
    def encode_face(self, image: np.ndarray, face_location: Tuple[int, int, int, int] = None) -> Optional[np.ndarray]:
        """Generate face encoding from image"""
        if not FACE_RECOGNITION_AVAILABLE:
            # Return a dummy encoding for demo purposes
            return np.random.rand(128).astype(np.float64)

        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image

            if face_location:
                face_encodings = face_recognition.face_encodings(rgb_image, [face_location])
            else:
                face_encodings = face_recognition.face_encodings(rgb_image)

            if face_encodings:
                return face_encodings[0]
            return None
        except Exception as e:
            st.error(f"Error encoding face: {str(e)}")
            return None
    
    def recognize_faces(self, image: np.ndarray) -> List[Dict]:
        """Recognize faces in an image and return results"""
        results = []

        if not FACE_RECOGNITION_AVAILABLE:
            st.info("Face recognition not available in this deployment. Please use local version for full functionality.")
            return []

        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image

            # Find face locations and encodings
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            for face_encoding, face_location in zip(face_encodings, face_locations):
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    list(self.known_face_encodings.values()), 
                    face_encoding,
                    tolerance=1.0 - self.confidence_threshold
                )
                
                # Calculate face distances
                face_distances = face_recognition.face_distance(
                    list(self.known_face_encodings.values()), 
                    face_encoding
                )
                
                teacher_id = "Unknown"
                teacher_name = "Unknown"
                confidence = 0.0
                
                if True in matches:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        teacher_ids = list(self.known_face_encodings.keys())
                        teacher_id = teacher_ids[best_match_index]
                        teacher_name = self.known_face_names.get(teacher_id, "Unknown")
                        confidence = 1.0 - face_distances[best_match_index]
                
                results.append({
                    'teacher_id': teacher_id,
                    'teacher_name': teacher_name,
                    'confidence': confidence,
                    'face_location': face_location,
                    'is_recognized': teacher_id != "Unknown" and confidence >= self.confidence_threshold
                })
            
            return results
            
        except Exception as e:
            st.error(f"Error recognizing faces: {str(e)}")
            return []
    
    def draw_face_boxes(self, image: np.ndarray, recognition_results: List[Dict]) -> np.ndarray:
        """Draw bounding boxes and labels on faces"""
        try:
            output_image = image.copy()
            
            for result in recognition_results:
                top, right, bottom, left = result['face_location']
                
                # Choose color based on recognition status
                if result['is_recognized']:
                    color = (0, 255, 0)  # Green for recognized
                    label = f"{result['teacher_name']} ({result['confidence']:.2f})"
                else:
                    color = (0, 0, 255)  # Red for unknown
                    label = "Unknown"
                
                # Draw rectangle
                cv2.rectangle(output_image, (left, top), (right, bottom), color, 2)
                
                # Draw label background
                cv2.rectangle(output_image, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
                
                # Draw label text
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(output_image, label, (left + 6, bottom - 6), font, 0.6, (255, 255, 255), 1)
            
            return output_image
            
        except Exception as e:
            st.error(f"Error drawing face boxes: {str(e)}")
            return image
    
    def process_uploaded_images(self, uploaded_files: List) -> Tuple[bool, List[np.ndarray], str]:
        """Process multiple uploaded images for teacher registration"""
        try:
            face_encodings = []
            processed_images = []
            
            for uploaded_file in uploaded_files:
                # Read image
                image = Image.open(uploaded_file)
                image_array = np.array(image)
                
                # Convert to RGB if needed
                if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                    rgb_image = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
                else:
                    rgb_image = image_array
                
                # Detect faces
                face_locations = self.detect_faces_in_image(rgb_image)
                
                if not face_locations:
                    return False, [], f"No face detected in {uploaded_file.name}"
                
                if len(face_locations) > 1:
                    return False, [], f"Multiple faces detected in {uploaded_file.name}. Please use images with single face."
                
                # Encode face
                face_encoding = self.encode_face(rgb_image, face_locations[0])
                
                if face_encoding is None:
                    return False, [], f"Could not encode face in {uploaded_file.name}"
                
                face_encodings.append(face_encoding)
                processed_images.append(rgb_image)
            
            # Average the encodings for better accuracy
            if face_encodings:
                # Return the first encoding for simplicity
                return True, processed_images, "Images processed successfully"
            else:
                return False, [], "No valid face encodings found"
                
        except Exception as e:
            return False, [], f"Error processing images: {str(e)}"
    
    def validate_face_quality(self, image: np.ndarray) -> Tuple[bool, str]:
        """Validate if the face image is of good quality for recognition"""
        try:
            # Convert to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            # Check image size
            height, width = rgb_image.shape[:2]
            if height < 100 or width < 100:
                return False, "Image too small. Please use higher resolution image."
            
            # Detect faces
            face_locations = face_recognition.face_locations(rgb_image)
            
            if not face_locations:
                return False, "No face detected. Please ensure face is clearly visible."
            
            if len(face_locations) > 1:
                return False, "Multiple faces detected. Please use image with single face."
            
            # Check face size relative to image
            top, right, bottom, left = face_locations[0]
            face_width = right - left
            face_height = bottom - top
            
            if face_width < 50 or face_height < 50:
                return False, "Face too small in image. Please move closer to camera."
            
            # Check if face takes reasonable portion of image
            face_area_ratio = (face_width * face_height) / (width * height)
            if face_area_ratio < 0.05:
                return False, "Face too small relative to image. Please move closer."
            
            return True, "Face quality is good"
            
        except Exception as e:
            return False, f"Error validating face quality: {str(e)}"
    
    def set_confidence_threshold(self, threshold: float):
        """Update confidence threshold"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
    
    def get_face_landmarks(self, image: np.ndarray) -> List[Dict]:
        """Get facial landmarks for detected faces"""
        try:
            # Convert BGR to RGB if needed
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
            
            face_landmarks_list = face_recognition.face_landmarks(rgb_image)
            return face_landmarks_list
            
        except Exception as e:
            st.error(f"Error getting face landmarks: {str(e)}")
            return []
