"""CSC111 Project 2: Identifying Quality Films Through Rotten Tomatoes' Metrics

Module Description
==================

This module contains the _Vertex and Graph classes along with some custom methods we created.
All methods made originally by us are given comments, docstrings, doctests, and preconditions as required.

Copyright and Usage Information
===============================

This file is provided solely for the personal and private use of CSC111 students, teaching staff,
and the Department of Computer Science at the University of Toronto St. George campus.
All forms of distribution of this code, whether as given or with any changes, are
expressly prohibited.

This file is Copyright (c) Akram Klai, Reena Obmina, Edison Yao, Derek Lam.
"""
from __future__ import annotations
from typing import Any, Union
import networkx as nx


########################################################################################################################
# _Vertex class
########################################################################################################################
# @check_contracts
class _Vertex:
    """A vertex in a movie review graph, used to represent a user or a movie.

    Each vertex item is either a user id or movie title. Both are represented as strings,
    even though we've kept the type annotation as Any to be consistent with what was
    discussed in lecture.

    Instance Attributes:
        - item: The data stored in this vertex, representing a user or book.
        - kind: The type of this vertex: 'User' or 'Movie'.
        - neighbours: The vertices that are adjacent to this vertex.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'User', 'Movie'}
    """
    item: Any
    kind: str
    neighbours: set[_Vertex]

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'User', 'Movie'}
        """
        self.item = item
        self.kind = kind
        self.neighbours = set()


########################################################################################################################
# _WeightedVertex class
########################################################################################################################
# @check_contracts
class _WeightedVertex(_Vertex):
    """A vertex in a weighted movie review graph, used to represent a Review or a Movie.

    Instance Attributes:
        - item: The data stored in this vertex, representing a review or movie.
        - kind: The type of this vertex: 'Review' or 'Movie'.
        - neighbours: The vertices that are adjacent to this vertex, and their corresponding
                      edge weights.
        - preferred: Indicates whether the vertex is marked as preferred by the user, affecting
                     the prioritization in the recommendation process.

    Representation Invariants:
        - self not in self.neighbours
        - all(self in u.neighbours for u in self.neighbours)
        - self.kind in {'Review', 'Movie'}
        -
    """
    item: Any
    kind: str
    neighbours: dict[_WeightedVertex, Union[int, float]]
    preferred: bool

    def __init__(self, item: Any, kind: str) -> None:
        """Initialize a new vertex with the given item and kind.

        This vertex is initialized with no neighbours.

        Preconditions:
            - kind in {'Review', 'Movie'}
        """
        super().__init__(item, kind)
        self.neighbours = {}
        self.preferred = False

    def get_number_of_reviews(self) -> int:
        """Returns the number of reviews associated with this movie vertex.

        Preconditions:
            - self.kind == 'Movie'

        # test case: movie has no reviews
        >>> movie = _WeightedVertex("Frozen II", "Movie")
        >>> movie.get_number_of_reviews()
        0

        # test case: movie has reviews
        >>> movie = _WeightedVertex("Fast and Furious", "Movie")
        >>> review1 = _WeightedVertex("Review1", "Review")
        >>> review2 = _WeightedVertex("Review2", "Review")
        >>> movie.neighbours = {review1: 5, review2: 4}
        >>> movie.get_number_of_reviews()
        2

        # test case: movie only connected to other movies, not reviews
        >>> movie = _WeightedVertex("Blade Runner", "Movie")
        >>> other_movie1 = _WeightedVertex("Blade Runner 2049", "Movie")
        >>> other_movie2 = _WeightedVertex("Dune", "Movie")
        >>> movie.neighbours = {other_movie1: 1, other_movie2: 1}
        >>> movie.get_number_of_reviews()
        0
        """
        # check if the current vertex is a review or has insufficient neighbours
        if len(self.neighbours) <= 1 or self.kind == "Review":

            # return 0 if not a movie or no reviews to count
            return 0
        else:

            # filter and collect items of neighbours that are of kind 'review'
            reviews = [review.item for review in self.neighbours if review.kind == "Review"]

            # count and return the number of reviews
            return len(reviews)

    def average_score(self) -> float:
        """Returns the average review score for a film from all available reviews.
        This is represented by a decimal proportion out of 1.0.

        Preconditions:
            - self.kind == 'Movie'

        # test case: able to calculate average score
        >>> movie = _WeightedVertex("Fast and Furious", "Movie")
        >>> review1 = _WeightedVertex(0.6, "Review")
        >>> review2 = _WeightedVertex(0.9, "Review")
        >>> movie.neighbours = {review1: 0.8, review2: 0.9}
        >>> movie.average_score()
        0.75

        # test case: movie has no reviews at all
        >>> movie = _WeightedVertex("Mary Poppins", "Movie")
        >>> movie.average_score()
        0

        # test case: movie connected only to other movies or non-review entities
        >>> movie = _WeightedVertex("The Lord of the Rings", "Movie")
        >>> movie1 = _WeightedVertex("The Hobbit", "Movie")
        >>> movie2 = _WeightedVertex("Fellowship of the Ring", "Movie")
        >>> movie.neighbours = {movie1: 0.8, movie2: 0.9}
        >>> movie.average_score()
        0
        """
        # check if the current vertex represents a movie and has review neighbours
        if len(self.neighbours) == 0 or self.kind == "Review":

            # not applicable for review vertices or movies without reviews
            return 0
        else:

            # extract unique review scores from neighbours
            reviews = {review.item for review in self.neighbours if review.kind == "Review"}

            # if there are no reviews after filtering neighbours, return 0
            if len(reviews) == 0:
                return 0

            # calculate and return the average score:
            # sum of review scores divided by the number of reviews
            return sum(reviews) / len(reviews)

    def average_score_strict(self, min_number_of_reviews: int = 3) -> float:
        """Returns the average review score for a film from all available reviews.
        This is represented by a decimal proportion out of 1.0.

        If a movie does NOT have enough reviews based on a minimum needed to
        recommended it, then return it as 0.

        Preconditions:
            - self.kind == 'Movie'
            - min_number_of_reviews > 0
            - The number of neighbor vertices with kind == 'Review' >= min_number_of_reviews

        # test case: movie has enough reviews to calculate average score
        >>> movie = _WeightedVertex("Bluey", "Movie")
        >>> review1 = _WeightedVertex(0.6, "Review")
        >>> review2 = _WeightedVertex(0.9, "Review")
        >>> review3 = _WeightedVertex(0.7, "Review")
        >>> movie.neighbours = {review1: 0.6, review2: 0.9, review3: 0.7}
        >>> movie.average_score_strict()
        0.7333333333333334

        # test case: movie does not have enough reviews
        >>> movie = _WeightedVertex("My Little Pony", "Movie")
        >>> review1 = _WeightedVertex(0.6, "Review")
        >>> review2 = _WeightedVertex(0.9, "Review")
        >>> movie.neighbours = {review1: 0.6, review2: 0.9}
        >>> movie.average_score_strict()
        0

        # test case: movie has no reviews
        >>> movie = _WeightedVertex("Mickey Mouse", "Movie")
        >>> movie.average_score_strict()
        0
        """
        # ensure this vertex is a movie and has at least the minimum required number of review neighbours
        if len(self.neighbours) == 0 or self.kind == "Review":

            # not applicable for review vertices or movies without any reviews
            return 0
        else:

            # collect unique review scores from neighbours
            reviews = {review.item for review in self.neighbours if review.kind == "Review"}

            # check if the number of reviews meets the minimum requirement
            if len(reviews) < min_number_of_reviews:
                return 0

            # calculate and return the average score if the minimum number of reviews is met
            return sum(reviews) / len(reviews)

    def average_similarity(self) -> float:
        """Returns the average weight between a movie and its reviews.
        This weight is the proportion of the movie's genre similarity to the user's preference.

        Preconditions:
            - self.kind == 'Movie'

        # test case: movie with reviews having similarity scores
        >>> movie = _WeightedVertex("The Matrix", "Movie")
        >>> review1 = _WeightedVertex(0.8, "Review")
        >>> review2 = _WeightedVertex(0.7, "Review")
        >>> movie.neighbours = {review1: 0.8, review2: 0.7}
        >>> movie.average_similarity()
        0.75

        # test case: movie without reviews
        >>> movie = _WeightedVertex("Toy Story", "Movie")
        >>> movie.average_similarity()
        0

        # test case: review vertex (should not compute similarity)
        >>> review1 = _WeightedVertex(0.2, "Review")
        >>> review1.average_similarity()
        0
        """
        # check if this vertex represents a movie and has review neighbours
        if len(self.neighbours) == 0 or self.kind == "Review":

            # not applicable for review vertices or movies without any reviews
            return 0
        else:

            # extract the similarity scores (edge weights) from the connected review vertices
            reviews = {self.neighbours[review] for review in self.neighbours if review.kind == "Review"}

            # ensure there are similarity scores to calculate an average
            if len(reviews) == 0:

                # return 0 if there are no connected reviews to calculate similarity
                return 0

            # calculate and return the average similarity score
            return sum(reviews) / len(reviews)

    def overall_similarity_score(self, movie: _WeightedVertex, weight_for_movie: float = 0.5,
                                 weight_for_genres: float = 0.5) -> float:
        """Returns the overall similarity score: a score that represents how "similar"
        this movie is to a particular movie and set of given genres.

        The score is calculated as follows: 0.5 * {similarity to movie} + 0.5 * {similarity to genres}
        The similarity to movie is stored as a weight between the two movies.
        The similarity to genres is calculated by computing the average weight in all reviews.

        Preconditions:
            - self.kind == 'Movie'
            - movie.kind == 'Movie'
            - 0 <= weight_for_movie <= 1
            - 0 <= weight_for_genres <= 1
            - The sum(weight_for_movie, weight_for_genres) == 1

        # test case: two movies with reviews having similarity scores
        >>> matrix = _WeightedVertex("The Matrix", "Movie")
        >>> inception = _WeightedVertex("Inception", "Movie")
        >>> review1 = _WeightedVertex(0.7, "Review")
        >>> review2 = _WeightedVertex(0.8, "Review")
        >>> matrix.neighbours = {inception: 0.6, review1: 0.7, review2: 0.8}
        >>> inception.neighbours = {matrix: 0.7}
        >>> matrix.overall_similarity_score(inception)
        0.675

        # test case: only movie similarity, no genre similarity considered
        >>> movieC = _WeightedVertex("Movie C", "Movie")
        >>> movieD = _WeightedVertex("Movie D", "Movie")
        >>> movieC.neighbours = {movieD: 1.0}
        >>> movieD.neighbours = {movieC: 1.0}
        >>> movieC.overall_similarity_score(movieD, weight_for_movie=1.0, weight_for_genres=0.0)
        1.0

        # test case: higher weight to genre similarity over movie similarity
        >>> movieX = _WeightedVertex("Movie X", "Movie")
        >>> movieY = _WeightedVertex("Movie Y", "Movie")
        >>> reviewX1 = _WeightedVertex(0.9, "Review")
        >>> movieX.neighbours = {movieY: 0.4, reviewX1: 0.9}
        >>> movieY.neighbours = {movieX: 0.4}
        >>> movieX.overall_similarity_score(movieY, weight_for_movie=0.3, weight_for_genres=0.7)
        0.75

        # test case: higher weight to movie similarity over genre similarity
        >>> movieA = _WeightedVertex("Movie A", "Movie")
        >>> movieB = _WeightedVertex("Movie B", "Movie")
        >>> reviewA1 = _WeightedVertex(0.5, "Review")
        >>> reviewA2 = _WeightedVertex(0.6, "Review")
        >>> movieA.neighbours = {movieB: 0.8, reviewA1: 0.5, reviewA2: 0.6}
        >>> movieB.neighbours = {movieA: 0.8}
        >>> movieA.overall_similarity_score(movieB, weight_for_movie=0.7, weight_for_genres=0.3)
        0.725
        """
        # calculate the direct similarity to the specified movie
        movie_similarity = self.neighbours[movie] * weight_for_movie

        # calculate the average genre similarity from reviews
        genre_similarity = self.average_similarity() * weight_for_genres

        # return the combined overall similarity score
        return movie_similarity + genre_similarity


########################################################################################################################
# Graph class
########################################################################################################################
# @check_contracts
class Graph:
    """A graph used to represent a movie review network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _Vertex object.
    _vertices: dict[Any, _Vertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'Review', 'Movie'}
        """
        if item not in self._vertices:
            self._vertices[item] = _Vertex(item, kind)

    def add_edge(self, item1: Any, item2: Any) -> None:
        """Add an edge between the two vertices with the given items in this graph.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            v1.neighbours.add(v2)
            v2.neighbours.add(v1)
        else:
            raise ValueError

    def adjacent(self, item1: Any, item2: Any) -> bool:
        """Return whether item1 and item2 are adjacent vertices in this graph.

        Return False if item1 or item2 do not appear as vertices in this graph.
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            return any(v2.item == item2 for v2 in v1.neighbours)
        else:
            return False

    def get_neighbours(self, item: Any) -> set:
        """Return a set of the neighbours of the given item.

        Note that the *items* are returned, not the _Vertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_all_vertices(self, kind: str = '') -> set:
        """Return a set of all vertex items in this graph.

        If kind != '', only return the items of the given vertex kind.

        Preconditions:
            - kind in {'', 'Review', 'Movie'}
        """
        if kind != '':
            return {v.item for v in self._vertices.values() if v.kind == kind}
        else:
            return set(self._vertices.keys())


