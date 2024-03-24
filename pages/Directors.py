import streamlit as st
import pandas as pd
from plotly import graph_objects as go
import plotly.express as px
from utils.streamlit_utilities import gradient, local_css, init_to_null, plot_xy_radio_buttons, set_frame
from utils.palettes import blue_bath1, fft_knight_male, streamlit_blue, vermeer_pearl

## top rated dirs
        ## DONE table
        ## plot rating over time (by Nth film or by year or by year-of-career)
## top grossing dirs
        ## table
        ## gross over time (by Nth film or by year or by year-of-career)
## gross by rating
        ## table
        ## are higher rated directors grossing more? (Maybe do it for top 5 films per director?)
        ## regression plot of gross by rating
## director by genre
    ## which dirs are best at which genres?
    ## which dirs love which genres?
    ## which genres do they gross most/least (vs. expecation from regression)
## Create selectable plot for show the films which grossed more than expectation for their rating.  Show expectation line and show the residuals, basically.

class PageBoxOffice():
    """Layout class for Directors page.
    """
    
    def __init__(self):
        st.set_page_config(page_title="IMDb Lists", layout="wide", page_icon='🎥', initial_sidebar_state="expanded")
        # local_css("style/style.css")
        self.initialize_state()
        # st.cache_data.clear() ## change to use button to clear cache....?  Punt for now.
        self.df = set_frame(load_demo=True)
        self.page_header()
        self.show_page()


    def show_page(self):

        # if self.df['gross'].sum() == 0:
        #     st.markdown(f"#### <font color={fft_knight_male[5]}>WARNING:</font> No film 'gross' data available.", unsafe_allow_html=True)  
        #     st.markdown("Please check out other pages that aren't dealing with gross revenue.")
        #     return
        
        # self.intro_text()
        st.markdown('***')
        # self.data_insights_text()
        st.markdown('***')
        self.table_most_freq_directors(self.df)
        st.markdown('***')
        self.table_top_rated_directors(self.df)
        self.plot_dir_rating_over_time(self.df)
        st.markdown('***')
        self.plot_dir_rating_by_film(self.df)
        st.markdown('***')
        self.plot_dir_rating_after_n_films(self.df)
        # self.table_dir_rating_after_n_films(self.df)
        



    def initialize_state(self):
        state = st.session_state
        init_to_null(state, 'show_more_info', False)
        init_to_null(state, 'df', None)
        init_to_null(state, 'df_cache', None)

    def element_header(self, text: str, header_tag: str='h4', color: str=blue_bath1[1]):
        return st.markdown(f"<{header_tag} align=center><font color={color}>{text}</font></{header_tag}>", unsafe_allow_html=True)

    def page_header(self):
        gradient(grad_clr1=blue_bath1[1], grad_clr2=blue_bath1[3], title_clr=blue_bath1[5], subtitle_clr='#fcfbfb', title=f"🎬 Directors", subtitle="Examine the directors in your list", subtitle_size=27)
        st.markdown("<br><br>", unsafe_allow_html=True)

    def intro_text(self):
        self.element_header("Introduction")
        st.markdown("""""") 

        if not st.session_state.show_more_info:
            st.button('Show More', key='show_more_button', on_click=lambda: st.session_state.update(show_more_info=True))
        
        def show_more_info():
            # st.markdown(f"<h5><font color={blue_bath1[1]}>Home Video and Streaming</font></h5>", unsafe_allow_html=True)
            self.element_header("")
            st.markdown("""""")
            
            st.markdown("""""")
            
            st.markdown("""""")

            # st.markdown(f"<h5><font color={blue_bath1[1]}>Theaters and Technology</font></h5>", unsafe_allow_html=True)
            self.element_header("T")
            st.markdown("""""")

        if st.session_state.show_more_info:
            show_more_info()
            st.button('Show Less', key='show_less_button', on_click=lambda : st.session_state.update(show_more_info=False))

        st.markdown("""Okay, let's get started!""")  
        
        # st.write('<BR><BR>', unsafe_allow_html=True)

    def data_insights_text(self):
        self.element_header("Insights From Your List")
        st.markdown("""Here are some insights from your list of films.  This is a great place to start to understand the data you have.  You can see different trends and facts about directors from your list of films.""")

        st.markdown(f"""<font color={blue_bath1[1]}>Tables are sortable and charts are interactive.  Hover over the charts to see more information.  Click and drag to zoom in on the charts.  Click on the legend to hide or show data.</font>""", unsafe_allow_html=True)

    def table_most_freq_directors(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Most Frequent Directors")
        
        @st.cache_data
        def transform_frame(df: pd.DataFrame):
            return df['director'].value_counts()\
                                .head(15)\
                                .to_frame()\
                                .rename(columns={'count': 'Number of Films'})\
                                .assign(rank=lambda f: f['Number of Films'].rank(ascending=False, method='dense').astype(int))\
                                .reset_index()\
                                .set_index('rank')
        
        top_dirs = transform_frame(df)

        col1, col2, col3 = st.columns([.33, .33, .34])
        with col1:
            st.dataframe(top_dirs.iloc[:5].style.format({'Number of Films': "{:,.0f}"}), use_container_width=False)
        with col2:
            st.dataframe(top_dirs.iloc[5:10].style.format({'Number of Films': "{:,.0f}"}), use_container_width=False)
        with col3:
            st.dataframe(top_dirs.iloc[10:].style.format({'Number of Films': "{:,.0f}"}), use_container_width=False)

        st.markdown("")

    def table_top_rated_directors(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Top Rated Directors")

        c1, _, c3 = st.columns([.35, .4, .25])
        with c1:
            x = st.radio('Select Rating System', ('metacritic_score', 'imdb_score', 'combo_score'), index=1,key='x_top_rated_dir_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)
        with c3:
            n = int(st.slider('Min. Number of Films', 1, 10, 2, 1, key='n_top_rated_dir_radio'))

        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, n: int):
            return df[df[x] > 0].groupby('director')[x].mean().round(1)\
                                .sort_values(ascending=False)\
                                .to_frame()\
                                .reset_index()\
                                .rename(columns={x: f'avg. score'})\
                                .assign(films=lambda df_: df_['director'].map(df['director'].value_counts()))\
                                .query("films > @n")\
                                .assign(rank=lambda df_: df_[f'avg. score'].rank(ascending=False, method='dense').astype(int))\
                                .set_index('rank')\
                                .head(15)
        
        frame = transform_frame(df, x, n)

        col1, col2, col3 = st.columns([.33, .33, .34])
        with col1:
            st.dataframe(frame.iloc[:5].style.format({'avg. score': "{:.1f}"}), use_container_width=False)
        with col2:
            if frame.shape[0] > 5:
                st.dataframe(frame.iloc[5:10].style.format({'avg. score': "{:.1f}"}), use_container_width=False)
        with col3:
            if frame.shape[0] > 10:
                st.dataframe(frame.iloc[10:].style.format({'avg. score': "{:.1f}"}), use_container_width=False)

        st.markdown("")

    def plot_dir_rating_over_time(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Director Rating Over Time")

        ## Sort this so the default multiselect is the top 3 directors by rating
        @st.cache_data
        def sort_frame(df: pd.DataFrame):
            return df.sort_values('metacritic_score', ascending=False)
        df = sort_frame(df)

        c1, c2, c3 = st.columns([.25, .5, .25])
        with c1:
            x = st.radio('Select Timeframe', ['year', 'decade'], index=1, key='x_dir_rating_over_time_radio', horizontal=True)
        with c2:
            chosen_dir = st.multiselect(
                            'Select Director(s)',
                            df['director'].unique().tolist(),
                            df['director'].unique().tolist()[:3],
                            key='dir_rating_over_time_multiselect')
        with c3:
            y = st.radio('Select Rating System', ['metacritic_score', 'imdb_score', 'combo_score'], index=1, key='y_dir_rating_over_time_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)


        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, y: str):
            frame = df[(df[y] > 0) & (df['year'] > 0)].groupby([x, 'director'])[y].agg(['mean', 'count'])\
                                                        .rename(columns={'mean': y, 'count': 'films'})\
                                                        .round(1)\
                                                        .reset_index()
            if x == 'year':
                frame = frame.merge(df[['year', 'director', 'title']], left_on=['year', 'director'], right_on=['year', 'director'], how='left')
            return frame
        
        df_plot = transform_frame(df, x, y)

        dir_mask = (df_plot['director'].isin(chosen_dir))
        size = 11 if x == 'year' else 9

        def hover(x, y, data_clr: pd.DataFrame):
            if x == 'year':
                hov = '<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Rating</b>: ' + data_clr[y].map('{:.1f}'.format).astype(str) + '<extra></extra>'
            else:
                hov = '<b>Dir</b>: ' + data_clr['director'] + ' (' + data_clr['decade'].astype(str) +'s) ' + '<br><b>Films</b>: ' + data_clr['films'].astype(str) + '<br><b>Avg. Rating</b>: ' + data_clr[y].map('{:.1f}'.format).astype(str) + '<extra></extra>'
            return hov

        
        colors = int(df_plot.shape[0] / 8) * px.colors.qualitative.Pastel

        def plot_unchosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for director in df_plot['director'].unique():
                data_grey = df_plot[(df_plot['director'] == director) & ~dir_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey[x],
                    y=data_grey[y],
                    mode='markers',
                    name=f"{director}s" if x == 'decade' else f"{director}",
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, director in enumerate(df_plot.loc[dir_mask, 'director'].unique()):
                data_clr = df_plot[(df_plot['director'] == director) & dir_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr[x],
                    y=data_clr[y],
                    mode='markers+lines',
                    name=f"{director}s" if x == 'decade' else f"{director}",
                    marker=dict(color=colors[idx], size=12 if len(chosen_dir) < 8 else 11, opacity=1 if len(chosen_dir) < 8 else .8, line=dict(color='black', width=1)),
                    hovertemplate=hover(x, y, data_clr),
                    showlegend=True,
                ))

        fig = go.Figure()
        plot_unchosen_dir(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_dir(fig, df_plot)

        fig.update_layout(width=1000,
                          height=500,
                          yaxis_title=y,
                        # title={'font_color': blue_bath1[1], 'font_size': 23, # 'font_family': "Times New Roman", 'text': "Gross over Time", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'}
                        )
                            
        st.plotly_chart(fig)
        # self.table_top_decades_by_gross_per_film(self.df, y=y)

    def plot_dir_rating_by_film(self, df: pd.DataFrame=pd.DataFrame()):
        """ """
        
        self.element_header("How Are Directors Rated Per Film?")
        
        ## Sort this so the default multiselect is the top 3 directors by rating
        @st.cache_data
        def sort_frame(df: pd.DataFrame):
            return df.sort_values('combo_score', ascending=False)
        df = sort_frame(df)


        c1, c2, c3 = st.columns([.25, .5, .25])
        with c1:
            n = int(st.slider('Select Number of Films', 1, 20, 1, 1, help='Rating by director after N films', key='per_film_rating_slider'))
        with c2:
            chosen_dir = st.multiselect(
                            'Select Director(s)',
                            df['director'].unique().tolist(),
                            df['director'].unique().tolist()[:3],
                            key='dir_per_film_rating_multiselect')
        with c3:
            y = st.radio('Select Rating System', ['metacritic_score', 'imdb_score', 'combo_score'], index=1, key='y_dir_per_film_rating_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)


        @st.cache_data
        def transform_frame(df: pd.DataFrame, y: str):
            return df[(df[y] > 0) & (df['year'] > 0)].sort_values('year')\
                                                    .assign(nth_film=lambda f: f.groupby('director')['year']\
                                                            .transform(lambda f: f.rank(method='first')))\
                                                    .sort_values('nth_film')
        
        df_plot = transform_frame(df, y)
        dir_mask = (df_plot['director'].isin(chosen_dir))

        def hover(y, data_clr: pd.DataFrame):
            if len(chosen_dir) <= 1:
                hov = '<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Rating</b>: ' + data_clr[y].map('{:.1f}'.format).astype(str) + '<br><b>Film No.</b>: ' + data_clr['nth_film'].astype(int).astype(str) + '<extra></extra>'
            else:
                hov = '<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Dir</b>: ' + data_clr['director']+ '<br><b>Rating</b>: ' + data_clr[y].map('{:.1f}'.format).astype(str) + '<br><b>Film No.</b>: ' + data_clr['nth_film'].astype(int).astype(str) + '<extra></extra>'
            return hov


        colors = int(df_plot.shape[0] / 8) * px.colors.qualitative.Pastel
        # st.write(colors[:17])

        def plot_unchosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for director in df_plot['director'].unique():
                data_grey = df_plot[(df_plot['director'] == director) & ~dir_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey.loc[data_grey['nth_film'] <= n, 'nth_film'],
                    y=data_grey[y],
                    mode='markers',
                    name='none',
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, director in enumerate(df_plot.loc[dir_mask, 'director'].unique()):
                data_clr = df_plot[(df_plot['director'] == director) & dir_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr.loc[data_clr['nth_film'] <= n, 'nth_film'],
                    y=data_clr[y],
                    mode='markers+lines',
                    name=director,
                    marker=dict(color=colors[idx], size=12 if len(chosen_dir) < 8 else 11, opacity=1 if len(chosen_dir) < 8 else .8, line=dict(color='black', width=1)),
                    hovertemplate=hover(y, data_clr),
                    showlegend=True,
                ))
                idx += 1

        fig = go.Figure()
        plot_unchosen_dir(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_dir(fig, df_plot)

        fig.update_layout(width=1000,
                          height=500,
                          yaxis_title=y,
                        # title={'font_color': blue_bath1[1], 'font_size': 23, # 'font_family': "Times New Roman", 'text': "Gross over Time", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'}
                        )
                            
        st.plotly_chart(fig)





    def plot_dir_rating_after_n_films(self, df: pd.DataFrame=pd.DataFrame()):
        """Average scores for the top and bottom grossing films."""
        
        self.element_header("How Are Directors Rated After N Films?")
        st.markdown("<div align=center>This chart shows the career rating of a director after N films, giving insight into how a director's rating changes over time</div><BR><BR>", unsafe_allow_html=True)
        
        ## Sort this so the default multiselect is the top 3 directors by rating
        @st.cache_data
        def sort_frame(df: pd.DataFrame):
            return df.sort_values('combo_score', ascending=False)
        df = sort_frame(df)


        c1, c2, c3 = st.columns([.25, .5, .25])
        with c1:
            n = int(st.slider('Select Number of Films', 1, df.groupby('director').size().max(), 3, 1, help='Rating by director after N films', key='n_films_rating_slider'))
        with c2:
            chosen_dir = st.multiselect(
                            'Select Director(s)',
                            df['director'].unique().tolist(),
                            df['director'].unique().tolist()[:3],
                            key='dir_n_films_rating_multiselect')
        with c3:
            y = st.radio('Select Rating System', ['metacritic_score', 'imdb_score', 'combo_score'], index=1, key='y_dir_n_films_rating_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)


        @st.cache_data
        def transform_frame(df: pd.DataFrame, y: str):
            return df[(df[y] > 0) & (df['year'] > 0)].sort_values('year')\
                                                    .assign(nth_film=lambda f: f.groupby('director')['year']\
                                                            .transform(lambda s: s.rank(method='first')))\
                                                    .sort_values(['nth_film', 'director'])\
                                                    .assign(career_rating=lambda f: f.groupby('director')[y].transform(lambda s: s.expanding().mean().round(1)))
        
        df_plot = transform_frame(df, y)
        dir_mask = (df_plot['director'].isin(chosen_dir))

        def hover(y, data_clr: pd.DataFrame):
            if len(chosen_dir) <= 1:
                hov = '<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Career Rating</b>: ' + data_clr['career_rating'].map('{:.1f}'.format).astype(str) + '<br><b>Film No.</b>: ' + data_clr['nth_film'].astype(int).astype(str) + '<extra></extra>'
            else:
                hov = '<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Dir</b>: ' + data_clr['director']+ '<br><b>Career Rating</b>: ' + data_clr['career_rating'].map('{:.1f}'.format).astype(str) + '<br><b>Film No.</b>: ' + data_clr['nth_film'].astype(int).astype(str) + '<extra></extra>'
            return hov


        colors = int(df_plot.shape[0] / 8) * px.colors.qualitative.Pastel

        # st.write(df_plot.head(30))

        def plot_unchosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for director in df_plot['director'].unique():
                data_grey = df_plot[(df_plot['director'] == director) & ~dir_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey.loc[data_grey['nth_film'] <= n, 'nth_film'],
                    y=data_grey['career_rating'],
                    mode='markers',
                    name='none',
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, director in enumerate(df_plot.loc[dir_mask, 'director'].unique()):
                data_clr = df_plot[(df_plot['director'] == director) & dir_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr.loc[data_clr['nth_film'] <= n, 'nth_film'],
                    y=data_clr['career_rating'],
                    mode='markers+lines',
                    name=director,
                    marker=dict(color=colors[idx], size=12 if len(chosen_dir) < 8 else 11, opacity=1 if len(chosen_dir) < 8 else .8, line=dict(color='black', width=1)),
                    hovertemplate=hover(y, data_clr),
                    showlegend=True,
                ))
                idx += 1

        fig = go.Figure()
        plot_unchosen_dir(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_dir(fig, df_plot)

        fig.update_layout(width=1000,
                          height=500,
                          yaxis_title=y,
                        # title={'font_color': blue_bath1[1], 'font_size': 23, # 'font_family': "Times New Roman", 'text': "Gross over Time", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'}
                        )
                            
        st.plotly_chart(fig)
        self.table_dir_rating_after_n_films(df_plot, y, n)



    def table_dir_rating_after_n_films(self, df: pd.DataFrame=pd.DataFrame(), y: str='imdb_score', n: int=5):
        """ 
        """

        @st.cache_data
        def transform_frame(df: pd.DataFrame, y: str, n: int):
            ## .query("nth_film == @n") or .query("nth_film <= @n").... 
            return df[df[y] > 0].sort_values('nth_film', ascending=True)\
                                .query("nth_film == @n")\
                                .groupby('director')[['nth_film', 'career_rating']].last()\
                                .sort_values(['career_rating', 'director'], ascending=[False, True])\
                                .assign(rank=lambda f: f['career_rating'].rank(ascending=False, method='dense').astype(int))\
                                .rename(columns={'career_rating': 'Career Rating'})

        frame = transform_frame(df, y, n)[['rank', 'Career Rating']]

        # st.write(df.tail(20))
        # st.write(frame.head(10))
        rating = y.replace('_score', '').title() if y != 'imdb_score' else 'IMDb'
        st.markdown(f"""<div align=center><font size=5>Career <font color={vermeer_pearl[1]}>{rating}</font> Rating After <font color={vermeer_pearl[1]}>{n}</font> Films</font></div><BR>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([.34, .33, .33])
        with col1:
            st.dataframe(frame.iloc[:5].style.format({'Career Rating': "{:.1f}", 'nth_film': '{:.0f}'}), use_container_width=False)
        with col2:
            if frame.shape[0] > 5:
                st.dataframe(frame.iloc[5:10].style.format({'Career Rating': "{:.1f}", 'nth_film': '{:.0f}'}), use_container_width=False)
        with col3:
            if frame.shape[0] > 10:
                st.dataframe(frame.iloc[10:15].style.format({'Career Rating': "{:.1f}", 'nth_film': '{:.0f}'}), use_container_width=False)

        st.markdown("")








    def table_top_grossing_directors(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Top Rated Directors")

        c1, _, c3 = st.columns([.35, .4, .25])
        with c1:
            x = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='x_dir_gross_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)
        with c3:
            n = int(st.slider('Min. Number of Films', 1, 10, 2, 1, key='n_dir_gross_radio'))

        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, n: int):
            return df[df[x] > 0].groupby('director')[x].mean().round(1)\
                                .sort_values(ascending=False)\
                                .to_frame()\
                                .reset_index()\
                                .rename(columns={x: f'avg. gross'})\
                                .assign(films=lambda df_: df_['director'].map(df['director'].value_counts()))\
                                .query("films > @n")\
                                .assign(rank=lambda df_: df_[f'avg. gross'].rank(ascending=False, method='dense').astype(int))\
                                .set_index('rank')\
                                .head(15)
        
        frame = transform_frame(df, x, n)

        col1, col2, col3 = st.columns([.33, .33, .34])
        with col1:
            st.dataframe(frame.iloc[:5].style.format({'avg. gross': "{:.1f}"}), use_container_width=False)
        with col2:
            if frame.shape[0] > 5:
                st.dataframe(frame.iloc[5:10].style.format({'avg. gross': "{:.1f}"}), use_container_width=False)
        with col3:
            if frame.shape[0] > 10:
                st.dataframe(frame.iloc[10:].style.format({'avg. gross': "{:.1f}"}), use_container_width=False)

        st.markdown("")

    def plot_dir_gross_over_time(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Director Rating Over Time")

        c1, c2, c3 = st.columns([.25, .5, .25])
        with c1:
            x = st.radio('Select Timeframe', ['year', 'decade'], index=1, key='x_dir_rating_over_time_radio', horizontal=True)
        with c2:
            chosen_dir = st.multiselect(
                            'Select Director(s)',
                            df['director'].unique().tolist(),
                            df['director'].unique().tolist()[:2],
                            key='dir_rating_over_time_multiselect')
        with c3:
            y = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='y_dir_gross_over_time_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)


        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, y: str):
            frame = df[(df[y] > 0) & (df['year'] > 0)].groupby([x, 'director'])[y].agg(['mean', 'count'])\
                                                        .rename(columns={'mean': y, 'count': 'films'})\
                                                        .round(1)\
                                                        .reset_index()
            if x == 'year':
                frame = frame.merge(df[['year', 'director', 'title']], left_on=['year', 'director'], right_on=['year', 'director'], how='left')
            return frame
        
        df_plot = transform_frame(df, x, y)

        # dir_mask = (df_plot['director'] == chosen_dir) if chosen_dir != 'All' else (df_plot['director'] == df_plot['director'])
        dir_mask = (df_plot['director'].isin(chosen_dir))
        size = 11 if x == 'year' else 9

        def hover(x, y, data_clr: pd.DataFrame):
            if x == 'year':
                hov = '<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Rating</b>: ' + data_clr[y].map('{:.1f}'.format).astype(str) + '<extra></extra>'
            else:
                hov = '<b>Dir</b>: ' + data_clr['director'] + ' (' + data_clr['decade'].astype(str) +'s) ' + '<br><b>Films</b>: ' + data_clr['films'].astype(str) + '<br><b>Avg. Rating</b>: ' + data_clr[y].map('{:.1f}'.format).astype(str) + '<extra></extra>'
            return hov

        
        colors = int(df_plot.shape[0] / 8) * px.colors.qualitative.Pastel

        def plot_unchosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for director in df_plot['director'].unique():
                data_grey = df_plot[(df_plot['director'] == director) & ~dir_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey[x],
                    y=data_grey[y],
                    mode='markers',
                    name=f"{director}s" if x == 'decade' else f"{director}",
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_dir(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, director in enumerate(df_plot['director'].unique()):
                data_clr = df_plot[(df_plot['director'] == director) & dir_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr[x],
                    y=data_clr[y],
                    mode='markers+lines',
                    name=f"{director}s" if x == 'decade' else f"{director}",
                    marker=dict(color=colors[idx], size=12 if len(chosen_dir) < 8 else 11, opacity=1 if len(chosen_dir) < 8 else .8, line=dict(color='black', width=1)),
                    hovertemplate=hover(x, y, data_clr),
                    # hovertemplate='<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Rating</b>: ' + data_clr[x].map('{:.1f}'.format).astype(str) + '<extra></extra>',
                    showlegend=True,
                ))

        fig = go.Figure()
        plot_unchosen_dir(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_dir(fig, df_plot)

        fig.update_layout(width=1000,
                          height=500,
                          yaxis_title=y,
                        # title={'font_color': blue_bath1[1], 'font_size': 23, # 'font_family': "Times New Roman", 'text': "Gross over Time", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'}
                        )
                            
        st.plotly_chart(fig)
        # self.table_top_decades_by_gross_per_film(self.df, y=y)







    def table_top_gross_dir_by_rating(self, df: pd.DataFrame=pd.DataFrame()):
        """Average scores for the top and bottom grossing films."""
        
        self.element_header("Are Top Grossing Directors Better Rated?")
        
        _, col2, _, col4 = st.columns([.15, .3, .1, .45])
        with col2:
            n = int(st.slider('Select Number of Films', 10, 100, 10, 10, help='Shows the N top films and N bottom films average gross and scores.', key='top_bottom_slider'))
        with col4:
            gross = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], index=0, key='y_top_bottom_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)

        @st.cache_data
        def transform_frame(df: pd.DataFrame, n: int, gross: str):
            df = df[df['metacritic_score']>0].sort_values(gross, ascending=False) # Remove films with no metacritic score
            top_films = df.head(n)
            bottom_films = df.tail(n)

            top_metacritic_avg = top_films['metacritic_score'].mean()
            top_imdb_avg = top_films['imdb_score'].mean()
            top_imdb_votes_avg = top_films['imdb_votes'].mean()
            bottom_metacritic_avg = bottom_films['metacritic_score'].mean()
            bottom_imdb_avg = bottom_films['imdb_score'].mean()
            bottom_imdb_votes_avg = bottom_films['imdb_votes'].mean()
            top_gross_avg = top_films[gross].mean()
            bottom_gross_avg = bottom_films[gross].mean()

            avg_scores_df = pd.DataFrame({
                'Avg. Gross': [top_gross_avg, bottom_gross_avg],
                'Avg. Metacritic Score': [top_metacritic_avg, bottom_metacritic_avg],
                'Avg. IMDb Score': [top_imdb_avg, bottom_imdb_avg],
                'Avg. IMDb Votes': [top_imdb_votes_avg, bottom_imdb_votes_avg]}, 
                index=[f'Top Grossing {n} Films', f'Bottom Grossing {n} Films'])
            
            # Add a row for the difference between the first two rows
            diff_row = avg_scores_df.iloc[0] - avg_scores_df.iloc[1]
            avg_scores_df.loc[avg_scores_df.shape[0]] = diff_row
            avg_scores_df = avg_scores_df.rename(index={avg_scores_df.shape[0]-1: 'Difference'})
            return avg_scores_df
        
        avg_scores_df = transform_frame(df, n, gross).style.format({
                    'Avg. Gross': "${:,.0f}",
                    'Avg. Metacritic Score': "{:.1f}",
                    'Avg. IMDb Score': "{:.1f}",
                    'Avg. IMDb Votes': "{:,.0f}"
                })
        
        _, col2 = st.columns([.15, .85])
        with col2:
            st.dataframe(avg_scores_df, use_container_width=False)

    def remarks_top_and_bottom_grossing_films(self):
        """Remarks about the top and bottom grossing films."""

        st.markdown("<BR>", unsafe_allow_html=True)
        st.markdown("""Depending on your dataset, there may be some interesting insights to be had from the top- and bottom-grossing films.  For large enough lists of movies that have a wide spread between the top and bottom N grossing films, it's possible to see that the *very* bottom-grossing movies (bottom 10 or 30) are significantly lower rated than the equivalent top-grossing films.  But once there is a larger sample (~70+), it's possible to see that the bottom-grossing films are not significantly lower rated than the top-grossing films.  This is because the bottom-grossing films are likely to be more obscure and less well-known, and therefore less likely to be rated.  As such, the number of ratings for each film, and not just the average rating, can be informative.""")
        st.markdown("<BR><BR>", unsafe_allow_html=True)

    def plot_gross_by_rating_plotly(self, df: pd.DataFrame=pd.DataFrame()):
        # self.element_header(f"Gross by Rating Score")

        c1, c2, _, c4 = st.columns([.35, .25, .15, .25])
        with c1:
            x = st.radio('Select Rating System', ('metacritic_score', 'imdb_score', 'combo_score'), index=1,key='x_gross_by_rating_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)
        with c2:
            chosen_genre = st.selectbox('Select Genre', ['All'] + list(df['genre1'].unique()))
            st.markdown(f"<div align=center>{df[df['genre1']==chosen_genre].shape[0]} {chosen_genre} films</div>" if chosen_genre != 'All' else '', unsafe_allow_html=True)
        with c4:
            y = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='y_gross_by_rating_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)

        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str):
            return df[df[x]>0].assign(score_decile=pd.cut(df[x], 10, labels=False, duplicates='drop')).sort_values(x, ascending=False)

        df_plot = transform_frame(df, x)
        genre_mask = (df_plot['genre1'] == chosen_genre) if chosen_genre != 'All' else (df_plot['genre1'] == df_plot['genre1'])
        colors = 5 * px.colors.qualitative.Pastel

        def plot_unchosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for decile in df_plot['score_decile'].unique():
                data_grey = df_plot[(df_plot['score_decile'] == decile) & ~genre_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey[x],
                    y=data_grey[y],
                    mode='markers',
                    name=f"{decile}0th pct.",
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, decile in enumerate(df_plot['score_decile'].unique()):
                data_clr = df_plot[(df_plot['score_decile'] == decile) & genre_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr[x],
                    y=data_clr[y],
                    mode='markers',
                    name=f"{decile}0th pct.",
                    marker=dict(color=colors[idx], size=12 if chosen_genre != 'All' else 11, opacity=1 if chosen_genre != 'All' else .8, line=dict(color='black', width=1)),
                    hovertemplate='<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Gross</b>: ' + data_clr[y].div(1000000).map("${:,.1f} M".format) + '<br><b>Rating</b>: ' + data_clr[x].map('{:.1f}'.format).astype(str) + '<extra></extra>',
                    showlegend=True,
                ))

        fig = go.Figure()
        plot_unchosen_genre(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_genre(fig, df_plot)

        # fig.update_xaxes(tick0=0, dtick=10)
        fig.update_layout(
            xaxis_title=x,
            yaxis_title='Gross',
            # xaxes=dict(tick0=0, dtick=10),
            width=1000,
            height=500
        )

        st.plotly_chart(fig)

        st.markdown("""Also, note that if a film has a Metacritic score of 0, it means that it has not been rated on Metacritic.  This is not the same as a film having a Metacritic score of 0.  The same goes for IMDb scores. As such, those films have been removed from the plot to avoid skewing the visualization.""")

    def plot_gross_over_time_plotly(self, df: pd.DataFrame=pd.DataFrame()):
        """Plot the gross over Time."""

        self.element_header(f"Film Gross over Time")
        
        c1, c2, _, c4 = st.columns([.35, .25, .15, .25])
        with c1:
            x = st.radio('Select Timeframe', ['year', 'decade'], index=1, key='x_gross_by_year_radio', format_func=lambda label: label.replace('_score', ''), horizontal=True)
        with c2:
            chosen_genre = st.selectbox('Select Genre', ['All'] + list(df['genre1'].unique()), key='genre_over_time_radio')
            st.markdown(f"<div align=center>{df[df['genre1']==chosen_genre].shape[0]} {chosen_genre} films</div>" if chosen_genre != 'All' else '', unsafe_allow_html=True)
        with c4:
            y = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='y_gross_by_year_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)


        @st.cache_data  # Cache the function so it doesn't run every time the user changes the radio buttons
        def transform_frame(df):
            return df[df['decade']>0].sort_values('decade', ascending=False)
        df_plot = transform_frame(df)
        genre_mask = (df_plot['genre1'] == chosen_genre) if chosen_genre != 'All' else (df_plot['genre1'] == df_plot['genre1'])
        size = 11 if x == 'year' else 9

        ## TODO: There are some movies that have 'decade' == 0.  Need to manually add their correct data in 'specific_fixes' in the imdb_acquisition.py file.  Until then, must drop them here.

        colors = 5 * px.colors.qualitative.Pastel

        def plot_unchosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for decade in df_plot['decade'].unique():
                data_grey = df_plot[(df_plot['decade'] == decade) & ~genre_mask]
                
                fig.add_trace(go.Scatter(
                    x=data_grey[x],
                    y=data_grey[y],
                    mode='markers',
                    name=f"{decade}0s.",
                    marker=dict(color='grey', size=9, opacity=.4, line=dict(color='black', width=1)),
                    hoverinfo='skip',
                    showlegend=False,
                ))

        def plot_chosen_genre(fig: go.Figure, df_plot: pd.DataFrame):
            for idx, decade in enumerate(df_plot['decade'].unique()):
                data_clr = df_plot[(df_plot['decade'] == decade) & genre_mask]

                fig.add_trace(go.Scatter(
                    x=data_clr[x],
                    y=data_clr[y],
                    mode='markers',
                    name=f"{decade}s",
                    marker=dict(color=colors[idx], size=12 if chosen_genre != 'All' else 11, opacity=1 if chosen_genre != 'All' else .8, line=dict(color='black', width=1)),
                    hovertemplate='<b>Title</b>: ' + data_clr['title'] + ' (' + data_clr['year'].astype(str) +') ' + '<br><b>Gross</b>: ' + data_clr[y].div(1000000).map("${:,.1f} M".format) + '<br><b>Rating</b>: ' + data_clr[x].map('{:.1f}'.format).astype(str) + '<extra></extra>',
                    showlegend=True,
                ))

        fig = go.Figure()
        plot_unchosen_genre(fig, df_plot) ## add grey first so that the colored points are on top
        plot_chosen_genre(fig, df_plot)

        fig.update_layout(width=1000,
                          height=500
                        # title={'font_color': blue_bath1[1], 'font_size': 23, # 'font_family': "Times New Roman", 'text': "Gross over Time", 'y':0.9, 'x':0.5, 'xanchor': 'center', 'yanchor': 'top'}
                        )
                            
        st.plotly_chart(fig)
        # self.table_top_decades_by_gross_per_film(self.df, y=y)

    def remarks_gross_over_time(self):
        st.markdown("""The top grossing films by decade can be intereseting!  Depending on your dataset, there might be very distinct trends which differ from others.  One thing to keep in mind is the increase in both number of theaters and average ticket price as time goes on.  This means that the top grossing films of the 2010s might not be as impressive as the top grossing films of the 1970s, for example.  This is why we adjust for inflation.  It's also why we look at the average gross per film, and not just the total gross of the top films.  The average gross per film can give us a better idea of how profitale films were in a given decade.  Last, most people won't have many films from the 1930s, 1940s, or 1950s, so the data might not be as reliable for those decades.  In theory, it would be great to have at least, say, the top 50 films from each decade to make a comparison.""")

    def table_grid_top_genres_over_time(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Highest Grossing Genres Over Time")
        
        genre, gross = plot_xy_radio_buttons(x_label='Select Genre', x_buttons=('genre1', 'genre2'), x_format=lambda label: 'Primary' if label == 'genre1' else 'Secondary', xkey='x_top_gross_genre_radio', y_label='Select Box Office Revenue', y_buttons=['gross', 'gross_adj_2023'], ykey='y_top_gross_genre_radio', y_format=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', col_spacing=[.5, .25, .25], horizontal=True)

        @st.cache_data
        def transform_frame(df: pd.DataFrame, decade: int):
            tmp = df.groupby(['decade', genre])[gross].agg(['mean', 'count'])\
                    .sort_values(by=['decade', 'mean'], ascending=False)\
                    .groupby('decade').head()\
                    .assign(**{f"{decade}s": lambda f: f.groupby('decade')['mean'].rank(ascending=False, method='dense')})\
                    .assign(mean=lambda f: f['mean'].div(1000000).map("${:,.1f} M".format))\
                    .reset_index(level=1).loc[decade]\
            ## if there's only one genre per decade after grouping, even if there are multiple films in that decade 
            ## but all are the same genre (admittedly unlikely with > 10 films per decade, but still has to be accounted for)
            ## then pandas will return a series after we index via .loc[decade], not a dataframe, so we have to convert 
            ## it to a dataframe.  Ugly, but it works. (I'm sure there's a smoother way to do this.)
            if isinstance(tmp, pd.Series):
                tmp = tmp.to_frame().T
            return tmp.reset_index()\
                .rename(columns={'mean': 'Avg. Gross', 'count': 'Film Count', 'genre1': 'Primary', 'genre2': 'Secondary', 'index': 'decade'})\
                .set_index(f"{decade}s")
                
        frames = [transform_frame(df, decade).drop('decade', axis=1) for decade in sorted(df['decade'].unique())]

        # Print the tables in a grid, 3 per row, one table per decadde
        for idx in range(len(frames)):
            if idx % 3 == 0:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.dataframe(frames[idx], use_container_width=False)
                with col2:
                    if idx+1 < len(frames):
                        st.dataframe(frames[idx+1], use_container_width=False)
                with col3:
                    if idx+2 < len(frames):
                        st.dataframe(frames[idx+2], use_container_width=False)

    def remarks_top_genres_over_time(self):
        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown("""The top grossing genres can be revealing.  Depending on your dataset, there might be very distinct trends which differ from others.  Adjusting for inflation is likely a good choice for evaluating the top grossing genres.  Acknowledging that different genres (Drama, Action, Adenture...) tend to have many more films than others (Western, War, Musical...) is important and should be noted with your specific dataset. Assuming substantial samples of each decade and genre, it's most interesting to remark on the genres that are consistently top grossing across time (Action, Adventure, Animation), and, conversely, those that seem to have distinct eras (Film-Noir, Western, War, Sci-Fi...)""")
        st.markdown('<BR>', unsafe_allow_html=True)

    def plot_gross_by_genre_plotly(self, df: pd.DataFrame=pd.DataFrame(), x: str='genre1', y: str='gross'):
        """Plot the gross by genre."""

        self.element_header(f"Gross by Genre")
        def xlabel(label):
            if label == 'genre1': lab = 'primary genre'
            elif label == 'genre2': lab = 'secondary genre'
            elif label == 'genre3': lab = 'third genre'
            return lab

        x, y = plot_xy_radio_buttons(x_label='Select Genre', y_label='Select Box Office Revenue', x_buttons=['genre1', 'genre2', 'genre3'], y_buttons=['gross', 'gross_adj_2023'], xkey='x_gross_by_genre_radio', ykey='y_gross_by_genre_radio', x_format=xlabel, y_format=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', col_spacing=[.45, .3, .25], horizontal=True)
        
        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, y: str, power: float=0.8, lower: int=12, upper: int=80):
            ## create a 'count_plot' column for the size of the bubble and bound it to a minimum of 12 and a maximum of 80
            avg_gross_by_genre = df.groupby(x)[y].agg(['mean', 'count'])\
                .reset_index()\
                .rename(columns={'mean': 'avg_gross'})\
                .assign(count_plot=lambda f: f['count'].pow(power).clip(upper=upper).clip(lower=lower)) 
            return avg_gross_by_genre.sort_values(x, ascending=True)
        
        df_plot = transform_frame(df, x, y, power=1 if x == 'genre3' else 0.8)
        colors = 3 * px.colors.qualitative.Pastel ## extend the color palette if there are more genres than default palette   

        fig = go.Figure()
        for idx, genre in enumerate(df_plot[x].unique()):
            data = df_plot[df_plot[x]==genre]
            
            fig.add_trace(go.Scatter(
                x=data[x], 
                y=data['avg_gross'], 
                mode='markers', 
                marker=dict(line=dict(color='black', width=0.5), color=colors[idx], size=data['count_plot']),
                hovertemplate='<b>Genre</b>: ' + data[x] + '<br><b>Gross</b>: ' + data['avg_gross'].div(1000000).map("${:,.1f} M".format)  + '<br><b>Count</b>: ' + data['count'].astype(str) + '<extra></extra>',
                showlegend=False)
                )
        
        fig.update_layout(width=1000)
        st.plotly_chart(fig)

    def remarks_gross_by_genre(self):
        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown("""This interactive chart is meant to give some idea of the relative categorical sizes of the genres in your list through bubble size, and, further helps show how adjusting for inflation can alter the average gross by genre.  This change can be quite substantial and shows how genre popularity has changed over time.""")



    def plot_gross_by_director_plotly(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header(f"Gross by Director")

        def set_default_indices(df: pd.DataFrame):
            '''Set the default indices for the radio buttons b/c in small frames most options will display an empty chart.'''
            if df.shape[0] > 100:
                thresh_idx = 3 ## $100M
            elif df.shape[0] > 50:
                thresh_idx = 1 ## $20M
            else:
                thresh_idx = 0

            minfilms_idx = 1 if df.shape[0] > 50 else 0
            return thresh_idx, minfilms_idx

        thresh_idx, minfilms_idx = set_default_indices(df)

        def xlabel(label):
            if label == 'All':
                return 'All Directors'
            elif int(label) < 1000000000:
                lab = int(label) // 1000000
                denom = 'M'
            else:
                lab = int(label) // 1000000000
                denom = 'B'
            return f"${lab:,d} {denom}"
        
        col1, _, col2, col3 = st.columns([.35, .07, .33, .25])
        with col1:
            thresh = st.radio('Avg. Gross Threshold', ['All', '20000000', '50000000', '100000000', '300000000', '500000000', '1000000000'], index=thresh_idx, help='Minimum avg. gross per film by director', key='x_gross_by_director_radio', format_func=xlabel, horizontal=True)
        with col2:
            minfilms = st.radio("Min. Number of Films", [1, 2, 3], index=minfilms_idx, help='Minimum number of films by director. Helps weed out one-hit wonders', key='min_films_by_director_radio', horizontal=True)
        with col3:
            y = st.radio('Select Box Office Revenue', ['gross', 'gross_adj_2023'], key='y_gross_by_director_radio', format_func=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', horizontal=True)
        
        @st.cache_data
        def transform_frame(df: pd.DataFrame, x: str, y: str, thresh: int, power: float=0.8, lower: int=12, upper: int=80):
            ## create a 'count_plot' column for the size of the bubble and bound it to a minimum of 12 and a maximum of 80
            avg_gross_by_director = df.groupby(x)[y].agg(['mean', 'count'])\
                .reset_index()\
                .rename(columns={'mean': 'avg_gross'})\
                .query(f"avg_gross >= @thresh")\
                .assign(count_plot=lambda f: f['count'].pow(power).clip(upper=upper).clip(lower=lower)) 
            return avg_gross_by_director.sort_values('avg_gross', ascending=True)

        df_plot = transform_frame(df, 'director', y, int(thresh) if thresh != 'All' else 0)
        colors = 50 * px.colors.qualitative.Pastel ## extend the color palette

        fig = go.Figure()
        for idx, genre in enumerate(df_plot['director'].unique()):
            data = df_plot[(df_plot['director']==genre) & (df_plot['count'] >= int(minfilms))]
            # data = df_plot[df_plot['director']==genre]
            
            fig.add_trace(go.Scatter(
                x=data['director'], 
                y=data['avg_gross'], 
                mode='markers', 
                marker=dict(line=dict(color='black', width=0.5), color=colors[idx], size=data['count_plot']),
                hovertemplate='<b>Genre</b>: ' + data['director'] + '<br><b>Gross</b>: ' + data['avg_gross'].div(1000000).map("${:,.1f} M".format)  + '<br><b>Films</b>: ' + data['count'].astype(str) + '<extra></extra>',
                showlegend=False)
                )

        fig.update_layout(width=1000)
        st.plotly_chart(fig)

    def remarks_gross_by_director(self):
        st.markdown('<BR>', unsafe_allow_html=True)
        st.markdown("""The key takeaway from this chart (depending on your dataset) is that the number of directors with *ONE* big hit are more numerous than you might expect, but to have multiple is really challenging.  Setting the limit of number of films to 2 or 3 can help weed out the one-hit wonders.  Some, like Peter Jackson or (slightly less so) George Lucas, had one franchise they rode to massive success. Others, like Christopher Nolan or Steven Spielberg, have had multiple films that have been very successful.  Again, adjusting for inflation probably offers the fairest comparison.  Though not implemented here, it might also be worth adding a feature that allows the user to compare only the top N grossing films of a director's catalog, as opposed to all of them.""")
        st.markdown('<BR>', unsafe_allow_html=True)




if __name__ == "__main__":
    PageBoxOffice()

    