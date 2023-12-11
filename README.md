# Movie Recommender
This is web service API that provides extensive information about a wide range of movies and offers movie recommendations based on various filters and comparisons. It is designed to assist users in exploring and discovering movies that match their preferences and interests.

## Key Features: ##

**Movie Information:**

Retrieve detailed information about a vast collection of movies, including title, genre, release date, popularity, and more.
Filter movies by specific criteria such as genre, release year, original language, and minimum vote count.

**Movie Recommendations:**

Obtain personalized movie recommendations by comparing a selected movie with others in the database using.
Recommendations can be tailored based on filters like minimum rating, minimum vote count, and minimum release year.
The API suggests similar movies to the one provided, helping users discover films they might enjoy. This feature is based on cosine similarities of each movie data.


**Admin Functionality:**

Admin users have access to additional functionality through the API.
They can create database tables, insert movie data from CSV files, and generate recommendations for movies.
Admins can manage user accounts, roles, and authentication.


**Endpoints:**

/movies (POST): Retrieve a list of movies based on user-defined filters.  
/similar_movies/<int:id> (GET): Get movie recommendations similar to the provided movie ID, with optional filter parameters.  
/login (POST): Authenticate users and grant access to protected admin features.  
/logout (GET): Log out the current user.  
/sign_up (POST): Allow users to create new accounts with various roles.  
/create_tables (GET): Admin-only route to create database tables.  
/insert_movies (GET): Admin-only route to insert movie data from CSV files.  
/insert_similar_movies/<int:count> (GET): Admin-only route to generate and insert movie recommendations.  
