# QZ Trivia API

A RESTful API backend for managing and delivering trivia quizzes.
It serves questions across multiple categories, scores user submissions,
and provides immediate feedback and reviews.

This API is designed to work seamlessly with a custom user-facing client.
You can find the client application here: [justinharry4/qz-trivia][1]

[1]: https://github.com/justinharry4/qz-trivia

## Tech Stack

- Framework: Django + Django REST Framework
- Database: PostgreSQL (production), SQLite (development)
- Frontend Consumer: React + TypeScript ([view repo here][1])

## Setup

1. Clone the repository:

   ```
   git clone https://github.com/justinharry4/qz-trivia-api.git

   cd qz-trivia-api
   ```

2. Set up a virtual environment:

   ```
   # For MacOS/Linux
   python -m venv myenv
   source myenv/bin/activate

   # For Windows:
   myenv\Scripts\activate
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Run migrations:

   ```
   python manage.py migrate
   ```

5. Populate the database (with quiz data from OpenTrivia DB):

   ```
   python manage.py seed_db
   ```

6. Start the development server:

   ```
   python manage.py runserver
   ```

## CORS Setup

If your frontend runs on a separate origin (e.g., http://localhost:3000),
ensure CORS is configured correctly:

```
# qz/settings/dev.py

CORS_ALLOWED_ORIGINS = ["http://localhost:3000",]
# replace http://localhost:3000 with your local API's origin
```

## Features

- RESTful API for accessing quiz data
- Randomized question delivery
- Quiz submission and review

## Future Improvements

- Implement timed quizzes for added challenge
- Add user authentication, including optional social login (e.g., Google)
- Enable support for user-generated quizzes and custom question sets

Your feedback, suggestions, and contributions are welcome!
Feel free to open issues or submit pull requests to improve the project.
You may also contact me at justin.h.anyika@gmail.com.
