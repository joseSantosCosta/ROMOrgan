import FreeSimpleGUI as sg


def create_first_window():
    button_layout = [
        [
            sg.Column([[sg.Button(button_text='Create library from scratch',key="-FROM SCRATCH-",enable_events=True)]]),
            sg.VSeparator(),
            sg.Column([[sg.Button(button_text='Add games to existing library',key="-ADD GAMES-",enable_events=True)]]),
            sg.VSeparator(),
            sg.Column([[sg.Button(button_text="Organize your library",key="-ORGANIZE-",enable_events=True)]]),
            sg.VSeparator()
        ]
    ]

    layout = [
        [sg.Text(text='ROMorgan',font=('Silkscreen',50))],
        [sg.Text(text='What you want to do?', size=(20, 1))],
        button_layout
    ]
    return sg.Window('ROMorgan',layout,finalize=True)

def create_add_window(adding=False):
    if adding == False:
        input_output_layout = [
            [sg.Text('Choose the folder where the games you want to add are')],
            [sg.Text('Games to add'),sg.Input(key='-INPUT_FOLDER-',disabled=True),sg.FolderBrowse()],
            [sg.Text('Choose the place where you want to create your new ROMs library')],
            [sg.Text('New ROMs library path'),sg.Input(key='-OUTPUT_FOLDER-',disabled=True),sg.FolderBrowse()]
        ]
    else:
        input_output_layout = [
            [sg.Text('Choose the folder where the games you want to add are')],
            [sg.Text('Games to add'),sg.Input(key='-INPUT_FOLDER-',disabled=True),sg.FolderBrowse()],
            [sg.Text('Choose your ROMs folder')],
            [sg.Text('Your ROMs folder'),sg.Input(key='-OUTPUT_FOLDER-',disabled=True),sg.FolderBrowse()]
        ]
    
   

    checkboxes_layout = [
        [sg.Checkbox(text='Keep original archives after extraction?',key='-KEEP_EXTRACT-')],
        [sg.Checkbox(text = 'Keep original files after compression?',key='-KEEP_COMPRESS-')],
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
    return sg.Window('ROMorgan',layout,finalize=True)

if __name__ == '__main__':
    window = create_first_window()

    while True:
        events,values = window.read(timeout=100)
        if events == sg.WIN_CLOSED:
            break
        elif events == '-FROM SCRATCH-':
            from_scratch = True
            window.close()
            window = create_add_window()


