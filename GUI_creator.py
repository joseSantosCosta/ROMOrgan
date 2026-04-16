import FreeSimpleGUI as sg

def create_window():
    input_output_layout = [
        [sg.Text('Choose your input and output folder')],
        [sg.Text('Input folder'),sg.Input(key='-INPUT_FOLDER-',disabled=True),sg.FolderBrowse()],
        [sg.Text('Output folder'),sg.Input(key='-OUTPUT_FOLDER-',disabled=True),sg.FolderBrowse()]
    ]

    checkboxes_layout = [
        [sg.Checkbox(text='Keep original archives after extraction?',key='-KEEP_EXTRACT-')],
        [sg.Checkbox(text = 'Keep original files after compression?',key='-KEEP_COMPRESS-')],
        [sg.Checkbox(text="Create a library from scratch?",key="-FROM SCRATCH-")],
        [sg.Checkbox(text="Create console folders that are missing?",key="-MISSING FOLDERS-")],
        [sg.Button(button_text="START PROCESS",enable_events=True,key="-START_BUTTON-")]
    ]

    consoleside_layout = [
        [sg.ProgressBar(max_value=100)],
        [sg.Multiline(key = '-CONSOLE OUTPUT-',autoscroll=True,disabled=True,size=(50,20))],
        [sg.Button(button_text='ABORT',key='-ABORT BUTTON-')]
    ]

    layout = [
        [
            sg.Column(input_output_layout + checkboxes_layout),
            sg.VSeparator(),
            sg.Column(consoleside_layout)

        ]
    ]
    return sg.Window('ROMorgan',layout)
