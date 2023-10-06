from app import app
from flask import request
# from sqlalchemy import text
# from flask import jsonify
# from sqlalchemy.orm import sessionmaker
from app.utilities import read_movie_data_list
from app.utilities import read_most_similar_movies

# @app.route('/movies', methods=['GET'])
# def movies():
#     # return read_movie_data_list()
#     filters = {
#     'genres': ['Action', 'Adventure'],   
#     'release_date_from': 2000,
#     'original_language': 'en',
#     'sorting': ('popularity', 'desc'),
#     'min_vote_count': 100
#     }  
#     movie_data = read_movie_data_list(filters)
#     return movie_data

@app.route('/movies', methods=['POST'])
def movies():
    # Get the filter object from request body
    filters = request.json
    
    # Call the read_movie_data_list() function with filters
    movie_data = read_movie_data_list(filters)
    
    # Return the movie data as JSON response
    return movie_data


# @app.route('/similar_movies', methods=['GET'])
# def get_movies(id):
#     # return read_movie_data_list()
#     movie_data = read_most_similar_movies(id)
#     return movie_data


@app.route('/similar_movies/<int:id>', methods=['GET'])
def get_movies(id):
    optional_args = {
        'head': None,
        'min_rating': None,
        'min_vote_count': None,
        'min_release_year': None
    }

    # Iterate through the dictionary and extract values from URL query parameters
    for arg, _ in optional_args.items():
        value = request.args.get(arg)
        if value is not None:
            # Convert value to the appropriate data type, if needed
            if arg == 'min_rating':
                value = float(value)
            elif arg == 'min_vote_count':
                value = int(value)
            elif arg == 'min_release_year':
                value = int(value)
            elif arg == 'head':
                value = int(value)
            # Update the value in the dictionary
            optional_args[arg] = value

    # Pass the extracted values to the function
    movie_data = read_most_similar_movies(id, **optional_args)
    return movie_data

@app.route('/', methods=['GET'])
def home():
    return 'Hello world!'