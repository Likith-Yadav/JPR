# JPR Public School Website

## Database Setup

This project uses PostgreSQL for production and SQLite for development.

### Local Development (SQLite)

For local development, the project will automatically use SQLite. No additional configuration is needed.

### Production Deployment (PostgreSQL)

For production deployment on Railway:

1. **Add PostgreSQL to your Railway project**:
   - Go to Railway → Add Plugin → PostgreSQL
   - Railway will automatically provision a PostgreSQL database

2. **Configure Environment Variables**:
   - In Railway, go to your project → Variables
   - Add the following environment variables:
     - `DATABASE_URL`: Railway will automatically set this when you add PostgreSQL
     - `SECRET_KEY`: A secure random string for Django
     - `DEBUG`: Set to `False` for production

3. **Run Migrations**:
   - After deploying, run migrations on Railway:
     ```
     python manage.py migrate
     ```

4. **Create a Superuser** (if needed):
   - You can create a superuser through Railway's CLI or by running:
     ```
     python manage.py createsuperuser
     ```

### Migrating Data from SQLite to PostgreSQL

If you have existing data in your SQLite database that you want to migrate to PostgreSQL, follow these steps:

1. Make sure you have the required packages installed:
   ```
   pip install django dj-database-url psycopg2-binary
   ```

2. Set your PostgreSQL connection string in the `.env` file:
   ```
   DATABASE_URL=postgresql://postgres:password@host:port/database
   ```

3. Run the migration script:
   ```
   python migrate_to_postgres.py
   ```

   This script will:
   - Dump all data from your SQLite database to a JSON file in the `fixtures` directory
   - Load that data into your PostgreSQL database

4. Verify the migration by checking your PostgreSQL database.

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```
cp .env.example .env
```

## Deployment

1. **Ensure `.gitignore` includes**:
   ```
   db.sqlite3
   .env
   ```

2. **Push your changes to GitHub**:
   ```
   git add .
   git commit -m "Update for PostgreSQL deployment"
   git push
   ```

3. **Railway will automatically deploy your changes**

## Important Notes

- Never commit `db.sqlite3` to your repository
- Always use environment variables for sensitive information
- For local development, SQLite is fine, but for production, always use PostgreSQL
