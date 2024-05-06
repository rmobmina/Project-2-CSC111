"""CSC111 Project 2: Identifying Quality Films Through Rotten Tomatoes' Metrics

Module Description
==================

This module contains the main methods needed for our project.
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
from __future__ import annotations

import csv
import io
import tkinter as tk
from tkinter import simpledialog

from classes import WeightedGraph
import visualization1
import visualization2


def build_with_new_vertex_fraction(graph: list[WeightedGraph], test: list[str],
                                   dict_list: list[dict[str, str]], movie: str, fav_genres: list[str]) -> None:
    """Integrates review scores and genre similarities into the movie review graph.

    This function adds review vertices and edges between movies and reviews based on the score and genre similarity.

    The weight of edges reflects the similarity in genre preferences, and only reviews
    that match certain criteria are incorporated into the graph.

    Preconditions:
        - len(test) in {1, 2} and elements convertible to float
        - dict_list where dict_list[0]: {movie_id: set[genres]}, dict_list[1]: {movie_id: movie_title}
        - movie must be a key in dict_list[1]
    """
    # process the review score(s) and calculate the genre weight based on user's favorite genres and movie's genres
    if len(test) == 2 and dict_list[1].get(movie) and movie in dict_list[0]:
        try:

            # calculate the genre weight as the ratio of the intersection to the union of favorite and movie genres
            weight = (len(set(fav_genres).intersection(dict_list[0][movie]))
                      / len(set(fav_genres).union(dict_list[0][movie])))

            # calculate the review score as the ratio of the first score to the second, capped at 1.0
            score = min(list(map(float, test))[0] / list(map(float, test))[1], 1.0)

            # add vertices for the review and movie (if not already present) and connect them with the calculated weight
            graph[0].add_vertex(score, "Review")
            graph[0].add_vertex(dict_list[1].get(movie), "Movie")
            graph[0].add_edge(dict_list[1].get(movie), score, weight)
        except (ValueError, ZeroDivisionError):

            # ignore errors such as division by zero or conversion issues, proceeding without adding these reviews
            pass
    elif len(test) == 1 and dict_list[1].get(movie):
        try:

            # for a single score, calculate the weight similarly but without dividing scores
            weight = (len(set(fav_genres).intersection(dict_list[0][movie]))
                      / len(set(fav_genres).union(dict_list[0][movie])))

            # convert the single score to a float and cap it at 1.0
            score = min(float(test[0]), 1.0)

            # add a vertex for the review and connect it to the movie with the calculated weight
            graph[0].add_vertex(score, "Review")
            graph[0].add_edge(dict_list[1].get(movie), score, weight)
        except ValueError:

            # ignore conversion issues for the review score
            pass
    return


def load_weighted_review_graph(reviews_file: str, movie_file: str, threshold: float) -> list[WeightedGraph]:
    """Constructs two weighted graphs connecting reviews to movies and the user's favorite movies to other movies.

    This function reads from movie and review datasets, constructing graphs where nodes represent movies or reviews,
    and edges represent relationships based on genre similarity and review scores. One graph is the full graph while
    the other is a simplified version based on a similarity threshold.

    The weights on the edges between movies and reviews are determined by how closely the movie genres align with
    the user's preferred genres.

    Preconditions:
        - reviews_file is a path to a valid CSV file with review data.
        - movie_file is a path to a valid CSV file with movie data.
    """
    # initialize two graphs: one full and one simplified
    list_graphs = [WeightedGraph(), WeightedGraph()]

    # initialize dictionaries to store movie titles and genres
    dict_list = [{}, {}]

    # initialize a set to collect all unique genres
    genres_list = []

    # load movie data from the file
    with io.open(movie_file, 'r', encoding="utf-8") as file:

        # skip header row
        next(file)

        # loop through each row in the movie CSV file
        for row in csv.reader(file):
            # assign movie ID as key and title as value in dict_list[1]
            dict_list[1][row[0]] = row[1]

            # add a vertex for each movie in the full graph
            list_graphs[0].add_vertex(row[1], "Movie")

            # extract genres, format them, and assign to dict_list[0] with movie ID as key
            dict_list[0][row[0]] = set([genre.strip().capitalize() for genre in row[9].replace(", ", "&").split("&")])

            # union current genres with the total set of genres to keep it unique
            genres_list = list(set(genres_list).union(dict_list[0][row[0]]))

        # remove any empty genre entries that might have been added
        genres_list.remove("")

    # prompt the user to select their favorite movie and store the selection
    list_fav = get_favourite_movie(dict_list[1])
    print(list_fav)

    # get the user to search again if they want to
    while list_fav[1] == "Search again":
        list_fav = get_favourite_movie(dict_list[1])

    # prompt the user to select their favorite genres and store the selections
    fav_genres = get_favourite_genres(genres_list)

    # iterate over each movie in the dataset to calculate genre similarity and create graph connections
    for item in dict_list[1]:
        # calculate the genre similarity weight between the user's favorite movie and the current movie
        weight = (len(dict_list[0][item].intersection(dict_list[0][list_fav[0]]))
                  / len(dict_list[0][item].union(dict_list[0][list_fav[0]])))

        # add vertices and edges to the simplified graph based on the similarity threshold
        add_vertex_to_simplified_graph(list_fav[1], dict_list[1][item], weight, list_graphs[1], threshold)

        # for the full graph, always add edges between the user's favorite movie and the current movie
        list_graphs[0].add_edge(dict_list[1][item], list_fav[1], weight)

    # apply the user's preferences to both the full and simplified graphs to centralize the analysis around them
    list_graphs[0].set_user_preferences(list_fav[1], set(fav_genres))
    list_graphs[1].set_user_preferences(list_fav[1], set(fav_genres))

    # load and process review data, integrating it into the graphs
    with open(reviews_file, 'r', encoding="utf-8") as file:

        # skip header row
        next(file)
        for row in csv.reader(file):
            # extract review scores, split them, and prepare for processing
            test = row[5].strip("'*").strip(" ").split("/")

            # integrate review data into the graphs based on scores and genre similarity
            build_with_new_vertex_fraction(list_graphs, test, dict_list, row[0], genres_list)

    # return the list containing both the full and simplified graphs
    return list_graphs


def get_favourite_movie(films: dict[str, str]) -> tuple[str, str]:
    """
    Prompts the user to enter a keyword related to their favorite movie and
    allows them to select the movie from a filtered list based on the input keyword.

    If the user's initial search does not yield satisfactory results, they can choose to search again.
    """
    # initialize the Tkinter root window in hidden mode to avoid showing an empty window
    root = tk.Tk()
    root.withdraw()

    # initialize an empty list to store filtered movie IDs based on the search
    filtered_ids = []

    # convert the dictionary of films to a list of film titles for easier searching
    film_list = [films[key] for key in films]
    current_string = ""

    # loop until a valid movie selection is made or the user cancels the search
    while len(current_string) == 0:

        # prompt the user for a keyword to search for their favorite movie
        input_str = simpledialog.askstring("Favorite Movie", "Search for your favorite movie:")

        # if the user cancels the dialog, return empty values
        if input_str is None:
            return "", ""

        # filter the list of movies based on the user's input keyword
        filtered = [film for film in film_list if input_str.strip().lower() in film.lower()]

        # create a dictionary mapping filtered movie IDs to titles for lookup
        filtered_ids = {films[film]: film for film in films if films[film] in filtered}

        # add an option to search again to the list of filtered movies
        filtered = ["Search again"] + filtered

        # create a Toplevel window to display the filtered movie options
        menu_window = tk.Toplevel()
        menu_window.title("Choose Movie")

        # create a Listbox widget within the window to list the filtered movie options
        options_listbox = tk.Listbox(menu_window, width=50, height=10)
        options_listbox.pack(padx=10, pady=10)
        for option in filtered:
            options_listbox.insert(tk.END, option)

        # function to handle the confirmation of the movie selection
        def confirm_selection() -> None:
            """Confirms the selection made by the user."""
            selection_index = options_listbox.curselection()
            if selection_index:
                selected_option = options_listbox.get(selection_index)
                nonlocal current_string
                current_string = selected_option
                menu_window.destroy()

        # add a button in the window for the user to confirm their movie selection
        confirm_button = tk.Button(menu_window, text="Confirm", command=confirm_selection)
        confirm_button.pack(pady=5)

        # wait for the user to make a selection or close the menu window
        menu_window.wait_window(menu_window)

    # close the Tkinter root window to free resources after the selection is made
    root.quit()

    # return the ID and title of the selected movie, or empty strings if no selection was made
    return filtered_ids.get(current_string, ""), current_string


def get_favourite_genres(genres: list[str]) -> set[str]:
    """Prompts the user to select their favorite genres from a provided list via a graphical interface.
    The user can select multiple genres, and their choices are returned as a set.

    The function opens a dialog box where the user can input the indices of their favorite genres,
    supporting multiple selections separated by commas. The selected genres are returned as a set of strings.
    """
    # initialize the Tkinter root window in hidden mode to avoid showing an empty window
    root = tk.Tk()
    root.withdraw()

    # initialize an empty set to store the user's favorite genres
    favourite_genres = set()

    # the 'option' variable is initially set to an invalid value to ensure the loop is entered
    option = f"{len(genres)}"

    # loop to ensure valid input from the user. Continues until valid genres are selected or the dialog is canceled
    while len(favourite_genres) == 0 and int(option.strip()) >= len(genres) or int(option.strip()) < 0:

        # open a dialog box asking the user for their favorite genres, displaying all available genres
        input_str = simpledialog.askstring("Favorite Genres",
                                           "Enter the keys corresponding to genres separated by a comma to choose your"
                                           " favorite genres from the following options:\n\n"
                                           + "\n".join(f"{i}: {genres[i]}" for i in range(len(genres))))

        # if the dialog is canceled (input_str is None), return an empty set immediately
        if input_str is None:
            return set()

        # split the input string by commas to allow for multiple genre selections
        selected_genre_keys = input_str.split(",")

        # the case for multiple genres
        if len(selected_genre_keys) > 1:
            selected_genre_keys = [part.strip() for part in input_str.split(",")]

        # iterate over each index provided by the user
        for values in selected_genre_keys:

            # trim whitespace and check if the index is numeric and within the range of available genres
            if values.strip().isnumeric() and int(values.strip()) < len(genres) and int(values.strip()) >= 0:

                # if valid, add the corresponding genre to the set of favorite genres
                favourite_genres.add(genres[int(values)])

    # once selections are made or the dialog is canceled, close the Tkinter root window to free resources
    root.quit()

    # return the set of selected favorite genres
    return favourite_genres


def print_recommended_movies(graph: WeightedGraph, limit: int, show_num_of_reviews: bool = False) -> None:
    """Recommends movies based on the user's preferences and prints the results.

    Preconditions:
        - limit > 0
    """
    # display the user's chosen preferences for context
    print("Based on your preferrences: \n"
          + f"    - Preferred Movie: {graph.preferred_movie} \n"
          + f"    - Preferred Genre(s): {graph.preferred_genres}")

    # retrieve the preferred movie vertex for reference
    preferred_movie = graph.get_vertex(graph.preferred_movie)

    # gather movies that are considered similar based on graph connections
    similar_movies = preferred_movie.neighbours

    # calculate and sort movies by a combined score of average strict score and overall similarity
    # this score is meant to prioritize movies closely matching the user's preferences
    average_scores = [
        (sim_movie, sim_movie.average_score_strict() * sim_movie.overall_similarity_score(preferred_movie))
        for sim_movie in similar_movies if sim_movie != preferred_movie]
    average_scores.sort(key=lambda x: x[1], reverse=True)

    # limit the recommendations to the specified limit
    recommended_movies = average_scores[:limit]

    # print the recommendations along with their matching scores and optionally the number of reviews
    print(f"Here are the top {limit} movies matching your preferrences: \n")
    rank = 1
    for movie in recommended_movies:

        # format text to optionally include the number of reviews
        num_reviews_text = f"Num of reviews: {movie[0].get_number_of_reviews()}"

        # calculate and round the similarity score to be user-friendly
        rounded_similarity_score = round(movie[0].overall_similarity_score(preferred_movie), 2)

        # print the movie recommendation details
        print(f"#{rank} -> {movie[0].item}: {rounded_similarity_score * 100} % match\n"
              f"       Avg Score: {round(movie[0].average_score(), 2) * 100}  {show_num_of_reviews * num_reviews_text}")
        rank += 1


def display_recommendations(whole_graph: WeightedGraph, partial_graph: WeightedGraph) -> None:
    """Offers the user a choice of how to display movie recommendations based on their preferences.

        Displays the recommendations in one of three ways based on the users choice:
            1. Prints them on the console (default).
            2. Shows a graph plot with all the vertices representing a movie or review.
            3. Shows a quadrant visualization of all the movies.
    """
    # initialize Tkinter root window in hidden mode to prompt for user input
    root = tk.Tk()
    root.withdraw()

    # define the options for displaying recommendations
    options = {1: 'Print', 2: 'Graph', 3: 'Quadrant'}

    # prompt the user for their preferred display method
    user_input = simpledialog.askinteger("Display Recommendations",
                                         'How would you like your recommendations displayed?\n\n'
                                         + f"Options are {options}\n\nEnter the corresponding key to choose")

    # handle the case where user input is invalid or not given; default to printing recommendations
    if user_input is None or user_input not in options:
        print("Invalid Option Chosen. Printing recommendations (by default)")
        print_recommended_movies(whole_graph, 10, True)
        return

    # retrieve the chosen option from the options dictionary using the user's input
    chosen_option = options[user_input]
    root.quit()

    # based on the user's choice, display the recommendations accordingly
    if chosen_option == 'Graph':

        # if the user chooses "Graph", visualize the recommendations using the partial graph
        visualization1.visualize_graph(partial_graph, max_vertices=5000)
    elif chosen_option == 'Quadrant':

        # if "Quadrant" is chosen, plot the movie recommendations using quadrant visualization
        visualization2.plot_movie_recommendations(visualization2.load_data_with_graph(whole_graph), 3)
    else:

        # default action: Print the recommendations to the console.
        print_recommended_movies(whole_graph, 10, True)


def add_vertex_to_simplified_graph(target_movie: str, movie: str, weight: float,
                                   g: WeightedGraph, threshold: float) -> None:
    """Adds a vertex to a simplified version of the movie graph in which it ONLY includes vertices that are
    similar enough to the preferred film (i.e. weight is within a certain threshold).

    This is done to reduce the computations needed to produce the visualization
    and thus reduce the execution time at the cost of having less vertices displayed.

    Preconditions:
        - target_movie != ''
        - movie != ''
        - threshold > 0
    """
    # always ensure the target movie is present in the graph
    g.add_vertex(target_movie, kind="Movie")

    # check if the current movie's similarity weight meets or exceeds the threshold
    if weight >= threshold:

        # add the current movie to the graph if it passes the threshold check
        g.add_vertex(movie, kind="Movie")

        # if the current movie is not the target movie, establish a connection between them
        if movie != target_movie:

            # the connection represents the similarity, helping to visualize how closely related the movies are
            g.add_edge(movie, target_movie, weight)


if __name__ == "__main__":
    # requirement for "code quality"
    # "code-checking tools"

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

    movies_reviews = "data/rotten_tomatoes_movie_reviews.csv"
    movies_file = "data/rotten_tomatoes_movies.csv"
    graphs = load_weighted_review_graph(movies_reviews, movies_file, 0.7)
    movie_graph, simplified_graph = graphs[0], graphs[1]
    display_recommendations(movie_graph, simplified_graph)
