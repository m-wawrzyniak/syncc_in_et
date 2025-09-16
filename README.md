# SYNCC-IN Eyetracking Procedure


## Naming and definitions:

1. **Master PC** - PC on which the main procedure script is run. It is also supposed to be the PC which captures Child Subject ET data.
2. **Slave PC** - PC meant to capture Parent Subject ET data.
3. **User** - researcher operating the Master PC, responsible for ET registration.
4. **Subject** - child and parent dyad.
5. **Exec. monitor** - the monitor on which all stimuli meant for the Subjects are displayed.
6. **ET** - Eye-Tracking
7. **Main video** - snippets from Pixar movies, the main stimuli meant to be presented to the subjects.

## Paradigm timeline:
### As of 26.06 at the University of Warsaw

1. Both child and parent Subjects are already prepared for the procedure, according to ET Environment Preparation Guidelines. 
2. Senior researcher instructs the Subjects about the video presentation procedure. 
3. Senior researcher signals the readiness to the User.
4. User begins the procedure by executing run_procedure.bat
5. Command-line UI and simplified PsychoPy GUI open up. PsychPy GUI serves as a mean to input the logging data such as pseudo-anonymous subject dyad code.
6. User inputs the logging data and proceeds further by pressing 'OK'.
7. Throughout ET calibration, cartoon-like animation is presented, instructing the Subjects about their task in upcoming calibration procedure.
   1. The first part of calibration animation is initialized and awaits for User permission to continue.  
   2. The first part of calibration anim. is presented to Subjects. Once finished, awaits User input.
   3. The calibration of parent Subject is carried out. Awaits User input. NOTE: User can choose to repeat the calibration if the quality metrics were unsatisfactory.
   4. The second part of calib. anim. is initialized. Awaits User input.
   5. The calibration of child Subject is carried out. Awaits User input. NOTE: User can choose to repeat the calibration if the quality metrics were unsatisfactory.
   6. The third part od calib. anim. is initialized and presented.
8. The recording on both Subjects' ET devices begins.
9. Fixation cross is presented on exec. monitor. 
10. Three main videos are initialized. Photodiode signalization display is initialized. Awaits User input.
11. Main stimulation procedure:
    1. Fixation cross is removed.
    2. One of the main videos is randomly sampled (without replacement).
    3. Chosen main video is presented on exec. monitor.
    4. During the first 2-3 seconds of video presentation, photodiode signalization display informs EEG amplifier which video has just began.
    5. Once the video finishes (~60s), fixation cross is presented for 10 seconds.
    6. Repeats from step one until all three videos have been presented.
12. The recording on ET devices is finished. The script is on stand-by.
13. User informs senior researcher that the main stimulation procedure is finished.
14. Senior researcher instructs the Subjects about unrestricted conversation procedure.
15. Unrestricted conversation procedure:
    1. Senior researcher describes the topic to the Subjects 
    2. Senior researcher signals the readiness to the User. 
    3. User starts the unrestricted conversation procedure. The recording on both ET devices is started.
    4. Timer appears on the PsychoPy GUI. It counts down 30s, during which both Senior Researcher and User leave the room.
    5. After 30s, audio signal (C note) is played for 1s. After the signal, the Subjects are supposed to converse for 180s.
    6. Once the 180s are counted down by the script, another audio signal is executed. Subjects are supposed to stop conversing, Senior Researcher and User enter the room. The recording on both ET devices is stopped.
    7. The script awaits User input.
    8. Repeat from step 1 until both topic were covered.

16. The script shuts down both UI and saves data logs to prespecified directory.