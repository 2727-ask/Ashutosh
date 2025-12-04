#!/usr/bin/env python3
"""
Apply schema migration to local old database
"""

import subprocess
import sys
import getpass

def main():
    print("="*80)
    print("Apply Schema Migration to Local Database")
    print("="*80)
    
    # Get password
    print("\nEnter credentials for local MySQL (port 3680):")
    user = input("MySQL user [root]: ").strip() or 'root'
    password = getpass.getpass("MySQL password: ")
    
    # Read migration file
    migration_file = '/Users/ashutoshkumbhar/Development/imathas-neo/schema_migration.sql'
    print(f"\nReading migration file: {migration_file}")
    
    with open(migration_file, 'r') as f:
        migration_sql = f.read()
    
    # Count statements
    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
    print(f"Found {len(statements)} SQL statements to execute\n")
    
    # Apply migration
    print("Applying migration...")
    cmd = ['mysql', f'-u{user}', f'-P3680', 'imathasdb']
    if password:
        cmd.append(f'-p{password}')
    
    result = subprocess.run(cmd, input=migration_sql, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Migration applied successfully!")
        if result.stdout:
            print(f"\nOutput:\n{result.stdout}")
    else:
        print(f"✗ Migration failed with error:")
        print(result.stderr)
        sys.exit(1)
    
    # Verify
    print("\nVerifying migration...")
    verify_cmd = f"""
    SELECT COUNT(*) as column_count FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = 'imathasdb' AND TABLE_NAME = 'imas_courses';
    """
    
    result = subprocess.run(cmd + ['-sN', '-e', verify_cmd], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✓ Local database now has columns in imas_courses")
        
    print("\nNext steps:")
    print("1. Dump the upgraded local database:")
    print("   mysqldump -u root -P 3680 imathasdb > /tmp/old_upgraded.sql")
    print("\n2. Apply to Docker database:")
    print("   docker exec -i mysql-primary mysql -uroot -pRa\\!nb0w imathasdb < /tmp/old_upgraded.sql")


if __name__ == '__main__':
    main()
