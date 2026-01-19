"""
Test PostgreSQL connection
"""
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test database connection with different configurations"""
    
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_user = os.getenv('DB_USER', 'postgres')
    db_password = os.getenv('DB_PASSWORD', '')
    
    print("=" * 60)
    print("PostgreSQL Connection Test")
    print("=" * 60)
    print(f"\nConfiguration:")
    print(f"  Host: {db_host}")
    print(f"  Port: {db_port}")
    print(f"  User: {db_user}")
    print(f"  Password: {'*' * len(db_password) if db_password else '(empty)'}")
    
    # Try connecting to default postgres database first
    print(f"\n1. Testing connection to 'postgres' database...")
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='postgres'
        )
        print("✓ Successfully connected to 'postgres' database")
        
        # Try to create sentiment_db if it doesn't exist
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if sentiment_db exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'sentiment_db'")
        exists = cursor.fetchone()
        
        if not exists:
            print("\n2. Creating 'sentiment_db' database...")
            cursor.execute("CREATE DATABASE sentiment_db")
            print("✓ Database 'sentiment_db' created successfully")
        else:
            print("\n2. Database 'sentiment_db' already exists")
        
        cursor.close()
        conn.close()
        
        # Try connecting to sentiment_db
        print("\n3. Testing connection to 'sentiment_db' database...")
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database='sentiment_db'
        )
        print("✓ Successfully connected to 'sentiment_db' database")
        conn.close()
        
        print("\n" + "=" * 60)
        print("All tests passed! Database is ready.")
        print("=" * 60)
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nPossible solutions:")
        print("  1. Verify the password is correct")
        print("  2. Check PostgreSQL pg_hba.conf allows password authentication")
        print("  3. Make sure you're using the correct user credentials")
        print("  4. Try setting trust authentication temporarily in pg_hba.conf")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_connection()
