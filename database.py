import sqlite3

from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


# =====================================
# DATABASE PATH
# =====================================

BASE_DIRECTORY = Path(
    __file__
).resolve().parent

DATABASE_PATH = (
    BASE_DIRECTORY
    / "orchestrator.db"
)


# =====================================
# CONNECTION
# =====================================

@contextmanager
def get_connection():
    """
    Provide a database connection as a context manager.

    Commits on success, rolls back on error, and always closes
    the connection afterwards. Plain sqlite3.Connection objects
    only commit/rollback when used as a context manager - they
    never close themselves, which leaks a connection every time
    this used to be called directly. Wrapping it here means every
    existing "with get_connection() as connection:" call site
    keeps working exactly as before, just without the leak.
    """

    connection = sqlite3.connect(
        DATABASE_PATH
    )

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    try:

        yield connection

        connection.commit()

    except Exception:

        connection.rollback()

        raise

    finally:

        connection.close()


# =====================================
# INITIALIZE DATABASE
# =====================================

def initialize_database():
    """
    Create required database tables and
    add missing columns to existing
    databases.
    """

    with get_connection() as connection:

        cursor = connection.cursor()

        # =============================
        # REQUESTS TABLE
        # =============================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_prompt TEXT NOT NULL,
                final_request TEXT,
                created_at TEXT NOT NULL,

                understanding_score INTEGER,
                needs_clarification INTEGER,

                prompt_score INTEGER,
                enhanced_prompt TEXT,

                task_category TEXT,

                requires_ai_fallback INTEGER,

                recommended_llm TEXT,
                recommendation_reason TEXT,

                status TEXT NOT NULL
                DEFAULT 'created'
            )
        """)

        # =============================
        # INTERACTIONS TABLE
        # =============================

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                request_id INTEGER NOT NULL,

                interaction_type TEXT NOT NULL,

                content TEXT NOT NULL,

                created_at TEXT NOT NULL,

                FOREIGN KEY (request_id)
                    REFERENCES requests(id)
                    ON DELETE CASCADE
            )
        """)

        # =============================
        # DATABASE MIGRATIONS
        # =============================

        cursor.execute(
            "PRAGMA table_info(requests)"
        )

        existing_columns = {
            column[1]
            for column in cursor.fetchall()
        }

        required_columns = {
            "final_request": "TEXT",
            "task_category": "TEXT",
            "requires_ai_fallback": "INTEGER",
            "recommended_llm": "TEXT",
            "recommendation_reason": "TEXT",
            "status": "TEXT DEFAULT 'created'"
        }

        for (
            column_name,
            column_type
        ) in required_columns.items():

            if (
                column_name
                not in existing_columns
            ):

                cursor.execute(
                    f"""
                    ALTER TABLE requests
                    ADD COLUMN {column_name}
                    {column_type}
                    """
                )


# =====================================
# CREATE REQUEST
# =====================================

def create_request(original_prompt):
    """
    Create a new request.

    Returns:
        int: The ID of the new request.
    """

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO requests (
                original_prompt,
                created_at,
                status
            )
            VALUES (?, ?, ?)
        """, (
            original_prompt,
            datetime.now().isoformat(),
            "processing"
        ))

        return cursor.lastrowid


# =====================================
# SAVE INTERACTION
# =====================================

def save_interaction(
    request_id,
    interaction_type,
    content
):
    """
    Save an interaction connected to
    a request.
    """

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO interactions (
                request_id,
                interaction_type,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            request_id,
            interaction_type,
            content,
            datetime.now().isoformat()
        ))


# =====================================
# UPDATE REQUEST
# =====================================

def update_request(
    request_id,
    understanding_score=None,
    needs_clarification=None,
    prompt_score=None,
    enhanced_prompt=None,
    final_request=None,
    task_category=None,
    requires_ai_fallback=None,
    recommended_llm=None,
    recommendation_reason=None,
    status=None
):
    """
    Update an existing request.

    Only provided values are updated.
    """

    fields = []
    values = []

    if understanding_score is not None:

        fields.append(
            "understanding_score = ?"
        )

        values.append(
            understanding_score
        )

    if needs_clarification is not None:

        fields.append(
            "needs_clarification = ?"
        )

        values.append(
            int(needs_clarification)
        )

    if prompt_score is not None:

        fields.append(
            "prompt_score = ?"
        )

        values.append(
            prompt_score
        )

    if enhanced_prompt is not None:

        fields.append(
            "enhanced_prompt = ?"
        )

        values.append(
            enhanced_prompt
        )

    if final_request is not None:

        fields.append(
            "final_request = ?"
        )

        values.append(
            final_request
        )

    if task_category is not None:

        fields.append(
            "task_category = ?"
        )

        values.append(
            task_category
        )

    if requires_ai_fallback is not None:

        fields.append(
            "requires_ai_fallback = ?"
        )

        values.append(
            int(requires_ai_fallback)
        )

    if recommended_llm is not None:

        fields.append(
            "recommended_llm = ?"
        )

        values.append(
            recommended_llm
        )

    if recommendation_reason is not None:

        fields.append(
            "recommendation_reason = ?"
        )

        values.append(
            recommendation_reason
        )

    if status is not None:

        fields.append(
            "status = ?"
        )

        values.append(
            status
        )

    # Nothing to update.
    if not fields:

        return

    values.append(
        request_id
    )

    query = f"""
        UPDATE requests
        SET {", ".join(fields)}
        WHERE id = ?
    """

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute(
            query,
            values
        )


# =====================================
# GET REQUEST INTERACTIONS
# =====================================

def get_request_interactions(request_id):
    """
    Get all interactions related to
    one request.
    """

    with get_connection() as connection:

        cursor = connection.cursor()

        cursor.execute("""
            SELECT
                id,
                request_id,
                interaction_type,
                content,
                created_at
            FROM interactions
            WHERE request_id = ?
            ORDER BY id
        """, (
            request_id,
        ))

        return cursor.fetchall()
