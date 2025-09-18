# SYNCC-IN Eyetracking Procedure

This repository contains research software for running a **multimodal registration paradigm** involving child–parent dyads, combining **eye tracking (ET)** with **EEG**.  
Developed within the **SYNCC-IN project** (University of Warsaw).

The system integrates:  
- **Two Pupil Core eye trackers** (child and parent)  
- **EEG amplifier synchronization** (via photodiode signalization)  
- **Stimulus presentation** (Pixar movie clips + conversation prompts)  
- **Custom experiment control and logging** (PsychoPy GUI + command-line interface)  

---

## Overview

The paradigm is divided into three main phases:  

1. **Calibration**
   - Child and parent ET calibration
   - Animated cartoon instructing the child about the calibration
   - Optional calibration repetition

1. **Main stimulation**
   - Randomized presentation of three short Pixar movie clips  
   - Photodiode signalization during stimulus onset for EEG synchronization  

2. **Unrestricted conversation**  
   - Audio-cued free conversation between child and parent (two topics, 3 minutes each)  
   - Both ET devices and EEG continue recording  

This design enables **precise temporal alignment** of multimodal signals (ET, EEG, audio, video) during naturalistic parent–child interaction.  

---

## Key Features

- **Multimodal synchronization**  
  - Dual eye-tracking streams (child + parent)  
  - EEG amplifier synchronization via photodiode  
  - Stimulus onset and offsets logged automatically  

- **Automated experiment flow**  
  - Stepwise calibration with animated instructions  
  - Randomized video stimulus presentation  
  - Controlled free-conversation blocks with audio cues  

- **Experiment control**  
  - Hybrid command-line + PsychoPy GUI interface  
  - Logging of pseudo-anonymous subject IDs  
  - Clear user prompts for calibration, repetition, and procedure continuation  
  - Real-time communication between Python scripts and Pupil Capture instances via **pylsl** over Wi-Fi 

- **Data handling**  
  - Logs saved in `data/` subfolder  
  - Eye-tracking recordings stored by **Pupil Capture v3.5.1**  
  - Synchronization signals embedded in ET and EEG streams  

---

## Requirements

- **Python**: 3.10  
- **Dependencies**: listed in `requirements.txt`  
- **Operating system**: Windows 10/11  
- **Hardware setup**:  
  - Two PCs (Master + Slave)  
  - Two Pupil Core ET devices  
  - EEG amplifier with photodiode input  
  - Shared display (executive monitor for stimuli)  

---

## Usage

The main entry point is:

```bash
run_procedure.bat
```

This launches:

- Command-line interface

- Simplified PsychoPy GUI for dyad ID input and procedure control

## Procedure outline

1. **Calibration**

    - Animated instruction - part 1
    - Parent calibration > quality check > repeat if needed
    - Animated instruction - part 2
    - Child calibration > quality check > repeat if needed
    - Animated instruction - part 3

2. **Main stimulation**

    - Randomized Pixar clips (~60s each)
    - Pupil Capture annotations and photodiode markers during onset and offset
    - Fixation cross between trials

3. **Unrestricted conversation**

    - Two topics - 3 minutes each

    - Audio cues for start/stop

    - Countdown timer displayed for the User

See PARADIGM.md for the full, detailed paradigm timeline.

## Data & Outputs

- **ET recordings** > handled by Pupil Capture (formats: video, gaze, world data depending on configuration)

- **Logs** > stored locally in data/ subfolder

- **EEG markers** > photodiode signal encodes stimulus onset for synchronization

## Repository Structure

```bash
SYNCC-IN/
│
├── data/                # Experiment logs (auto-generated)
├── misc/                # Helper Python scripts.
├── config.py            # Configuration and hyperparameters
├── m00_configuration_setup.py      # Paths setup, names etc.
├── m01_procedure_setup.py          # Procedure setup, PsychoPy objects, communication etc.
├── m02_psychopy_routines.py        # PsychoPy routines handling
├── m03_pupilcapture_comms.py       # Pupil Capture communications handling
├── main.py              # Main executable script
├── PARADIGM.md          # Paradigm timeline
├── README.md            # README
├── requirements.txt     # Python dependencies
└── run_procedure.bat    # Win entry point


```

## Attribution

Developed by **Mateusz Wawrzyniak** within the **SYNCC-IN project**, University of Warsaw.

With additional contributions in the early project stages by **Maciej Padarz**.

This software is released under the MIT License.

Partner laboratories are welcome to reuse or adapt the codebase.