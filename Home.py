import streamlit as st
import pandas as pd
import re
from typing import Any
import logging
logging.basicConfig(level=logging.INFO, filename='logs/page_home.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
from utils.streamlit_utilities import gradient, local_css, init_to_null
from utils.imdb_acquisition import IMDB
from utils.palettes import blue_bath1, streamlit_blue, fft_knight_male
import utils.utilities as utl



class PageHome():
    """Layout class for Home page.
    """
    def __init__(self):
        st.set_page_config(page_title="IMDb Lists", layout="wide", page_icon='🎥', initial_sidebar_state="expanded")
        # local_css("style/style.css")
        self.initialize_state()
        # st.sidebar.markdown(info['Photo'], unsafe_allow_html=True)
        self.page_header()
        
        if st.session_state.df is not None:
            self.df = st.session_state.df

        self.get_list_input()
        # st.write(st.session_state.df)
        # st.write(st.session_state)

        if st.session_state.film_frame:
            self.list_preview()
            st.session_state.list_processed = True

        if st.session_state.list_processed:
            self.name_that_film(self.df)


    def initialize_state(self):
        state = st.session_state
        init_to_null(state, 'list_id', None)
        init_to_null(state, 'list_processed', False)
        init_to_null(state, 'film_frame', False)
        init_to_null(state, 'df', None)
        init_to_null(state, 'url', None)
        init_to_null(state, 'correct_guesses', 0)
        init_to_null(state, 'total_session_guesses', 0)
        init_to_null(state, 'single_film_guesses', 0)
        init_to_null(state, 'film_guess', False)
        init_to_null(state, 'show_answer', False)
        init_to_null(state, 'film_title', None)
        init_to_null(state, 'film_description', None)
        init_to_null(state, 'guessed_titles', [])
        init_to_null(state, 'used_films', [])
        init_to_null(state, 'completed_game', False)
        init_to_null(state, 'all_films_used', False)
        
    def page_header(self):
        gradient(grad_clr1=blue_bath1[1], grad_clr2=blue_bath1[3], title_clr=blue_bath1[5], subtitle_clr='#fcfbfb', title=f"🎬 IMDb Lists", subtitle="Here you can scrape any IMDb list and analyze it.", subtitle_size=27)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
    def get_list_input(self):
        '''provide list URL to scrape'''

        def get_list_id(url: str):
            '''get the IMDb list id from the URL to use when saving file'''

            pat = r".*(list/(?P<list_id>ls\d+))/?\??"
            match = re.search(pat, url)
            if match:
                self.list_id = match.group("list_id")
                if not st.session_state.list_id: st.session_state.list_id = self.list_id
            else:
                st.error('🚨 Provided URL {url} not of an IMDb list.')
                logging.error(f"Provided URL {url} not of an IMDb list.")
                raise ValueError(f"Provided URL {url} not of an IMDb list.")
            
        st.markdown('#### IMDb List URL')
        with st.container():
            col1, col2 = st.columns([.75, .25])
            with col1:
                with st.form(key="url_form", clear_on_submit=False):
                        self.url = st.text_input("Paste the URL of the IMDb list you want to scrape (any page of the list is fine):", key='list_url_input', value='https://www.imdb.com/list/ls528069836/').strip()
                        submitted = st.form_submit_button("Submit")
                        if submitted:
                            if 'www.imdb.com/list/' in self.url:
                                get_list_id(self.url)
                                with st.spinner('Scraping...'):
                                    self.scrape_list(self.url)
                                st.success('List scraped successfully!', icon='✅')
                                st.session_state.film_frame = True
                            else:
                                st.write('Provided URL not of an IMDb list. Please try again.')
            with col2:
                if st.button('Or use a Demo List', key='demo_list_button'):
                    self.demo_list(big_list=True)
                    st.session_state.film_frame = True
                if st.session_state.df is not None:
                    self.save_list_to_csv(st.session_state.df)

    def scrape_list(self, url):
        '''load page based on user input'''
        self.imdb = IMDB(url)
        self.df = self.imdb.df
        # if st.session_state.df is None: 
        st.session_state.df = self.df

    def demo_list(self, big_list: bool=False):
        st.markdown(f'<font color={streamlit_blue}>Using a pre-saved list.</font>', unsafe_allow_html=True)
        if big_list:
            self.df = pd.read_csv('data/input/imdb_big_list.csv')
        else:
            self.df = pd.read_csv('data/input/imdb_demo_list.csv')
        # if st.session_state.df is None: 
        st.session_state.df = self.df

    def save_list_to_csv(self, frame: pd.DataFrame):
        '''download list of films to local machine'''
        @st.cache_data
        def convert_df(df):
            # Cache the conversion to prevent computation on every rerun
            return df.to_csv().encode('utf-8')

        csv = convert_df(frame)

        st.download_button(
            label="Download entire list as CSV",
            data=csv,
            file_name=f'imdb_list_{st.session_state.list_id}.csv',
            mime='text/csv',
        )
        
    def list_preview(self):
        """show a preview of the list you entered."""
        
        st.markdown('<BR><BR>', unsafe_allow_html=True)
        st.markdown(f"<div align=center><font color={streamlit_blue} size=6>List Preview</font></div>", unsafe_allow_html=True)
        st.markdown('<BR>', unsafe_allow_html=True)
        st.dataframe(self.format_frame(self.df).set_index('title').sample(5))
        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown(f"<div align=center><font color={streamlit_blue} size=6>Quick Stats</font></div>", unsafe_allow_html=True)
        st.markdown('<BR>', unsafe_allow_html=True)
        self.intro_summary(self.df)

    def format_frame(self, frame: pd.DataFrame):
        frame = frame.assign(gross=lambda f: f['gross'].div(1000000).map("${:,.1f} M".format))\
                .assign(gross_adj_2023=lambda f: f['gross_adj_2023'].div(1000000).map("${:,.1f} M".format))\
                .assign(imdb_votes=lambda f: f['imdb_votes'].div(1000).map("{:,.0f} K".format))\
                .assign(year=lambda f: f['year'].astype(int).map("{:d}".format))
        return frame

    def intro_summary(self, frame: pd.DataFrame):
        '''show summary stats of films from provided list'''
        def write_summary(text: str, val: Any, color: str=streamlit_blue):
            st.write(f"<div align=center>{text}: <font color={color}><b>{val}</b></font></div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            write_summary("Total films in list", frame.shape[0])
            write_summary("Total actors in list", utl.get_unique_count_from_many_cols(frame, 'star'))
            write_summary("Total directors in list", frame['director'].nunique())
            write_summary("Total genres in list", utl.get_unique_count_from_many_cols(frame, 'genre'))

        with col2:
            write_summary("Average Combined rating", f"{frame['combo_score'].mean():.1f}")
            write_summary("Average Metacritic rating", f"{frame['metacritic_score'].mean():.1f}")
            write_summary("Average IMDb voter rating", f"{frame['imdb_score'].mean():.1f}")
            write_summary("Average IMDb votes per film", f"{frame['imdb_votes'].div(1000).mean():,.0f} K")

        with col3:
            write_summary("Highest gross (raw)", f"${frame['gross'].div(1000000).max():,.1f} M")
            write_summary("Highest gross (adj. for inflation)", f"${frame['gross_adj_2023'].div(1000000).max():,.1f} M")

    def name_that_film(self, frame: pd.DataFrame):
        '''show a random film from the list'''
        
        def header():
            gradient(grad_clr1=blue_bath1[1], grad_clr2=blue_bath1[3], title_clr=blue_bath1[5], subtitle_clr='#fcfbfb', title=f"🤔 How Well Do You Know Film?", subtitle="A Quiz On Your List", htag_lvl=3, title_size=45, subtitle_size=23)
       
        def set_title_and_description():
                if not st.session_state.film_title: 
                    film = frame[frame['genre1'].ne('Documentary')].sample(1) ## maybe show info about film upon completion
                    
                    if set(frame['title'].values).issubset(st.session_state.used_films):
                        st.write(f"""<BR><div align=center><font size="6" color={fft_knight_male[5]}>Game Over -- All films used!</font></div>""", unsafe_allow_html=True)
                        st.session_state.update(completed_game=True, all_films_used=True)

                    if st.session_state.all_films_used == False: ## prevent infinite loop
                        while film['title'].values[0] in st.session_state.used_films:
                            film = frame[frame['genre1'].ne('Documentary')].sample(1)
                    st.session_state.film_title = film['title'].values[0]
                    st.session_state.used_films.append(film['title'].values[0])

                if not st.session_state.film_description: 
                    st.session_state.film_description = film['description'].values[0]
     
        def show_description():
            st.markdown(f"**<BR><BR> <div align=center>Here's a description of a film from the list you just scraped - what's its name?**</font>", unsafe_allow_html=True)
            st.markdown(f"""> <font color="{streamlit_blue}" size="5">{st.session_state.film_description}</font>""", unsafe_allow_html=True)
            st.markdown(f""" <BR> """, unsafe_allow_html=True)
        
        def get_answer_form():
            with st.form('film_name_form', clear_on_submit=True):
                ans = st.text_input('Enter the name of the film. Punctuation and capitalization don\'t matter: (Ex: "The Godfather")', key='film_name_input').strip()
                if st.form_submit_button("Submit"):
                    st.session_state.film_guess = True          ## prevent answer dialogue until submitted
                    st.session_state.single_film_guesses += 1
                    st.session_state.total_session_guesses += 1
                    st.session_state.guessed_titles.append(ans)
                    if utl.clean_film_name(ans) == utl.clean_film_name(st.session_state.film_title):
                        st.write("""<div align=center><font size="5">✅ Correct!</font></div>""", unsafe_allow_html=True)
                        st.session_state.correct_guesses += 1
                    else:
                        st.write(f"""<div align=center><font size="5">"{ans}" is <font color={fft_knight_male[5]}>incorrect.</font></div>""", unsafe_allow_html=True)
                        
                return ans

        def show_answer_text(text: str=''):
            st.write(f"""<div align=center>{text}<font color="{streamlit_blue}" size="10">{st.session_state.film_title}</font></div>""", unsafe_allow_html=True)
            st.session_state.update(film_description=None, film_title=None, guessed_titles=[], single_film_guesses=0, film_guess=False, completed_game=True)
            play_again()

        def parse_answer(ans):
            if st.session_state.film_guess and st.session_state.completed_game == False:

                ## No more guesses
                if st.session_state.single_film_guesses == 3 and utl.clean_film_name(ans) != utl.clean_film_name(st.session_state.film_title):
                    answer_text = 'Strike number three... The film is: <BR>'
                    st.session_state.show_answer = True

                ## Correct guess
                elif utl.clean_film_name(ans) == utl.clean_film_name(st.session_state.film_title):
                    answer_text = ''
                    st.session_state.show_answer = True
                    
                ## Incorrect guess
                else:
                    col1, col2, col3 = st.columns([.7, .15, .15])
                    ## Incorrect Guessed Titles
                    with col1:
                        st.write(f"""Your guesses:""", unsafe_allow_html=True)
                        for idx, guess in enumerate(st.session_state.guessed_titles, 1):
                            st.write(f"""❌ {idx}. {guess}""", unsafe_allow_html=True)
                    ## Guesses Left
                    with col2:
                        guesses = "guesses" if 3 - st.session_state.single_film_guesses > 1 else "guess"
                        st.write(f"<div align=right>{3 - st.session_state.single_film_guesses} {guesses} left</div>", unsafe_allow_html=True)
                    ## Show Answer Button
                    with col3:
                        if st.button('Show Answer', on_click=lambda: st.session_state.update(show_answer=True)):
                            answer_text = 'The film is: <BR>'

            if st.session_state.show_answer:
                show_answer_text(answer_text)

        def play_again():
            st.markdown('<BR><BR>', unsafe_allow_html=True)
            if st.button('Play Again', key='play_again_button', use_container_width=True, on_click=lambda: st.session_state.update(film_guess=False, show_answer=False, film_description=None, film_title=None, guessed_titles=[], single_film_guesses=0, completed_game=False)):
                header()    ## restart game with new random selection

        def show_total_sesh_stats():
            if st.session_state.total_session_guesses > 0:
                st.write(f"""<div align=center>You've made {st.session_state.correct_guesses} correct guesses out of {st.session_state.total_session_guesses} total guesses this session.  That's a {st.session_state.correct_guesses/st.session_state.total_session_guesses:.0%} success rate!</div>""", unsafe_allow_html=True)



        st.markdown('<BR><BR>', unsafe_allow_html=True)
        st.markdown('***')
        st.markdown('<BR>', unsafe_allow_html=True)

        header()

        if st.session_state.all_films_used == False:  ## no game left if all films used
            if st.session_state.completed_game == True:
                play_again()
            else:    
                set_title_and_description()
                show_description()
                parse_answer(get_answer_form())

        show_total_sesh_stats()

    def create_dummy_frames(self, frame: pd.DataFrame):
        if st.session_state.dummy_genre is None:
            st.session_state.dummy_genre = utl.dummy_all_genres(frame)
        if st.session_state.dummy_star is None:
            st.session_state.dummy_star = utl.dummy_all_stars(frame)



if __name__ == '__main__':
    PageHome()