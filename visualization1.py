"""CSC111 Project 2: Identifying Quality Films Through Rotten Tomatoes' Metrics

Module Description
==================

This module contains the first visualization graph option.
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
from typing import List, Dict
import networkx as nx
from plotly.graph_objs import Scatter, Figure

from classes import WeightedGraph

LINE_COLOUR = 'rgb(100, 100, 100)'
VERTEX_BORDER_COLOUR = 'rgb(0, 0, 0)'
CHOSEN_MOVIE_COLOUR = 'rgb(255, 255, 255)'
REVIEW_COLOUR = 'rgb(105, 89, 205)'


def assign_vertex_colors(graph_nx: nx.Graph, num_movies: int) -> List[str]:
    """Generates a list of colors assigned to each vertex in a NetworkX graph based on vertex kind.

    This function creates a distinct color for each 'Movie' vertex using a rainbow color scheme,
    assigns a specific white color to 'Chosen Movie' vertices, and a default purple color to
    all other kinds of vertices, presumably 'Review' vertices.
    """
    # generate a list of rainbow colors, one for each movie
    # the color space is divided evenly among all movies
    rainbow_colours = [f'hsl({i * (360 / num_movies)}, 100%, 50%)' for i in range(num_movies)]

    # initialize an empty list for storing the color assigned to each vertex and a counter for the rainbow colors
    colours, rainbow_index = [], 0

    # iterate over each vertex in the graph, checking its 'kind' attribute to determine the appropriate color
    for kind in [graph_nx.nodes[k]['kind'] for k in graph_nx.nodes]:
        if kind == "Chosen Movie":

            # assign the predefined white color to 'Chosen Movie' vertices
            colours.append(CHOSEN_MOVIE_COLOUR)
        elif kind == "Movie":

            # assign the next color in the rainbow sequence to 'Movie' vertices
            colours.append(rainbow_colours[rainbow_index])

            # move to the next color in the sequence, looping back to the start if necessary
            rainbow_index = (rainbow_index + 1) % len(rainbow_colours)
        else:

            # assign the predefined purple color to vertices of any other kind, assumed to be 'Review' vertices
            colours.append(REVIEW_COLOUR)

    # return the list of assigned colors.
    return colours


def calculate_edge_positions(graph_nx: nx.Graph, pos: Dict) -> List[List[float]]:
    """Calculates the positions of edges in a graph for visualization.

    Given a graph and a mapping of node positions, this function computes the start
    and end positions of each edge in the graph. These positions are used for plotting
    lines between nodes in a visual representation of the graph.
    """
    # initialize a list to hold the x and y coordinates of the edges
    position_edges = [[], []]

    # iterate through each edge in the graph
    for edge in graph_nx.edges:

        # append the x-coordinates of the start and end points of the edge, followed by None
        position_edges[0] += [pos[edge[0]][0], pos[edge[1]][0], None]  # X-coordinates
        position_edges[1] += [pos[edge[0]][1], pos[edge[1]][1], None]  # Y-coordinates

    # return the list of x and y coordinates, ready for plotting
    return position_edges


def visualize_graph(graph: WeightedGraph, layout: str = 'spring_layout',
                    max_vertices: int = 5000, output_file: str = '') -> None:
    """Visualizes a graph using Plotly based on specified layout and color coding.

    This function converts a custom WeightedGraph object into a NetworkX graph,
    applies a layout algorithm to position the nodes, assigns colors based on node
    type, and plots the graph using Plotly with custom formatting for nodes and edges.
    """
    # convert the custom graph into a NetworkX graph, limiting the number of vertices
    graph_nx = graph.to_networkx(max_vertices)

    # apply the specified layout to determine the positions of nodes in the graph
    pos = getattr(nx, layout)(graph_nx)

    # extract node labels and count the number of movie nodes for color assignment
    labels = list(graph_nx.nodes)
    num_movies = [graph_nx.nodes[k]['kind'] for k in graph_nx.nodes].count("Movie")

    # assign colors to the nodes based on their type (movie, chosen movie, review)
    colours = assign_vertex_colors(graph_nx, num_movies)

    # calculate the positions of the edges for plotting
    position_edges = calculate_edge_positions(graph_nx, pos)

    # organize node positions into x and y coordinates for plotting
    position_values = [[pos[k][0] for k in graph_nx.nodes], [pos[k][1] for k in graph_nx.nodes]]

    # create Plotly traces for edges and nodes, configuring their appearance
    traces = [
        Scatter(
            x=position_edges[0],
            y=position_edges[1],
            mode='lines',
            name='edges',
            line={
                "color": LINE_COLOUR,
                "width": 1
            },
            hoverinfo='none'
        ),
        Scatter(
            x=position_values[0],
            y=position_values[1],
            mode='markers',
            name='nodes',
            marker={
                "symbol": 'circle-dot',
                "size": 10,
                "color": colours,
                "line": {
                    "color": VERTEX_BORDER_COLOUR,
                    "width": 0.5
                }
            },
            text=labels,
            hovertemplate='%{text}',
            hoverlabel={
                "namelength": 0
            }
        )
    ]

    # assemble the traces into a Plotly figure and configure the layout
    fig = Figure(data=traces)
    fig.update_layout({'showlegend': True})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)

    # display the figure interactively or save it as an image, based on 'output_file'
    if output_file == '':
        fig.show()
    else:
        fig.write_image(output_file)


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
