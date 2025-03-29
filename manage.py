import argparse
import os
import sys
import subprocess

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.database import init_db, SessionLocal
from apps.user.operations import UserOperation


def create_admin_user(name, email, password):
    """Create an admin user if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if user exists
        user = UserOperation.get_user_by_email(db, email)
        if user:
            if user.role == "admin":
                print(f"Admin user {email} already exists.")
                return
            else:
                # Update role to admin
                user.role = "admin"
                db.commit()
                print(f"User {email} has been upgraded to admin.")
                return
        
        # Create new admin user
        user = UserOperation.create_user(db, name, email, password, role="admin")
        print(f"Admin user {email} created successfully.")
    except Exception as e:
        print(f"Error creating admin user: {e}")
    finally:
        db.close()


def run_migrations(args):
    """Run database migrations"""
    if args.command == "init":
        # Initialize migrations
        subprocess.run(["alembic", "init", "migrations"], check=True)
        print("Migrations initialized.")
    elif args.command == "generate":
        # Generate a new migration
        message = args.message or "Auto-generated migration"
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)
        print(f"Migration created: {message}")
    elif args.command == "upgrade":
        # Upgrade database to the latest revision or to a specific one
        revision = args.revision or "head"
        subprocess.run(["alembic", "upgrade", revision], check=True)
        print(f"Database upgraded to: {revision}")
    elif args.command == "downgrade":
        # Downgrade database to a previous revision
        revision = args.revision or "-1"
        subprocess.run(["alembic", "downgrade", revision], check=True)
        print(f"Database downgraded to: {revision}")
    elif args.command == "history":
        # Show migration history
        subprocess.run(["alembic", "history"], check=True)
    else:
        print("Unknown migration command.")


def run_initdb(args):
    """Initialize the database"""
    init_db()
    print("Database initialized.")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Chat2API Management Tool")
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    
    # Command: python manage.py migration
    migration_parser = subparsers.add_parser("migration", help="Manage database migrations")
    migration_parser.add_argument("command", choices=["init", "generate", "upgrade", "downgrade", "history"], help="Migration command")
    migration_parser.add_argument("--message", "-m", help="Migration message")
    migration_parser.add_argument("--revision", "-r", help="Revision identifier")
    
    # Command: python manage.py initdb
    initdb_parser = subparsers.add_parser("initdb", help="Initialize the database")
    
    # Command: python manage.py createadmin
    admin_parser = subparsers.add_parser("createadmin", help="Create admin user")
    admin_parser.add_argument("--name", required=True, help="Admin name")
    admin_parser.add_argument("--email", required=True, help="Admin email")
    admin_parser.add_argument("--password", required=True, help="Admin password")
    
    args = parser.parse_args()
    
    if args.action == "migration":
        run_migrations(args)
    elif args.action == "initdb":
        run_initdb(args)
    elif args.action == "createadmin":
        create_admin_user(args.name, args.email, args.password)
    else:
        parser.print_help()
