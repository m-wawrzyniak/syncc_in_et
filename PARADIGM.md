# SYNCC-IN Eyetracking Procedure

This document describes the detailed procedure for running the **SYNCC-IN multimodal registration experiment**, involving child–parent dyads with **eye-tracking (ET)** and **EEG** recordings.

---

## Naming and Definitions

- **Master PC** – Runs the main procedure script and records the child subject’s ET data.  
- **Slave PC** – Records the parent subject’s ET data.  
- **User** – Researcher operating the Master PC, responsible for ET registration.  
- **Subject** – Child–parent dyad participating in the experiment.  
- **Exec. monitor** – Display where all stimuli for the subjects are presented.  
- **ET** – Eye tracking.  
- **Main video** – Pixar movie snippets, which are the primary stimuli.  

---

## Paradigm Timeline
*As of 18.09.2025, University of Warsaw*

1. Both child and parent subjects are prepared according to ET environment preparation guidelines.  
2. The senior researcher provides instructions to the subjects regarding the video presentation procedure.  
3. The senior researcher signals readiness to the User.  
4. The User starts the procedure by executing `run_procedure.bat`.  
5. Both the command-line UI and a simplified PsychoPy GUI launch.  
   - The PsychoPy GUI is used for entering logging data, such as the pseudo-anonymous dyad code.  
6. The User enters the required logging data and proceeds by pressing 'OK'.  
7. **ET Calibration Phase**:  
   1. The first part of the calibration animation is initialized and awaits User confirmation.  
   2. This first animation segment is presented to the subjects; upon completion, it waits for User input.  
   3. Parent calibration is performed. The User can repeat it if quality metrics are unsatisfactory.  
   4. The second calibration animation segment is initialized and awaits User confirmation.  
   5. Child calibration is performed. The User can repeat it if quality metrics are unsatisfactory.  
   6. The third calibration animation segment is initialized and presented.  
8. Recording begins on both ET devices.  
9. A fixation cross is displayed on the exec. monitor.  
10. The three main videos are initialized, and the photodiode signalization display is prepared. The system waits for User confirmation.  
11. **Main Stimulation Procedure**:  
    1. Fixation cross is removed.  
    2. One of the main videos is randomly selected (without replacement).  
    3. The chosen video is presented on the exec. monitor.  
    4. During the first 2–3 seconds of video presentation, the photodiode signal informs the EEG amplifier of the video onset.  
    5. After the video ends (~60 seconds), a fixation cross is displayed for 10 seconds.  
    6. Steps 1–5 are repeated until all three videos have been presented.  
12. Recording on both ET devices stops. The script enters standby mode.  
13. The User informs the senior researcher that the main stimulation procedure is complete.  
14. The senior researcher provides instructions to the subjects for the unrestricted conversation procedure.  
15. **Unrestricted Conversation Procedure**:  
    1. The senior researcher describes the topic to the subjects.  
    2. The senior researcher signals readiness to the User.  
    3. The User starts the unrestricted conversation procedure; recording on both ET devices begins.  
    4. A countdown timer (30 seconds) is displayed on the PsychoPy GUI while the User and senior researcher leave the room.  
    5. After 30 seconds, an audio signal (C note, 1 second) indicates that the subjects should begin conversing for 180 seconds.  
    6. After 180 seconds, another audio signal instructs subjects to stop conversing. The senior researcher and User return, and ET recording is stopped.  
    7. The script waits for User input.  
    8. Steps 1–7 are repeated for the second conversation topic.  
16. The script shuts down all UI elements and saves data logs to the prespecified directory.  
