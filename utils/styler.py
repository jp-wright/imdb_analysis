""" 
utilities
"""
from utils.palettes import *
from pandas import DataFrame
from typing import Union, List, Dict, Mapping


def colorize_frame(cell: Union[float, int, str], year: int, bg_clr_dct: Dict[str, str]):
    """
    asd
    """
    if cell == year:
        res = colorize_curr_year(cell, year)
    else:
        res = colorize_player_names_new(cell, conf_clr_dct, bg_clr_dct)
        # res = f"background-color: #FAFAFF; color: black"
    return res
    
    
def colorize_curr_year(cell: Union[float, int, str], year: int):
    """
    asd
    """
    # if cell == year:
    #     res = f"background-color: blue; color: white"
    # else:
    #     res = ''
        # res = f"background-color: #FAFAFF; color: black"
    # return res
    # return f{"background-color: blue; color: white" if cell == year else '#FAFAFF'}"
    return "background-color: blue; color: white"


def colorize_player_names_new(cell: Union[float, int, str], conf_clr_dct: Dict[str, str], bg_clr_dct: Dict[str, str]):
    """
    asd
    """
    return f'text-align:center; color:{conf_clr_dct.get(cell, "black")}; background-color:{bg_clr_dct.get(cell, "#FAFAFF")};'
    # return f'align:center; color:{conf_clr_dct.get(cell, "black")}; background-color:{bg_clr_dct.get(cell, "#FAFAFF")};'
    # return f'text-align:center; color:black; background-color:{bg_clr_dct.get(cell, "")};'
    # return f'text-align:center; color:black; background-color:{bg_clr_dct.get(cell, "#FAFAFF")};'
    # return f'text-align:center; color:black; background-color:{bg_clr_dct.get(cell, "#EAEAEE")};'
    # return f'text-align:center; color:black; background-color:{bg_clr_dct.get(cell, "#EDEDEE")};'


def style_frame(frame: DataFrame, bg_clr_dct: Dict[str, str], frmt_dct: Dict[str, str]={}, bold_cols: List=[], clr_yr: int=2000):
    """
    asd
    """
    return frame.reset_index(drop=True).style\
            .applymap(lambda cell: colorize_frame(cell, clr_yr, bg_clr_dct))\
            .format(frmt_dct)\
            .set_properties(**{'font-weight': 'bold'}, subset=bold_cols)
            # .applymap(lambda cell: colorize_curr_year(cell, clr_yr))\
            # .applymap(lambda cell: colorize_player_names_new(cell, bg_clr_dct))\

  