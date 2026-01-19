"""
Database migration script
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import init_database, get_session, SentimentRecord, DataSource
from dotenv import load_dotenv

load_dotenv()


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    try:
        engine = init_database()
        print("✓ Tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def verify_tables():
    """Verify tables exist and are accessible"""
    print("\nVerifying tables...")
    try:
        session = get_session()
        
        # Try to query each table
        sentiment_count = session.query(SentimentRecord).count()
        print(f"✓ sentiment_records table accessible ({sentiment_count} records)")
        
        source_count = session.query(DataSource).count()
        print(f"✓ data_sources table accessible ({source_count} sources)")
        
        session.close()
        return True
    except Exception as e:
        print(f"✗ Error verifying tables: {e}")
        return False


def seed_data():
    """Seed database with sample data"""
    print("\nSeeding sample data...")
    try:
        session = get_session()
        
        # Add sample data sources
        sources = ['twitter', 'news', 'custom']
        for source_name in sources:
            existing = session.query(DataSource).filter(
                DataSource.name == source_name
            ).first()
            
            if not existing:
                source = DataSource(
                    name=source_name,
                    status='active'
                )
                session.add(source)
        
        session.commit()
        print("✓ Sample data seeded successfully")
        session.close()
        return True
    except Exception as e:
        print(f"✗ Error seeding data: {e}")
        return False


def main():
    """Main migration function"""
    print("=" * 60)
    print("Database Migration Script")
    print("=" * 60)
    
    print(f"\nDatabase Configuration:")
    print(f"  Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  Port: {os.getenv('DB_PORT', '5432')}")
    print(f"  Database: {os.getenv('DB_NAME', 'sentiment_db')}")
    print(f"  User: {os.getenv('DB_USER', 'postgres')}")
    
    # Create tables
    if not create_tables():
        print("\nMigration failed at table creation")
        return False
    
    # Verify tables
    if not verify_tables():
        print("\nMigration failed at table verification")
        return False
    
    # Seed data
    if not seed_data():
        print("\nMigration failed at data seeding")
        return False
    
    print("\n" + "=" * 60)
    print("Migration completed successfully!")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
