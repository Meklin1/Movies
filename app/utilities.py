from flask import jsonify
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app import db
from app.models import Movies
from app.models import Similar_Movies
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from sqlalchemy import column
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import threading
from scipy.sparse import coo_matrix

def get_movies_for_similarities(specific_columns):
    
    # Query specific columns from the movies table
    columns = [column(col_name) for col_name in specific_columns]
    movies = db.session.query(*columns).from_statement(text(
        'SELECT ' + ', '.join(specific_columns) + ' FROM movies')).all()


    # Convert movies' data to a list of dictionaries
    movies_data = []
    for movie in movies:
        movie_data = {}
        for i in range(len(specific_columns)):
            movie_data[specific_columns[i]] = movie[i]
        movies_data.append(movie_data)

    return pd.DataFrame(movies_data)




def write_recommendations_to_psql(sim_count, chunk_size=2000):
    tfidf = TfidfVectorizer(stop_words='english')
    
    columns_for_movie_data = ['id', 'title', 'genres', 'original_language', 'overview',
                        'production_companies', 'tagline', 'credits', 'keywords']
    columns_for_keywords = ['title', 'genres', 'original_language', 'overview',
                        'production_companies', 'tagline', 'credits', 'keywords']
    # Query all movie data from the movies table
    movies = get_movies_for_similarities(columns_for_movie_data)

    # Concatenate the text data from the selected columns into a single Series
    documents = movies[columns_for_keywords].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)

    tfidf_matrix = tfidf.fit_transform(documents)

    print("Terms (words):", tfidf.get_feature_names_out())

    # File path
    file_path = "my_file.txt"

    # Open file in write mode
    with open(r'data\keywords.txt', 'w', encoding="utf-8") as file:
        # Write string to file
        keywords_str = '\n'.join(tfidf.get_feature_names_out())
        # Write string to file
        file.write(keywords_str)
    print("Shape:", tfidf_matrix.shape)
    
    num = 0

    for i in range(0, tfidf_matrix.shape[0] - 1, chunk_size):
        start_idx = i
        end_idx = min(i + chunk_size, tfidf_matrix.shape[0])

        cosine_sim = cosine_similarity(tfidf_matrix[start_idx:end_idx], tfidf_matrix)

        most_similar_indices = cosine_sim.argsort()[:, ::-1][:, 1:sim_count + 1]
        movie_ids = np.asarray(movies.iloc[most_similar_indices.flatten()]['id'].values.tolist())
        similar_movies_list = []

        for j in range(start_idx, end_idx):
            # movie_id = int(movies.iloc[j]['id'])
            movie_id = int(movies.loc[movies.index[j], 'id'])
            similar_ids = [int(movie_ids[(j - start_idx) * sim_count + k]) for k in range(sim_count)]
            similar_ids_str = ','.join(map(str, similar_ids))
            similar_movies = Similar_Movies(id=movie_id, similar_ids=similar_ids_str)
            similar_movies_list.append(similar_movies)

        # Add all similar_movies records to the session in a single transaction
        db.session.add_all(similar_movies_list)
        db.session.commit()
        num += 1
        print(f'{start_idx}  {end_idx} counter = {num}')
    print("Recommendations written to similar_movies table.")


def insert_movies_from_csv(csv_file_path, chunk_size=5000):
    """Function to read data from CSV file in chunks and insert into movies table in chunks."""
    total_rows = 0
    inserted_rows = 0

    try:
        print(f'Inserting movies from CSV file: {csv_file_path}...')
        # Get the total number of rows in the CSV file
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            total_rows = sum(1 for line in f) - 1  # Subtract 1 to exclude header row
        print(f'Total rows in CSV file: {total_rows}')

        # Read CSV file in chunks
        for i, chunk in enumerate(pd.read_csv(csv_file_path, chunksize=chunk_size, encoding='utf-8', sep=';')):
            # Convert chunk to list of dictionaries
            movies = chunk.to_dict(orient='records')
            # Insert movies into the database
            db.session.bulk_insert_mappings(Movies, movies)
            db.session.commit()
            inserted_rows += len(chunk)
            print(f'Inserted {inserted_rows} out of {total_rows} rows ({round(inserted_rows/total_rows*100, 2)}%)')

    except Exception as e:
        db.session.rollback()
        print(f'Error inserting movies from CSV: {e}')

    finally:
        db.session.close()

    print(f'Inserted {inserted_rows} rows into movies table.')
    
    
def create_tables_psql():
    """Function to create the movies table in the database."""
    db.create_all()
    db.session.commit()    

