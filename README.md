# Automated Sorting System Using Niryo 6-DOF Robot

## Project Overview
The objective of this project is to design and implement an automated sorting system using a 6 Degrees of Freedom (6-DOF) Niryo robotic manipulator. The system integrates artificial intelligence and computer vision to detect defective objects and automatically separate them from compliant parts.

This project combines collaborative robotics, machine vision, and industrial intelligence to enhance product quality and manufacturing efficiency.

---

## Objectives
- Develop an automated sorting process using a robotic arm  
- Implement a vision-based AI model to classify objects  
- Detect defective items in real time  
- Improve productivity and reduce human intervention  
- Ensure consistent quality control in industrial workflows  

---

## System Architecture
The system is composed of three main components:

### 1. Robotic Manipulator
- Niryo 6-DOF robotic arm  
- Responsible for pick-and-place operations  
- Executes sorting based on classification results  

### 2. Vision System
- Camera-based object detection  
- Captures images of items on the workspace  
- Sends data to the AI model for processing  

### 3. Artificial Intelligence Model
- Trained to distinguish between defective and non-defective objects  
- Outputs classification results used to guide the robot  

---

## Technologies Used
- ROS2 (Robot Operating System 2)  
- Gazebo Simulator  
- Python  
- OpenCV (for image processing)  
- Machine Learning / Deep Learning frameworks (e.g., TensorFlow or PyTorch)  

---

## Workflow
1. Capture image of object using camera  
2. Process image using the AI model  
3. Classify object (defective / non-defective)  
4. Send command to the robot  
5. Robot picks and places object in the appropriate location  

---

## Project Phases

### Phase 1: Simulation
- Environment setup using Gazebo  
- Integration with ROS2  
- Testing robot motion and perception pipeline  

### Phase 2: Experimental Validation
- Deployment on real Niryo robot  
- Real-world object detection and sorting  
- Performance evaluation and optimization  

---

## Expected Results
- Accurate classification of objects  
- Efficient and reliable sorting process  
- Reduced human error  
- Improved production speed and quality  

---

## Future Improvements
- Enhance AI model accuracy with larger datasets  
- Add multi-object detection capabilities  
- Optimize robot trajectory planning  
- Integrate with industrial production lines  

---

## Project Structure (Example)
