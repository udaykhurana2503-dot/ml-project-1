# Hand Gesture PowerPoint Controller 🖐️

A Python-based hand gesture detection system that allows users to control Microsoft PowerPoint slides using hand gestures.

## Features

* Real-time hand detection using MediaPipe
* Computer vision using OpenCV
* Next slide control using hand gestures
* Previous slide control using hand gestures
* Automatic PowerPoint window activation
* Gesture cooldown to prevent repeated slide changes

## Gestures

| Gesture         | Action         |
| --------------- | -------------- |
| ☝️ Pointing Up  | Next Slide     |
| ✌️ Victory Sign | Previous Slide |
| ✊ Fist          | No Action      |
| 🖐️ Open Palm   | No Action      |

## Technologies Used

* Python
* OpenCV
* MediaPipe
* PyAutoGUI
* PyGetWindow

## Requirements

* Windows PC
* Python 3.x
* Webcam
* Microsoft PowerPoint

## Installation

Clone the repository:

```bash
git clone YOUR-GITHUB-REPOSITORY-URL
```

Open the project folder:

```bash
cd Hand-Gesture-PowerPoint-Controller
```

Install the required packages:

```bash
pip install -r requirements.txt
```

## Running the Project

Run:

```bash
python main.py
```

Before using the gestures:

1. Open Microsoft PowerPoint.
2. Open your presentation.
3. Start the slideshow using `F5`.
4. Run the Python program.
5. Show your hand in front of the webcam.

## How It Works

The webcam captures the user's hand.

MediaPipe detects the hand landmarks.

The program analyzes the positions of the fingers and identifies the gesture.

PyAutoGUI then sends keyboard commands to PowerPoint:

* Right Arrow → Next Slide
* Left Arrow → Previous Slide

## Project Structure

```text
Hand-Gesture-PowerPoint-Controller/
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── LICENSE
```

## Limitations

* Currently designed primarily for Windows.
* Microsoft PowerPoint must be installed.
* A working webcam is required.
* The current version uses static hand poses rather than swipe detection.
* Gesture recognition can be affected by lighting and camera position.

## Future Improvements

* Add hand swipe detection
* Add Start/Stop presentation gesture
* Add slide show pause/resume
* Add volume control
* Add gesture-controlled mouse
* Add voice commands
* Improve gesture accuracy

## Author

Developed as a Python computer vision project using MediaPipe and OpenCV.