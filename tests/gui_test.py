import time
import datetime
import PySimpleGUI as sg


def load_projects():
    return {f"P_{e}": e for e in range(2)}


def load_queries(in_project_id):
    return {f"P_{in_project_id}_Q_{e}": e for e in range(100, 105, 1)}


# Filled by data
PROJECT_NAME_TO_ID = {}
QUERY_NAME_TO_ID = {}

PROJECT_ID = None
QUERY_ID = None
START_DATE = None
END_DATE = None

sg.theme('DarkAmber')  # Add a touch of color


def main():
    global PROJECT_NAME_TO_ID
    global QUERY_NAME_TO_ID
    global PROJECT_ID
    global QUERY_ID
    global START_DATE
    global END_DATE

    all_projects = list(PROJECT_NAME_TO_ID.keys())
    all_projects.sort()
    project_queries = list(QUERY_NAME_TO_ID.keys())
    project_queries.sort()

    layout = [
        [sg.Text("Token file:", font=("Courier", 14), size=(15,2)),
         sg.Checkbox(key="C_NoToken", text="-\"I don't have a token file\" ", default=False, enable_events=True,
                     tooltip="Check this box if you don't have a token file.", font=("Courier", 14)),
         sg.Button(key="B_RequestToken", button_text="Get New Token", visible=False, font=("Courier", 14))],

        [sg.InputText(key="IT_TokenFile", size=(60, 3), font=("Courier", 14)), sg.FileBrowse(target="IT_TokenFile", font=("Courier", 14),
                                                                       file_types=[("JSON files", "*.json"),
                                                                                   ("All files", "*")])],
        [sg.HorizontalSeparator()],

        [sg.Button(k="B_LoadProjects", button_text="Load all projects", font=("Courier", 14)), sg.Text(" " * 30),
         sg.Button(k="B_LoadQueries", button_text="Load Queries from the Project", font=("Courier", 14))],

        [sg.Listbox(key="LB_Projects", values=all_projects, enable_events=True, size=(30, 5), font=("Courier", 14)),
         sg.Listbox(key="LB_Queries", values=project_queries, enable_events=True, size=(30, 10), font=("Courier", 14))],

        [sg.HorizontalSeparator()],

        [sg.Text("Start Datetime                UTC-Timezone           End Datetime", font=("Courier", 14))],

        [sg.InputText(key="I_StartDate", size=(20, 1), enable_events=True, font=("Courier", 14)),
         sg.CalendarButton(key="CB_StartDate", button_text='Date', target='I_StartDate', format='%Y-%m-%d',
                           close_when_date_chosen=True, font=("Courier", 14)),
         sg.Text(" " * 30),
         sg.InputText(key="I_EndDate", size=(20, 1), enable_events=True, font=("Courier", 14)),
         sg.CalendarButton(key="CB_StartDate", button_text='Date', target='I_EndDate', format='%Y-%m-%d',
                           close_when_date_chosen=True, font=("Courier", 14))
         ],

        [sg.Slider(k="S_StartHours", range=(0, 23), default_value=0, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Hours of Start Datetime", enable_events=True, font=("Courier", 14)),
         sg.Text("            Hours            ", font=("Courier", 14)),
         sg.Slider(k="S_EndHours", range=(0, 23), default_value=23, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Hours of End Datetime", enable_events=True, font=("Courier", 14))],

        [sg.Slider(k="S_StartMinutes", range=(0, 59), default_value=0, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Minutes of Start Datetime", enable_events=True, font=("Courier", 14)),
         sg.Text("           Minutes           ", font=("Courier", 14)),
         sg.Slider(k="S_EndMinutes", range=(0, 59), default_value=59, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Minutes of End Datetime", enable_events=True, font=("Courier", 14))],

        [sg.Slider(k="S_StartSeconds", range=(0, 59), default_value=0, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Seconds of Start Datetime", enable_events=True, font=("Courier", 14)),
         sg.Text("           Seconds           ", font=("Courier", 14)),
         sg.Slider(k="S_EndSeconds", range=(0, 59), default_value=59, resolution=1, orientation='horizontal',
                   size=(20, 20), tooltip="Seconds of End Datetime", enable_events=True, font=("Courier", 14))],

        [sg.Text(key="T_StartDateTime", text="", font=("Courier", 16)), sg.Text(" " * 20, font=("Courier", 16)), sg.Text(key="T_EndDateTime", text="", font=("Courier", 16))],

        [sg.HorizontalSeparator()],

        [sg.Button('Download', font=("Courier", 14)), sg.InputText(key="IT_OutputFile", font=("Courier", 14)), sg.Push(), sg.Button('Cancel', font=("Courier", 14))],

        [sg.HorizontalSeparator()],

        [sg.Text(key="T_Status")]
    ]

    TimeHandlers = {"I_StartDate", "I_EndDate", "S_StartHours", "S_EndHours", "S_StartMinutes", "S_EndMinutes", "S_StartSeconds", "S_EndSeconds"}

    # Create the Window
    window = sg.Window("Chathura's Brandwatch Data Downloader", layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        print("EVENT: ", event, " \t VALUES: ", values)
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            break
        if event == "B_LoadProjects":
            PROJECT_NAME_TO_ID = load_projects()
            all_projects = list(PROJECT_NAME_TO_ID.keys())
            all_projects.sort()
            window["LB_Projects"].update(all_projects)
        if event == "B_LoadQueries":
            QUERY_NAME_TO_ID = load_queries(PROJECT_ID)
            project_queries = list(QUERY_NAME_TO_ID.keys())
            project_queries.sort()
            window["LB_Queries"].update(project_queries)
        if event == "LB_Projects":
            PROJECT_ID = values["LB_Projects"][0] if len(values["LB_Projects"]) > 0 else None
            window["T_Status"].update(
                "Project: {} Query: {} Datetime Range: {} to {}".format(PROJECT_ID, QUERY_ID, START_DATE, END_DATE))
        if event == "LB_Queries":
            QUERY_ID = values["LB_Queries"][0] if len(values["LB_Queries"]) > 0 else None
            window["T_Status"].update(
                "Project: {} Query: {} Datetime Range: {} to {}".format(PROJECT_ID, QUERY_ID, START_DATE, END_DATE))
        if event == "C_NoToken":
            window["B_RequestToken"].update(visible=values["C_NoToken"])
        if event in TimeHandlers:
            START_DATE = "{}T{:02}:{:02}:{:02}".format(values["I_StartDate"], int(values["S_StartHours"]),
                                          int(values["S_StartMinutes"]), int(values["S_StartSeconds"]))
            END_DATE = "{}T{:02}:{:02}:{:02}".format(values["I_EndDate"], int(values["S_EndHours"]), int(values["S_EndMinutes"]), int(values["S_EndSeconds"]))
            window["T_StartDateTime"].update(START_DATE)
            window["T_EndDateTime"].update(END_DATE)
            window["T_Status"].update("Project: {} Query: {} Datetime Range: {} to {}".format(PROJECT_ID, QUERY_ID, START_DATE, END_DATE))
        print(PROJECT_ID, QUERY_ID)
    window.close()


if __name__ == "__main__":
    main()
