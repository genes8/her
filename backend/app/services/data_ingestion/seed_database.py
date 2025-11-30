"""Database seeding script.

Run with: python -m app.services.data_ingestion.seed_database
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.models.base import SessionLocal
from app.services.data_ingestion.synthetic_generator import SyntheticDataGenerator


def seed_database(num_lsoa: int = 100) -> None:
    """Seed the database with synthetic data."""
    print("🌱 Starting database seeding...")
    print(f"   Generating {num_lsoa} LSOA areas with related data")

    db = SessionLocal()
    try:
        generator = SyntheticDataGenerator(db)
        counts = generator.generate_all(num_lsoa=num_lsoa)

        print("\n✅ Database seeded successfully!")
        print("   Generated records:")
        for table, count in counts.items():
            print(f"   - {table}: {count}")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Seed database with synthetic data")
    parser.add_argument(
        "--num-lsoa",
        type=int,
        default=100,
        help="Number of LSOA areas to generate (default: 100)",
    )
    args = parser.parse_args()

    seed_database(num_lsoa=args.num_lsoa)
