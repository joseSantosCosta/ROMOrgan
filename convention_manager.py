from pathlib import Path
import logging

possible_conventions = ['ES-DE','RetroArch','Full name','Manufacture/System']
possible_subs = ['','alphabetical','region']

def create_folder_based_in_convention(convention:tuple):
    """
    This function will receive a tuple with the convention decided by the user and a sub telling if the user wants subfolders
    organized alphabetically or by region (convention,sub)

    possible conventions are 'ES-DE','RetroArch','Full name' and 'Manufacture/System'
    
    possible subs are  '',alphabetical and region
    
    """