def read_movie_data_list(filters, head=20, offset=0):
    #     filters = {
    # 'genres': ['Action', 'Adventure'],   
    # 'release_date_from': 2000,
    # 'original_language': 'en',
    # 'sorting': ('popularity', 'desc'),
    # 'min_vote_count': 100
    # }  
    genres = filters.get('genres')
    release_date = filters.get('release_date')
    original_language = filters.get('original_language')
    sorting = filters.get('sorting')
    min_vote_count = filters.get('min_vote_count')
    min_vote_avg = filters.get('min_vote_average')

    # Create a session
    Session = sessionmaker(bind=db.engine)
    session = Session()

    # Build the base query
    query = session.query(Movies)
    # Apply filters
    if genres is not None:
        for genre in genres:           
            query = query.filter(Movies.genres.like(f'%{genre}%'))
            
    if release_date is not None:
        query = query.filter(text(f"date_part('year', Movies.release_date::date) > {release_date}"))
    if original_language is not None:
        query = query.filter(Movies.original_language == original_language)
    if min_vote_count is not None:
        query = query.filter(Movies.vote_count > min_vote_count)
    if min_vote_avg is not None:
        query = query.filter(Movies.vote_average > min_vote_avg)
        
    # Apply sorting
    if sorting is not None:
        column_name, sort_order = sorting
        if column_name not in ['popularity', 'vote_count', 'vote_average']:
            raise ValueError("Invalid column name in sorting object")
        # Check if the sort order is valid
        if sort_order not in ['asc', 'desc']:
            raise ValueError("Invalid sort order in sorting object")
        else:
            if column_name == 'popularity':
                column = Movies.popularity
            elif column_name == 'vote_count':
                column = Movies.vote_count
            elif column_name == 'vote_average':
                column = Movies.vote_average

            if sort_order == 'asc':
                query = query.order_by(column.asc(), Movies.id.asc())
            else:
                query = query.order_by(column.desc(), Movies.id.asc())
    else:
        query = query.order_by(Movies.id.asc())
    
    # Apply pagination
    query = query.limit(head).offset(offset)
    print(query)
    # Execute the query and fetch results
    results = query.all()
    print(results)
    # Convert results to dictionary
    movie_data_list = []
    for row in results:
        movie_data = {
            'id': row.id,
            'title': row.title,
            'backdrop_path': row.backdrop_path,
            'original_language': row.original_language,
            'overview': row.overview,
            'popularity': row.popularity,
            'poster_path': row.poster_path,
            'release_date': row.release_date,
            'runtime': row.runtime,
            'vote_average': row.vote_average,
            'vote_count': row.vote_count,
            'tagline': row.tagline,
            'credits': row.credits,
            'genres': row.genres,
            'production_companies': row.production_companies
        }
        movie_data_list.append(movie_data)

    # Close the session
    session.close()

    return jsonify(movie_data_list)

def read_most_similar_movies(film_id, **kwargs):
    similar_IDs = Similar_Movies.query.filter_by(id=film_id).first()
    min_vote_count = (kwargs.get('min_vote_count') or 0)
    min_rating = (kwargs.get('min_rating') or 0)
    min_release_date = kwargs.get('min_release_date')
    head = None
    if(kwargs.get('head') is not None):
        head = kwargs.get('head')
    if head is None or head < 1 :
        head = 20
    
    similar_movies = []
    movie_data = {}

    if similar_IDs:
        counter = 0
        similar_ID_values = similar_IDs.similar_ids.split(',')
        
        for value in similar_ID_values:
            
            result = Movies.query.get(int(value))
            # result = Movies.query.filter_by(id=int(value)).first()
            
            if result and result.vote_count >= min_vote_count and result.vote_average >= min_rating:
                movie_data = {
                    'id': result.id,
                    'title': result.title,
                    'backdrop_path': result.backdrop_path,
                    'original_language': result.original_language,
                    'overview': result.overview,
                    'popularity': result.popularity,
                    'poster_path': result.poster_path,
                    'release_date': result.release_date,
                    'runtime': result.runtime,
                    'vote_average': result.vote_average,
                    'vote_count': result.vote_count,
                    'tagline': result.tagline,
                    'credits': result.credits,
                    'genres': result.genres,
                    'production_companies': result.production_companies
                }
                if min_release_date is not None:
                    release_year = result.release_date.year
                    if release_year >= min_release_date:

                        similar_movies.append(movie_data)
                        counter += 1
                else:
                    similar_movies.append(movie_data)
                    counter += 1
            if counter == head:
                break

    return jsonify(similar_movies)