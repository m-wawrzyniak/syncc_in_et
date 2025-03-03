import pickle

from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout
import psychopy.iohub as io
from psychopy.hardware import keyboard

# Load the pickle file
with open("C:/Users/Badania/PycharmProjects/et_procedure/data/637455_et_syncc_in_procedure_2025-02-17_09h57.41.126.psydat", "rb") as f:  # "rb" means read binary
    data = pickle.load(f)

print(data._getExtraInfo())  # Check the loaded object
print(data.getAllEntries())