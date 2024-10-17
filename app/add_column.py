from sqlalchemy import create_engine, text
from app.database import DATABASE_URL

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(
        text("ALTER TABLE scheduled_calls ADD COLUMN custom_description TEXT"))
    conn.commit()

print("Column 'custom_description' added successfully.")