########################################################################################################################
# WeightedGraph class
########################################################################################################################
# @check_contracts
class WeightedGraph(Graph):
    """A weighted graph used to represent a movie review network that keeps track of review scores.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _WeightedVertex object.
    #     - preferred_genres:
    #         A set containing the genres preferred by the user. This attribute is used
    #         to tailor the movie recommendations to the user's tastes.
    #     - preferred_movie:
    #         The title of the movie that the user prefers most. This is used as a reference
    #         point for calculating similarity scores between movies.
    _vertices: dict[Any, _WeightedVertex]
    preferred_genres: set[str]
    preferred_movie: str

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}
        self.preferred_genres = set()
        self.preferred_movie = ''
        Graph.__init__(self)

    def __contains__(self, item: Any) -> bool:
        """Checks if the specified item exists as a vertex in the graph's collection of vertices.
        """
        return item in self._vertices

    def add_vertex(self, item: Any, kind: str) -> None:
        """Add a vertex with the given item and kind to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.

        Preconditions:
            - kind in {'Review', 'Movie'}
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedVertex(item, kind)

    def add_edge(self, item1: Any, item2: Any, weight: Union[int, float] = 1) -> None:
        """Add an edge between the two vertices with the given items in this graph,
        with the given weight.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]
            v1.neighbours[v2] = weight
            v2.neighbours[v1] = weight
        else:
            raise ValueError

    def get_number_of_vertices(self) -> int:
        """Returns the number of vertices."""
        return len(self._vertices)

    def get_vertex(self, item: Any) -> _WeightedVertex:
        """Gets the vertex in the graph based on its associated item."""
        return self._vertices[item]

    def set_user_preferences(self, movie: str, genres: set[str]) -> None:
        """Sets the preferred attribute to True for the vertex that matches the preferred film.
        The method marks the chosen movie vertex as preferred and updates the preferred genres.

        Preconditions:
            - self._vertices[movie].kind == 'Movie'
            - genres is a set of strings, where each string represents a valid genre

        # test case: test setting user preferences for preferred movie and genres
        >>> g = WeightedGraph()
        >>> g.add_vertex("Inception", "movie")
        >>> g.add_vertex("Dark Knight", "movie")
        >>> g.set_user_preferences("Inception", {"action", "sci-fi"})
        >>> g.preferred_movie
        'Inception'
        >>> sorted(g.preferred_genres)
        ['action', 'sci-fi']
        >>> g.get_vertex("Inception").kind
        'Chosen Movie'
        >>> g.get_vertex("Inception").preferred
        True

        # test case: attempting to set preferences for a non-existent movie
        >>> g.set_user_preferences("Nonexistent Movie", {"comedy"})
        Traceback (most recent call last):
        ...
        ValueError
        """
        # check if the specified movie title exists as a vertex within the graph's vertices
        if movie in self._vertices:

            # assign the user's chosen movie as the preferred movie for personalized recommendations
            self.preferred_movie = movie
            vertex = self._vertices[movie]

            # mark the vertex corresponding to the chosen movie as preferred
            vertex.preferred = True

            # update the kind of the vertex to 'Chosen Movie' to distinguish it from other movie vertices
            vertex.kind = 'Chosen Movie'

            # update the set of preferred genres based on the user's input
            self.preferred_genres = genres
        else:

            # if the specified movie is not found within the graph, an error is raised
            raise ValueError

    def to_networkx(self, max_vertices: int = 5000) -> nx.Graph:
        """Convert this graph into a networkx Graph.

        max_vertices specifies the maximum number of vertices that can appear in the graph.
        (This is necessary to limit the visualization output for large graphs.)
        """
        graph_nx = nx.Graph()
        v_center = self._vertices[self.preferred_movie]
        for v in self._vertices.values():
            if v == v_center:
                continue
            graph_nx.add_node(v.item, kind=v.kind)

            for u in v.neighbours.keys():
                if graph_nx.number_of_nodes() < max_vertices:
                    graph_nx.add_node(u.item, kind=u.kind)

                if u.item in graph_nx.nodes:
                    graph_nx.add_edge(v.item, u.item, weight=u.overall_similarity_score(v) + u.average_score())

            if graph_nx.number_of_nodes() >= max_vertices:
                break
        return graph_nx


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
