from datetime import date, timedelta
import sqlite3


class HabitTrackerDB:

  def __init__(self, db_name="habits_tracker.db"):
    self.conn = sqlite3.connect(db_name)
    self.create_tables()
    self.seed_presets()

  def create_tables(self):
    cursor = self.conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT DEFAULT 'عام'
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER,
                log_date TEXT,
                completed INTEGER DEFAULT 0,
                FOREIGN KEY(habit_id) REFERENCES habits(id),
                UNIQUE(habit_id, log_date)
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                streak INTEGER DEFAULT 0,
                last_completed_date TEXT
            )
        """)
    cursor.execute(
        "INSERT OR IGNORE INTO user_stats (id, streak, last_completed_date)"
        " VALUES (1, 0, '')"
    )
    self.conn.commit()

  def seed_presets(self):
    cursor = self.conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM habits")
    if cursor.fetchone()[0] == 0:
      presets = [
          ("قيام الليل", "طاعات"),
          ("أذكار الصباح والمساء", "طاعات"),
          ("ورد سورة البقرة", "طاعات"),
          ("الصلوات الخمس (في وقتها)", "طاعات"),
          ("الصدقة اليومية", "طاعات"),
          ("قراءة / تعلم اللغة الإنجليزية", "تطوير ذات"),
          ("الرياضة والنشاط البدني", "صحة"),
          ("الاهتمام بالنفس والعناية الشخصية", "صحة"),
          ("العمل على المشروع الخاص", "إنتاجية"),
          ("التعلم وقراءة كتاب", "تطوير ذات"),
      ]
      cursor.executemany(
          "INSERT INTO habits (title, category) VALUES (?, ?)", presets
      )
      self.conn.commit()

  def get_habits_with_status(self, target_date=None):
    if not target_date:
      target_date = str(date.today())
    cursor = self.conn.cursor()
    cursor.execute(
        """
            SELECT h.id, h.title, h.category, COALESCE(d.completed, 0)
            FROM habits h
            LEFT JOIN daily_logs d ON h.id = d.habit_id AND d.log_date = ?
        """,
        (target_date,),
    )
    return cursor.fetchall()

  def toggle_habit(self, habit_id, completed, target_date=None):
    if not target_date:
      target_date = str(date.today())
    cursor = self.conn.cursor()
    cursor.execute(
        """
            INSERT INTO daily_logs (habit_id, log_date, completed)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) DO UPDATE SET completed=excluded.completed
        """,
        (habit_id, target_date, int(completed)),
    )
    self.conn.commit()

  def add_custom_habit(self, title, category="عام"):
    cursor = self.conn.cursor()
    cursor.execute(
        "INSERT INTO habits (title, category) VALUES (?, ?)", (title, category)
    )
    self.conn.commit()

  def get_streak(self):
    cursor = self.conn.cursor()
    cursor.execute("SELECT streak FROM user_stats WHERE id = 1")
    row = cursor.fetchone()
    return row[0] if row else 0

  def update_streak(self, percentage):
    cursor = self.conn.cursor()
    today_str = str(date.today())
    cursor.execute(
        "SELECT streak, last_completed_date FROM user_stats WHERE id = 1"
    )
    streak, last_date = cursor.fetchone()

    if percentage >= 80:  # إذا وصل الإنجاز 80% فأكثر يعتبر اليوم منجزاً
      if last_date != today_str:
        yesterday_str = str(date.today() - timedelta(days=1))
        if last_date == yesterday_str:
          streak += 1
        elif last_date == "" or last_date < yesterday_str:
          streak = 1
        cursor.execute(
            "UPDATE user_stats SET streak = ?, last_completed_date = ? WHERE"
            " id = 1",
            (streak, today_str),
        )
        self.conn.commit()
    return streak