# SmoothOperator: Joystick-Based Neuro-Motor Assessment Toolkit

**SmoothOperator** is a digital biomarker platform designed to quantify motor and cognitive impairments associated with neurodegenerative diseases (e.g., Parkinson’s Disease, Multiple Sclerosis) using high-frequency joystick input.

By transitioning from subjective clinical observations to objective, high-resolution data, this toolkit enables the early screening of tremors, bradykinesia, and executive dysfunction.

---

##  Core Assessment Modules

The toolkit decomposes complex motor behavior into several validated neuro-physiological metrics:

* **Tremor Analysis (`tremor_analysis.py`)**: Utilizes **Fast Fourier Transform (FFT)** to isolate pathological tremors (typically 4–8 Hz) from intentional movement and sensor noise.
* **Motor Planning & Fitts's Law (`fitts_law.py`)**: Models the relationship between target distance, width, and movement time to quantify motor precision and "speed-accuracy trade-offs."
* **Reaction Time (`reaction.py`)**: Measures the latency between visual stimuli and physical motor response to assess conduction delays in the central nervous system.
* **Path Smoothness (`path_smoothness.py`)**: Calculates **Jerk** (the third derivative of position) and path efficiency to evaluate coordination and rigidity.
* **Cognitive Load / Dual-Tasking (`dual_task.py`)**: Evaluates the interference between motor control and simultaneous cognitive processing.
* **Target Tracking (`target_tracking.py`)**: Assesses dynamic visuospatial coordination and pursuit smoothness.
* **Tapping Performance (`tapping.py`)**: Digitizes the traditional finger-tapping test to measure rhythmicity and fatigue.

---

##  Technical Implementation

* **Language:** Python
* **Signal Processing:** Real-time $(x, y)$ coordinate sampling and frequency-domain analysis.
* **Experimental Design:** Integrated targeting tasks modeled after clinical **UPDRS** (Unified Parkinson's Disease Rating Scale) protocols.

##  Future Research Directions 

* **Machine Learning Integration:** Training classifiers (Random Forest/SVM) to categorize disease stages based on movement "jerk" and spectral power.
* **Signal Denoising:** Implementing **Kalman Filtering** to separate hardware-induced jitter from biological tremors.
* **Longitudinal Tracking:** Developing a cloud-based pipeline for at-home, long-term monitoring of patient "off-periods."

---
*Note: This project is part of an ongoing exploration into non-invasive diagnostic tools for neuro-rehabilitation.*
