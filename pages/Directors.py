import streamlit as st
st.write("Under construction...")


def tmp():
    pass
    def plot_gross_by_director_decade_plotly(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header(f"Highest Grossing Directors by Decade")

        thresh, y = plot_xy_radio_buttons(x_label='Top N Directors Per Decade', x_buttons=['5', '10', '25', 'All'], xindex=0, xhelp='Show top N directors for each decade by avg. gross per film', y_label='Select Box Office Revenue', y_buttons=['gross', 'gross_adj_2023'], xkey='x_gross_by_director_decade_radio', ykey='y_gross_by_director_decade_radio', y_format=lambda label: 'raw gross' if label == 'gross' else 'inflation adj.', col_spacing=[.5, .25, .25], horizontal=True)


        @st.cache_data
        def transform_frame(y: str, thresh: int):
            avg_gross_per_decade = df.groupby('decade')[y].mean().reset_index()

            avg_gross_dir_per_decade = df.groupby(['decade', 'director'])[y].agg(['mean', 'size'])\
                                            .rename(columns={'mean': 'avg_gross', 'size': 'count'})
            
            top10grossing_dir_per_decade = avg_gross_dir_per_decade\
                                            .groupby(['decade'])['avg_gross']\
                                            .nlargest(thresh)\
                                            .droplevel(0, axis=0)
            
            top10grossing_dir_per_decade = avg_gross_dir_per_decade\
                                            .reindex(top10grossing_dir_per_decade.index)\
                                            .reset_index()
            return top10grossing_dir_per_decade, avg_gross_per_decade

        top10, avg_gross = transform_frame(y, int(thresh) if thresh != 'All' else 10000)

        fig = go.Figure()
        
        # Add scatter trace for top directors
        for idx, decade in enumerate(top10['decade'].unique()):
            data = top10[top10['decade'] == decade]
            fig.add_trace(go.Scatter(
                x=data['decade'],
                y=data['avg_gross'],
                mode='markers',
                marker=dict(color=px.colors.qualitative.Pastel[idx], size=13, line=dict(color='black', width=.75)),
                name=f'{decade}',
                showlegend=True,
                # showlegend=True if decade == 2010 else False,
                # showlegend=False,
                hovertemplate='<b>Director</b>: ' + data['director'] + '<br><b>Avg. Gross</b>: ' + data['avg_gross'].div(1000000).map("${:,.1f} M".format) + '<br><b>Films</b>: ' + data['count'].astype(str) + '<extra></extra>',
            ))

        # Add scatter trace for average film gross by decade per list of directors
        fig.add_trace(go.Scatter(
            x=avg_gross['decade'],
            y=avg_gross[y],
            mode='markers',
            marker=dict(color='red', size=8, line=dict(color='white', width=1)),
            name='Avg. Decade Gross',
            hovertemplate='Decade avg: ' + avg_gross[y].div(1000000).map("${:,.1f} M".format) + '<extra></extra>',
        ))

        fig.update_layout(xaxis_title='Decade',
                            yaxis_title=y,
                            width=1000,)
        st.plotly_chart(fig)



    def table_top_directors_by_gross_per_film(self, df: pd.DataFrame=pd.DataFrame()):
        self.element_header("Top Directors by Gross per Film")
        
        @st.cache_data
        def transform_frame(df: pd.DataFrame):
            director_stats = df.groupby('director')['gross'].agg(['mean', 'count']).sort_values(by='mean', ascending=False).head(2)
            director_stats['mean'] = director_stats['mean'].div(1000000).map("${:,.1f} M".format)
            director_stats = director_stats.rename(columns={'mean': 'Average Gross per Film', 'count': 'Film Count'})
            return director_stats
        
        director_stats = transform_frame(df)
        st.dataframe(director_stats, use_container_width=False)

    def table_directors_with_multiple_films(self, df: pd.DataFrame=pd.DataFrame()):
        # Create a new dataframe for directors with more than one film count
        directors_with_multiple_films = df.groupby('director').filter(lambda x: len(x) > 1)
        director_stats_multiple_films = directors_with_multiple_films.groupby('director')['gross'].agg(['mean', 'count']).sort_values(by='mean', ascending=False)
        director_stats_multiple_films['mean'] = director_stats_multiple_films['mean'].div(1000000).map("${:,.1f} M".format)
        director_stats_multiple_films = director_stats_multiple_films.rename(columns={'mean': 'Average Gross per Film', 'count': 'Film Count'})

        st.dataframe(director_stats_multiple_films, use_container_width=False)

if __name__ == '__main__':
    pass