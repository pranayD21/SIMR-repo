import cv2
from hsemotion.facial_emotions import HSEmotionRecognizer

# Initialize the emotion recognizer
model_name = 'enet_b0_8_best_afew'  # You can try other models if needed
emotion_recognizer = HSEmotionRecognizer(model_name=model_name, device='cpu')  # Use 'gpu' if available

# Load a pre-trained face detector from OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize the webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Unable to access the webcam.")
    exit()

print("Press 'q' to quit the application.")

while True:
    # Capture a frame from the webcam
    ret, frame = cap.read()
    if not ret:
        print("Error: Failed to capture a frame.")
        break

    # Convert the frame to grayscale for face detection
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the frame
    faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # Extract the face region
        face_img = frame[y:y+h, x:x+w]
        face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)

        # Predict the emotion
        try:
            emotion, scores = emotion_recognizer.predict_emotions(face_rgb, logits=False)
        except Exception as e:
            print(f"Error during emotion prediction: {e}")
            emotion = "Error"

        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Annotate the frame with the predicted emotion
        cv2.putText(frame, f'Emotion: {emotion}', (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

    # Display the frame with annotations
    cv2.imshow('Live Facial Emotion Recognition', frame)

    # Quit the application when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()