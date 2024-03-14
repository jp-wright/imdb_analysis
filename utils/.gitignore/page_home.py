import streamlit as st
# import altair as alt
import pandas as pd
# from pandas import DataFrame
from utils.streamlit_utilities import gradient, local_css, init_to_null
from utils.imdb_scraper import IMDB
from utils.palettes import *

# import utils.styler as sty
# import utils.plotter as plt
# from utils.utilities import adjust_for_inflation, get_unique_count_from_many_cols, clean_film_name
import utils.utilities as utl
# from itertools import chain
import re
from typing import Any



class PageHome():
    """Layout class for Home page.
    """
    def __init__(self):
        st.set_page_config(page_title="IMDb Lists", layout="wide", page_icon='🎥', initial_sidebar_state="expanded")
        # local_css("style/style.css")
        self.initialize_state()
        # st.sidebar.markdown(info['Photo'], unsafe_allow_html=True)
        self.page_header()
        # st.write('WFF https://www.imdb.com/list/ls528069836/')
        # st.write('big list https://www.imdb.com/list/ls040479474/?st_dt=&mode=detail&page=1&sort=list_order,asc')
        state = st.session_state
        if state.df is not None:
            self.df = state.df
        
        
        self.get_list_input()
        ## WORKS
        # with st.form('Or use a Demo List'):
        #     submit = st.form_submit_button('Or use a Demo List', on_click=lambda: state.update(film_frame=True))

        ## WORKS
        # st.button('Or use a Demo List', key='demo_list_button', on_click=lambda: state.update(film_frame=True))

        ## FAILS???
        # if st.button('Or use a Demo List', key='demo_list_button', on_click=lambda: self.demo_list):
        #     # self.demo_list()
        #     st.session_state.film_frame = True
            
        if state.film_frame:
            # self.demo_list()
            self.list_preview()
            state.list_processed = True

        if state.list_processed:
            self.name_that_film(self.df)



        # if st.session_state.df is not None:
        #     st.session_state.update(crosspage_df=st.session_state.df)


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
        # init_to_null(state, 'crosspage_df', None)
        init_to_null(state, 'dummy_genre', None)
        init_to_null(state, 'dummy_star', None)
        
    def page_header(self):
        gradient(grad_clr1=blue_bath1[1], grad_clr2=blue_bath1[3], title_clr=blue_bath1[5], subtitle_clr='#fcfbfb', title=f"🎬 IMDb Lists", subtitle="Here you can scrape any IMDb list and analyze it.", subtitle_size=27)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
    def get_list_input(self):
        '''provide list URL to scrape'''

        def get_list_id(url: str):
            '''get the IMDb list id from the URL to use when saving file'''
            pat = r"(list/(?P<list_id>.*))/"
            match = re.search(pat, url)
            if match:
                self.list_id = match.group("list_id")
                if not st.session_state.list_id: st.session_state.list_id = self.list_id
            else:
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
                # st.button('Or use a Demo List', key='demo_list', on_click=lambda: self.demo_list)
                if st.button('Or use a Demo List', key='demo_list_button'):
                    self.demo_list(big_list=True)
                    st.session_state.film_frame = True
                if st.session_state.df is not None:
                    self.save_list_to_csv(st.session_state.df)

    def scrape_list(self, url):
        '''load page based on user input'''
        self.imdb = IMDB(url)
        self.df = self.imdb.df
        if st.session_state.df is None: 
            st.session_state.df = self.df

    def demo_list(self, big_list: bool=False):
        st.write('Using a pre-saved list')
        if big_list:
            self.df = pd.read_csv('data/input/imdb_big_list.csv')
        else:
            self.df = pd.read_csv('data/input/imdb_demo_list.csv')
        if st.session_state.df is None: 
            st.session_state.df = self.df
        # st.write('self.df created')

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
            # file_name=f'{self.imdb}.csv',
            mime='text/csv',
        )
        
    def list_preview(self):
        """show a preview of the list you entered."""
        
        st.markdown('<BR>', unsafe_allow_html=True)
        st.write("Here's a preview of the list you entered!")
        st.dataframe(self.format_frame(self.df).set_index('title').sample(5))
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
            write_summary("Average Combined rating", f"{frame['combo_rk'].mean():.1f}")
            write_summary("Average Metacritic rating", f"{frame['metacritic_rk'].mean():.1f}")
            write_summary("Average IMDb voter rating", f"{frame['imdb_rk'].mean():.1f}")
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
                        st.write(f"""<BR><div align=center><font size="6">Game Over -- All films used!</font></div>""", unsafe_allow_html=True)
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



    def DEMO_cool_state_persistence_code(self):
        state = st.session_state

        if "dict_options" not in state:
            state.dict_options = {}

        if "submitted" not in state:
            state.submitted = False

        options = ["option1", "option2", "option3", "option4"]

        col1, col2, _ = st.columns(3)

        with col1.form("my_form"):
            new_country = st.text_input("New country")
            submit_button = st.form_submit_button(
                label="Add new country", on_click=lambda: state.update(submitted=True)
            )

        if state.submitted:
            state.dict_options[new_country] = col2.multiselect(
                f"Select the options you want for {new_country}",
                options,
                default=options[:2],
            )
            col2.write(state.dict_options)

            





    # def frmt_cols(self):
    #     frmts = {k: '{:.0f}' for k in self.int_cols}
    #     frmts.update({k: '{:.1f}' for k in self.float_cols})
    #     return frmts

    # def WoW_metrics(self):
    #     """
    #     """
    #     st.write("""<BR><h6 align=center>Week over Week Changes 📈</h6>""", unsafe_allow_html=True)

    #     def show_metric(frame, idx):
    #         if frame.iloc[idx]['WoW_Wins'] <= 1:
    #             clr = 'inverse'
    #         elif frame.iloc[idx]['WoW_Wins'] < 3:
    #             clr = 'off'
    #         else:
    #             clr = 'normal'

    #         st.metric(f":blue[{idx+1}. {frame.iloc[idx]['Player']}]", f"{int(frame.iloc[idx]['Total_Win'])} wins", f"{int(frame.iloc[idx]['WoW_Wins'])} last week", delta_color=clr)
            

    #     with st.container():
    #         col1, col2, col3, col4 = st.columns(4)
    #         with col1:
    #             show_metric(self.wow, 0)
    #         with col2:
    #             show_metric(self.wow, 1)
    #         with col3:
    #             show_metric(self.wow, 2)
    #         with col4:
    #             show_metric(self.wow, 3)
    #         with col1:
    #             show_metric(self.wow, 4)
    #         with col2:
    #             show_metric(self.wow, 5)
    #         with col3:
    #             show_metric(self.wow, 6)
    #         with col4:
    #             show_metric(self.wow, 7)

    # def manager_ranking(self):
    #     """
    #     """
    #     frame = self.dfy_
    #     st.write("""<BR><h6 align=center>Manager Ranking #️⃣1️⃣</h6>""", unsafe_allow_html=True)
    #     bold = 'Total Win' if 'Total Win' in frame.columns else 'Win'
        
    #     with st.container():
    #         _, col2, _ = st.columns([.05, .9, .05])
    #         with col2:
    #             st.dataframe(sty.style_frame(frame, bg_clr_dct, frmt_dct=self.frmt_cols(), bold_cols=[bold]), use_container_width=True, hide_index=True)
                
    #         ## using st.table() honors intracellular formatting...  I actually like this more, but it's hard to center (yes..) and isn't sortable AND can't get rid of the damned index yet
    #         # with col2:
    #         #     frame = sty.style_frame(frame.set_index('Rank').drop('Total Win%' if frame['Total Win%'].sum() == 0 else '', errors='ignore', axis=1), self.bg_clr_dct, frmt_dct={'Win%': '{:.1f}', 'Full_Ssn_Pace': '{:.1f}', col: '{:.1f}'}, bold_cols=['Win'])
    #         #     st.table(frame)

    # def manager_by_round(self):
    #     """
    #     """
    #     st.write("""<BR><h6 align=center>Manager by Round (wins) </h6>""", unsafe_allow_html=True)
    #     with st.container():
    #         _, col2, _ = st.columns([.05, .9, .05])
    #         with col2:
    #             st.dataframe(sty.style_frame(self.dfpt, self.bg_clr_dct), hide_index=True, use_container_width=True)

    # def playoff_teams(self):
    #     """
    #     """
    #     if not self.dfpo.empty:
    #         st.write("""<BR><h6 align=center>Playoff Teams Tracker</h6>""", unsafe_allow_html=True)
    #         st.dataframe(sty.style_frame(self.dfpo, self.bg_clr_dct, frmt_dct={'Playoff_Win': '{:.0f}', 'Playoff_Loss': '{:.0f}'}), width=765, height=620)

    # def draft_overview_chart(self):
    #     """
    #     """
    #     st.write(f"""<BR><h4 align=center>The {self.curr_year} Draft</h4>""", unsafe_allow_html=True)
    #     st.write("""<p align=center>TIP: Click any player's dot to see only their picks. Shift-Click dots to add more players; double-click to reset.</p>""", unsafe_allow_html=True)
    #     # self.df['Total_Win'] = np.random.randint(1,18, size=self.df.shape[0])  ## testing for chart
    #     plt.plot_draft_overview_altair(self.df, year_range=[self.curr_year])

    # def best_worst_picks(self):
    #     """
    #     """
    #     st.write('  #')
    #     with st.container():
    #         left_col, right_col = st.columns([1, 1])
    #         with left_col:
    #             st.write("""<h6 align=center>✅ Best picks by round:</h6>""", unsafe_allow_html=True)
            
    #         with right_col:
    #             st.write("""<h6 align=center>❌ Worst picks by round:</h6>""", unsafe_allow_html=True)

    #     for rd in range(1, 5):
    #         with st.container():
    #             left_col, right_col = st.columns([1, 1])
    #             with left_col:
    #                 # st.write("""**Best picks by round:**""")
    #                 self.picks_by_round(self.dfd, 'Best', rd)
                
    #             with right_col:
    #                 # st.write("""**Worst picks by round:**""")
    #                 self.picks_by_round(self.dfd, 'Worst', rd)

    # def wins_by_round(self):
    #     st.write(""" # """)
    #     st.write(f"""<BR><h5 align=center>Best Draft Rounds</h5>""", unsafe_allow_html=True)
    #     st.write("""<div align=center>Did we use our early draft picks wisely (does Round 1 have a higher win% than Round 2, etc.)?</div>""", unsafe_allow_html=True)
        
    #     drop_cols = ['Rank', 'Year'] if self.dfr_['Playoff Teams'].sum() > 0 else ['Rank', 'Year', 'Playoff Teams']
    #     frame = self.dfr_.drop(drop_cols, axis=1)[['Round', 'Win%', 'Win', 'Loss', 'Tie', 'Games']]
    #     with st.container():
    #         col1, col2 = st.columns([.45, 1])
    #         with col2:
    #             st.dataframe(sty.style_frame(frame, self.bg_clr_dct, frmt_dct={'Win%': '{:.1f}'}, bold_cols=['Win%']))
            
    # def top_10_reg_ssn(self):
    #     st.write(f"""
    #         Let's take a look at the top 10 Regular Season finishes.
    #         """)
    #     st.dataframe(sty.style_frame(self.hist_frames[0].sort_values(['Win%_Rk', 'Win', 'Year'], ascending=[True, False, True]), self.bg_clr_dct, frmt_dct={'Win%': '{:.1f}'}, bold_cols=['Win%']), width=620, height=550)
        
    # def top_10_playoffs(self):
    #     # st.write(body_dct['pohist_txt'])
    #     st.write(f"""
    #     How about the top 10 Playoff runs?
    #     """)

    #     st.dataframe(sty.style_frame(self.hist_frames[1].sort_values(['Win_Rk', 'Win%', 'Year'], ascending=[True, False, True]), self.bg_clr_dct, frmt_dct={'Win%': '{:.1f}'}, bold_cols=['Win']), width=620, height=550)
        
    # def top_10_total_wins(self):
    #     # st.write(body_dct['tothist_txt'])
    #     st.write(f"""And what about the top 10 regular season and playoffs combined (for a single season) -- i.e. a player's total wins? 
    #         """)
        
    #     st.dataframe(sty.style_frame(self.hist_frames[2].sort_values(['Win%_Rk', 'Win%', 'Year'], ascending=[True, False, True]), self.bg_clr_dct, frmt_dct={'Win%': '{:.1f}'}, bold_cols=['Win']), width=620, height=550)        
            
    # def champions(self):
    #     st.write("""#### Champions""")
    #     st.write("""Past champions and their results, as well as projected champion for the current year (highlighted in blue).
    #         """)
    #     st.write("""I'm not sure how to parse the added week 18 in the regular season except to use win percent as opposed to wins.  
    #     """)
        
    #     st.dataframe(sty.style_frame(self.champs, self.bg_clr_dct, frmt_dct={'Total_Win%': '{:.1f}'}, clr_yr=self.curr_year, bold_cols=['Total_Win']))  
        
    # def careers(self):
    #     st.write("""#""")
    #     st.write("""#### Career Performance""")
    #     st.write("Who in our pool has been the best over their careers (sorted by Wins)?")
        
    #     st.dataframe(sty.style_frame(self.dfc_, self.bg_clr_dct, frmt_dct={'Total Win%': '{:.1f}'}))
        
    #     st.write("""...Victoria hasn't even won as many games as the Leftovers.  Sad! 😜""")
        
    #     st.write("""#""")
    #     # dfs_ = player_hist.sort_values('Year', ascending=True).groupby(['Player', 'Year']).sum().groupby('Player').cumsum().reset_index().sort_values(['Player', 'Year'])
    #     # dfs_
    #     if 'Champ' in self.player_hist.columns:
    #         player_hist = self.player_hist 
    #     else:
    #         player_hist = self.player_hist.merge(self.champs.assign(Champ=True)[['Player', 'Year', 'Champ']], on=['Player', 'Year'], how='left').fillna(False)
    #     # player_hist = player_hist.merge(champs.assign(Champ='Yes')[['Player', 'Year', 'Champ']], on=['Player', 'Year'], how='left').fillna('No')
    #     # player_hist.loc[(player_hist['Year']==curr_year) & (player_hist['Champ']=='Yes'), 'Champ'] = 'Proj'
    #     # player_hist.tail(20)
        
        
    #     ## tried to use this for color=champ_condition .. can't get to work
    #     # champ_condition = {
    #     #     'condition': [
    #     #         {alt.datum.Champ: 'Yes', 'value': 'firebrick'},
    #     #         {alt.datum.Champ: 'Proj', 'value': 'Navy'}],
    #     #      'value': 'orange'}
            
            
        
    #     bars = alt.Chart()\
    #                 .mark_bar()\
    #                 .encode(
    #                     alt.X('Player:N', axis=alt.Axis(title='')),
    #                     alt.Y('Total_Win:Q', scale=alt.Scale(domain=[0, 50], zero=True)),
    #                     # color=alt.Color('Player:N', scale=alt.Scale(domain=dfs_['Player'].unique(),       range=list(self.plot_bg_clr_dct.values()))),
    #                     # color=champ_condition
    #                     color=alt.condition(
    #                         alt.datum.Champ == True, 
    #                         alt.value('firebrick'), 
    #                         # alt.value(list(self.plot_bg_clr_dct.values())),
    #                         alt.value(self.plot_bg_clr_dct['Mike']),
    #                         ),
    #                     )
                        

    #     text = bars.mark_text(align='center', baseline='bottom')\
    #                 .encode(text='Total_Win:Q')
                    
    #     ## Can't use "+" layer operator with faceted plots
    #     chart = alt.layer(bars, text, data=player_hist).facet(column=alt.Column('Year:O', header=alt.Header(title='')), title=alt.TitleParams(text='Wins by Year', anchor='middle'))#.resolve_scale(color='independent')

    #     st.altair_chart(chart)
    
    # def sweet_ridge_plot(self):
    #     # source = data.seattle_weather.url
    #     source = self.dfy
    #     step = 30
    #     overlap = 1
    #     # st.write(source.head(100))
    
    #     ridge = alt.Chart(source, height=step).transform_joinaggregate(
    #         mean_wins='mean(Total_Win)', groupby=['Player']
    #     ).transform_bin(
    #         ['bin_max', 'bin_min'], 'Total_Win'
    #     ).transform_aggregate(
    #         value='count()', groupby=['Player', 'mean_wins', 'bin_min', 'bin_max']
    #     ).transform_impute(
    #         impute='value', groupby=['Player', 'mean_wins'], key='bin_min', value=0
    #     ).mark_area(
    #         interpolate='monotone',
    #         fillOpacity=0.8,
    #         stroke='lightgray',
    #         strokeWidth=0.5
    #     ).encode(
    #         alt.X('bin_min:Q', bin='binned', title='Total Wins'),
    #         alt.Y(
    #             'value:Q',
    #             scale=alt.Scale(range=[step, -step * overlap]),
    #             axis=None
    #         ),
    #         alt.Fill(
    #             'mean_wins:Q',
    #             legend=None,
    #             scale=alt.Scale(domain=[source['Total_Win'].max(), source['Total_Win'].min()], scheme='redyellowblue')
    #         )
    #     ).facet(
    #         row=alt.Row(
    #             'Player:N',
    #             title=None,
    #             header=alt.Header(labelAngle=0, labelAlign='left')
    #         )
    #     ).properties(
    #         title='Win History by Player',
    #         bounds='flush'
    #     ).configure_facet(
    #         spacing=0
    #     ).configure_view(
    #         stroke=None
    #     ).configure_title(
    #         anchor='end'
    #     )
    #     st.altair_chart(ridge)
    
    # def personal_records(self):
    #     st.write("""#""")
    #     st.write("""#### Personal Records""")    
    #     # st.write(body_dct['pr_txt'])
    #     st.write("""Last, here are the personal records for each player, sorted by most at top.  \nBlue highlight is for this season and shows who might have a chance at setting a new personal record for total wins.""")
        
        
    #     # print(self.player_hist)

    #     left_column, right_column = st.columns([2, 1])
        
    #     # # st.write(self.player_hist)
    #     # with left_column:
    #     #     for name in self.dfy_['Player'].unique():
    #     #         self.show_player_hist_table(name)
    #     #         st.write("\n\n\n _")

    #     # with right_column: 
    #     #     for name in self.dfy_['Player'].unique():
    #     #         self.plot_wins_by_year(self.player_hist[self.player_hist['Player'] == name])


    #     for name in self.dfy_['Player'].unique():
    #         with left_column:
    #             self.show_player_hist_table(name)
    #         with right_column: 
    #             self.plot_wins_by_year(self.player_hist[self.player_hist['Player'] == name])
    #             st.write("\n\n\n _")


    # def picks_by_round(self, frame: DataFrame, best_worst: str, rd: int): 
    #     """
    #     """
    #     # idx_max = frame.groupby('Round')['Total_Win'].transform('max') == frame['Total_Win']
    #     # idx_min = frame.groupby('Round')['Total_Win'].transform('min') == frame['Total_Win']
        
        
        
    #     # components.html(f'<div style="text-align: center"> Round {rd} </div>')
    #     st.write(f""" <div align=center>Round {rd}</div>""", unsafe_allow_html=True)
    #     # idx = idx_max if best_worst.lower() == 'best' else idx_min
    #     max_min = 'max' if best_worst.lower() == 'best' else 'min'
    #     idx = frame.groupby('Round')['Total_Win'].transform(max_min) == frame['Total_Win']
        
    #     st.dataframe(sty.style_frame(frame[(idx) & (frame['Round']==rd)], bg_clr_dct, frmt_dct={'Total_Win': '{:.0f}'}), width=495)
    #     # st.dataframe(sty.style_frame(frame[idx].query("""Round==@rd"""), bg_clr_dct, frmt_dct={'Total_Win': '{:.0f}'}), width=495)
    
    #     # for rd_res in [(rd, best_worst) for rd in range(1,5)]:
    #     #     rd, res = rd_res[0], rd_res[1]
    #     #     # components.html(f'<div style="text-align: center"> Round {rd} </div>')
    #     #     st.write(f""" Round {rd}""")
    #     #     idx = idx_max if res == 'Best' else idx_min
    #     #     st.dataframe(sty.style_frame(frame[idx].query("""Round==@rd"""), bg_clr_dct, frmt_dct={'Total_Win': '{:.0f}'}), width=495)





    # def project_info(self):
    #     st.markdown('<BR>', unsafe_allow_html=True)
    #     # st.header(":blue[Project Information]")
    #     # st.header('💻  :blue[Platforms Used]')
    #     st.header('💻  Platforms Used')

    #     with st.container():
    #         # st.subheader('💻  Platforms Used')
    #         col1, col2, col3 = st.columns([1, 1, 1])
    #         with col1:
    #             show_logo('python', width=120, height=70)
    #         with col2:
    #             show_logo('pandas', width=120, height=70)
    #         with col3:
    #             show_logo('r_data', width=120, height=80)
    #         with col1:
    #             show_logo('bash', width=120, height=55)
    #         with col2:
    #             show_logo('numpy', width=120, height=80)
    #         with col3:
    #             show_logo('elastic_search', width=120, height=60)
    #         with col1:
    #             show_logo('rest_api', width=120, height=60)
            


    #     with st.container():
    #         st.markdown('<BR>', unsafe_allow_html=True)
    #         # st.header('⚒️ :blue[Skills]')
    #         st.header('⚒️ Skills')

    #         md_domain = f"""
    #         ##### <font color={subheading_blue}>Domain Research</font>
    #         A multitude of economic and demographic terms were learned in order to explain to users some of the more complex signals that were developed.  Understanding how this data was tracked and released was also necessary to accurately devise information-rich signals which would offer significant value to clients.
    #         """

    #         md_gather = f"""
    #         ##### <font color={subheading_blue}>Data Gathering</font>
    #         A dizzying array of geo-based data sources were used and their cadence of ingestion depended on how often they were released, as some were weekly, others monthly, and still others quarterly.  This was not in the scope of Jonpaul's role.
    #         """

    #         md_storage = f"""
    #         ##### <font color={subheading_blue}>Data Storage</font>
    #         Data was stored in ElasticSearch.  This was not in the scope of Jonpaul's role.
    #         """

    #         md_clean = f"""
    #         ##### <font color={subheading_blue}>Data Cleaning & Preparation</font>
    #         Most input data was from published sources and tended to be relatively clean. Jonpaul ported data cleaning and processing scripts from R to Python as the Signals Repository was a Python-based pipeline.
    #         """

    #         md_eng = f"""
    #         ##### <font color={subheading_blue}>Feature Engineering</font>
    #         Jonpaul authored scripts which consisted of basic (raw) data and more complex, customized signals.  Key signals were engineered by allowing a user to define a specific area (down to the block of a street) for which they wanted to see any number of changes in interactions over time.  Multiple raw signals were used to compmrise information-rich and model-ready signals that clients used in their own data science pipelines.  
    #         """

    #         md_model = f"""
    #         ##### <font color={subheading_blue}>Model Building</font>
    #         This is a signals repository and did not contain models.
    #         """

    #         md_res = f"""
    #         ##### <font color={subheading_blue}>Threshold Selection and Result Visualization</font>
    #         Demo visualizations displayed the concepts of key signals but the goal of this repository was to provide clients with data to enhance their own modeling endeavors.
    #         """



    #         st.markdown(md_domain, unsafe_allow_html=True)
    #         st.markdown(md_gather, unsafe_allow_html=True)
    #         st.markdown(md_storage, unsafe_allow_html=True)
    #         st.markdown(md_clean, unsafe_allow_html=True)
    #         st.markdown(md_eng, unsafe_allow_html=True)
    #         st.markdown(md_model, unsafe_allow_html=True)
    #         st.markdown(md_res, unsafe_allow_html=True)


    # def conclusion(self):
    #     st.markdown('<BR>', unsafe_allow_html=True)
    #     with st.container():
    #         st.header('✅ Conclusion')

    #         md_conc = """
    #         The Signals Repository was (is) highly successful and has clients across Europe in addition to America, now.  At bi-annual events hosted by KPMG, clients have given presentations on the ways in which the Signals Repository has bolstered their own modeling efforts.  Overall, the platform matured to the point of being a notable revenue generator for KPMG due to the real and accessible value it added to clients' data science workflows.
    #         """
    #         st.markdown(md_conc)


    # def gallery(self):
    #     st.markdown("<BR>", unsafe_allow_html=True)
    #     with st.container():
    #         st.header('🖼 Gallery')

    #         col1, col2 = st.columns([1, 1])
    #         with col1:
    #             show_img(signals['us_geo_growth'], width=450, height=450, hover='', caption='Example of the type of geo-based activity that signals offered.')
    #         with col2:
    #             show_img(signals['kpmg_signals'], width=450, height=450, hover='', caption='')


if __name__ == '__main__':
    pass