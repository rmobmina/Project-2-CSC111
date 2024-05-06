"""CSC111 Project 2: Identifying Quality Films Through Rotten Tomatoes' Metrics

Module Description
==================

This module contains the second visualization graph option.
All functions here are original and therefore have proper documentation.
Due to the complexity of the code in this file, no doctests are given.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of CSC111 students, teaching staff,
and the Department of Computer Science at the University of Toronto St. George campus.
All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) Akram Klai, Reena Obmina, Edison Yao, Derek Lam.
"""
from typing import Any
import pandas as pd
import plotly.graph_objects as go

from classes import WeightedGraph


def load_data_with_graph(graph: WeightedGraph) -> Any:
    """Extracts and computes necessary data from a WeightedGraph object for plotting movie recommendations.

    This function processes a graph of movies and their reviews to compute several metrics:
    average review scores, overall similarity scores with the preferred movie, and the number
    of reviews for each movie. It returns a pandas DataFrame containing these metrics along
    with the titles of the movies.
    """
    # get the preferred movie vertex and calculate scores for its neighbours
    chosen_movie = graph.get_vertex(graph.preferred_movie)
    review_scores = {v.item: v.average_score() for v in chosen_movie.neighbours}
    similarity_scores = {v.item: v.overall_similarity_score(chosen_movie) for v in chosen_movie.neighbours}

    # extract titles and prepare data series for plotting
    titles = [v.item for v in chosen_movie.neighbours]
    w1 = pd.Series(review_scores)  # Weighted average review score
    w2 = pd.Series(similarity_scores)  # Overall similarity score
    goodness_score = pd.Series({v.item: v.average_score() * v.overall_similarity_score(chosen_movie)
                                for v in chosen_movie.neighbours})

    # count of reviews for each movie
    num_reviews = pd.Series({v.item: len(v.neighbours) - 1 for v in chosen_movie.neighbours})

    # compile the data into a DataFrame for easy manipulation and visualization
    return pd.DataFrame({
        'title': titles,
        'w1': w1,
        'w2': w2,
        'Color Value': goodness_score,
        'num_reviews': num_reviews
    })


def plot_movie_recommendations(df: pd.DataFrame, review_threshold: int, output_file: str = '') -> None:
    """Creates a scatter plot of movie recommendations based on computed review and similarity scores.

    This function filters movies based on a minimum review threshold and plots them on a scatter plot
    according to their average review scores and overall similarity scores. The color of each point
    indicates the combination of these scores, providing an intuitive visual metric of recommendation
    quality. The plot can be either displayed interactively or saved to a file.
    """
    # apply review threshold filter to narrow down movies for visualization
    filtered_df = df[df['num_reviews'] >= review_threshold]

    # initialize Plotly figure
    fig = go.Figure()

    # scatter plot for visualizing movies
    fig.add_trace(go.Scatter(
        x=filtered_df['w1'],  # set x-axis data
        y=filtered_df['w2'],  # set y-axis data
        mode='markers',
        marker={
            'size': 10,
            'color': filtered_df['Color Value'],  # set marker color based on 'Color Value'
            'colorscale': 'Viridis',  # color scale for markers
            'line': {'width': 1, 'color': 'DarkSlateGrey'},
            'colorbar': {'title': 'Color Value'}
        },
        text=filtered_df['title'],  # hover text
        hoverinfo='text',
        hovertemplate="<b>%{text}</b><br>Average Review Score: %{x}<br>Overall Similarity Score: %{y}"
    ))

    # add lines indicating the mean values for review and similarity scores
    fig.add_shape(go.layout.Shape(
        type="line", x0=filtered_df['w1'].mean(), y0=filtered_df['w2'].min(),
        x1=filtered_df['w1'].mean(), y1=filtered_df['w2'].max(),
        line={'dash': "solid"}
    ))
    fig.add_shape(go.layout.Shape(
        type="line", x0=filtered_df['w1'].min(), y0=filtered_df['w2'].mean(),
        x1=filtered_df['w1'].max(), y1=filtered_df['w2'].mean(),
        line={'dash': "solid"}
    ))

    # update figure layout with titles and axis labels
    fig.update_layout(
        title="Movie Recommendations Based on Genre Similarity and Review Scores",
        xaxis_title="Average Review Score",
        yaxis_title="Overall Similarity Score",
        showlegend=False  # Hide legend
    )

    # caption to explain color scale
    caption = "Color Value: Yellow means high similarity and reviews, Purple means low similarity and reviews."
    fig.add_annotation(text=caption, xref="paper", yref="paper", x=0, y=-0.1, showarrow=False, align="left")

    # display or save the figure depending on 'output_file' parameter
    if output_file == '':
        fig.show()  # Display the plot
    else:
        fig.write_image(output_file)  # Save the plot to a file


if __name__ == "__main__":
    # requirement for "code quality"
    # "code-checking tools"
    import doctest

    doctest.testmod(verbose=True)

    # import python_ta.contracts
    # python_ta.contracts.check_all_contracts()

    import python_ta

    python_ta.check_all(config={
        'extra-imports': ["csv", "networkx", "typing", "io", "time", "tkinter",
                          "visualization1", "visualization2", "classes",
                          "plotly.graph_objs", "pandas", "plotly.graph_objects"],
        'allowed-io': ["get_favourite_movie", "get_favourite_genres", "load_weighted_review_graph",
                       "print_recommended_movies", "display_recommendations"],
        'max-line-length': 120
    })
