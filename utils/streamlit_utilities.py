""" 
utilities
"""
import streamlit as st
from typing import Optional, Sequence, List, Union
from collections.abc import Callable
import requests
from pandas import read_csv, DataFrame
import time

def local_css(file_name):
    """
    """
    with open(file_name) as f:
        st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)


def load_lottieurl(url: str):
    """
    """
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def gradient(grad_clr1, grad_clr2, title_clr, subtitle_clr, title, subtitle, htag_lvl: int=1, title_size: int=60, subtitle_size: int=17):
    """
    """
    st.markdown(f'<h{htag_lvl} style="text-align:center;background-image: linear-gradient(to right,{grad_clr1}, {grad_clr2});font-size:{title_size}px;border-radius:2%;">'
                f'<span style="color:{title_clr};">{title}</span><br>'
                f'<span style="color:{subtitle_clr};font-size:{subtitle_size}px;">{subtitle}</span></h{htag_lvl}>', 
                unsafe_allow_html=True)
    

def show_img(url: str, width: int=100, height: int=100, hover: Optional[str]=None, caption: Optional[str]=None, link: bool=False, spacer: Optional[int]=1):
    """
    """    
    img = f'''<img src="{url}" width={width} height={height}>'''
    if caption:
        img = img.replace('>', '') + f' alt={hover} title={hover}>'
    if link:
        img = f'<a href="{url}">' + img + '</a>'

    st.markdown(img, unsafe_allow_html=True)

    if caption:
        st.markdown(f"<font size=2>{caption}</font>", unsafe_allow_html=True)
    if spacer:
        st.markdown("<BR>" * spacer, unsafe_allow_html=True)

def init_to_null(state, key, val):
    '''Initialize st.session_state to val if key not in state.'''
    if key not in state:
        state[key] = val
    # return state

# @st.cache_data(persist='disk')
def set_frame(load_demo: bool=False, url: Optional[str]=None):
    """ Probably just a function for use during development but should be removed before deployment b/c every user will have to load the data from a URL they provide.?
    
    Set the DataFrame in st.session_state.df. If it's already set, return it.
    It is also possible to use the @st.cache_data decorator to cache the data instead of storing it in st.session_state.
    But with multiple pages, it's not clear how to use the decorator in a way that makes the data available to all pages.

    load_demo : bool : whether to load the demo list [used in testing]
    """

    
    if st.session_state.df is not None:
        frame = st.session_state.df
    elif url:
        pass
        ## Make this scrape the IMDb list URL?
        # with st.spinner('Loading Data...'):
        #     frame = read_csv(url, dtype=({'year': int, 'gross': float}))
        #     st.session_state.df = frame
    elif load_demo:
        with st.spinner('Loading Data...'):
            # time.sleep(3)
            frame = read_csv('data/input/imdb_demo_list.csv', dtype=({'year': int, 'gross': float}))
            # frame = read_csv('data/input/imdb_big_list.csv', dtype=({'year': int, 'decade': int, 'gross': float}))
            st.session_state.df = frame
    else:
        st.error('🚨 No data found or URL to scrape provided. Please provide a URL or use the Demo List.')
        raise Exception('No data found or URL to scrape provided. Please provide a URL or use the Demo List.')

    return frame        


def get_movie_poster(title: str, width: int=200, height: int=300):
    '''Get the movie poster from OMDB API.
    title : str : the title of the movie
    width : int : the width of the image
    height : int : the height of the image
    '''
    url = f'http://www.omdbapi.com/?t={title}&apikey=trilogy'
    r = requests.get(url)
    if r.status_code != 200:
        return None
    try:
        poster = r.json()['Poster']
    except KeyError:
        return None
    return poster


def get_movie_info(title: str):
    '''Get the movie info from OMDB API.
    title : str : the title of the movie
    '''
    url = f'http://www.omdbapi.com/?t={title}&apikey=trilogy'
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def plot_radio_buttons_sidebar(radio_buttons: list, default: str, key: str, label: str, help_tip: str):
    '''Plot radio buttons.
    radio_buttons : list : the list of radio buttons to plot
    default : str : the default value
    key : str : the key to use for the radio buttons
    label : str : the label for the radio buttons
    help_tip : str : the help tip for the radio buttons
    '''
    st.sidebar.markdown(f'<h3>{label}</h3>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<font size=2>{help_tip}</font>', unsafe_allow_html=True)
    return st.sidebar.radio('', radio_buttons, index=radio_buttons.index(default), key=key)


def plot_checkbox_sidebar(checkboxes: list, default: list, key: str, label: str, help_tip: str):
    '''Plot checkboxes.
    checkboxes : list : the list of checkboxes to plot
    default : list : the default value
    key : str : the key to use for the checkboxes
    label : str : the label for the checkboxes
    help_tip : str : the help tip for the checkboxes
    '''
    st.sidebar.markdown(f'<h3>{label}</h3>', unsafe_allow_html=True)
    st.sidebar.markdown(f'<font size=2>{help_tip}</font>', unsafe_allow_html=True)
    return st.sidebar.checkbox('', checkboxes, default, key=key)


def plot_xy_radio_buttons(x_label: str='', y_label: str='', x_buttons: Sequence[Union[str, int]]=[], y_buttons: Sequence[Union[str, int]]=[], xindex: int=0, yindex: int=0, xhelp: Optional[str]=None, yhelp: Optional[str]=None, xkey: str='', ykey: str='', x_format: Callable[[str], str]=str, y_format: Callable[[List[str]], str]=str, horizontal: bool=True, col_spacing: List[Union[float, int]]=[.3, .45, .25]) -> tuple:
    
    assert x_buttons or y_buttons, 'At least one of x_buttons or y_buttons must be provided.'

    if not (x_buttons and y_buttons) and (x_buttons or y_buttons):
        if x_buttons:
            x = st.radio(x_label, x_buttons, index=xindex, key=xkey, format_func=x_format, help=xhelp, horizontal=horizontal)
            y = None
        else:
            x = None
            y = st.radio(y_label, y_buttons, index=yindex, key=ykey, format_func=y_format, help=yhelp, horizontal=horizontal)
        
    if x_buttons and y_buttons:
        col1, _, col3 = st.columns(col_spacing)
        with col1:
            x = st.radio(x_label, x_buttons, index=xindex, key=xkey, format_func=x_format, help=xhelp, horizontal=horizontal)
        with col3:
            y = st.radio(y_label, y_buttons, index=yindex, key=ykey, format_func=y_format, help=yhelp, horizontal=horizontal)

    return x, y




    # col1, col2, _ = st.columns([.35, .3, .35])
    #     with col1:
    #         x = st.radio("Select Rating System", ('metacritic', 'imdb', 'combo'), horizontal=True)
    #         x = x + '_score'
    #     with col2:
    #         y = st.radio("Select Raw Value or Adjusted for Inflation", ('gross', 'gross_adj_2023'), horizontal=True)



def set_sidebar_menu():
    with st.sidebar:
        st.markdown('## IMDb Lists')
        st.markdown('### 🎬 [IMDb](https://www.imdb.com) is a great source for film data.')
        st.markdown('### 📈 Here you can scrape any IMDb list and analyze it.')
        st.markdown('### 📊 The data is then available for further analysis in the [Data](/data) page.')
        st.markdown('### 📜 You can also use the data to play a game in the [Game](/game) page.')
        st.markdown('### 📌 [GitHub](')