from datetime import date
import customtkinter as ctk
from database import HabitTrackerDB

# إعداد الثيم الأخضر العام
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")


class HabitTrackerApp(ctk.CTk):

  def __init__(self):
    super().__init__()
    self.db = HabitTrackerDB()

    self.title("متابع العادات والروتين اليومي - Habit Tracker")
    self.geometry("620x730")
    self.minsize(520, 650)

    # الهيدر العلوي
    self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.header_frame.pack(fill="x", padx=25, pady=15)

    self.title_label = ctk.CTkLabel(
        self.header_frame,
        text="✨ جدول الروتين والعادات اليومية",
        font=("Tajawal", 20, "bold"),
        text_color="#2ecc71",
    )
    self.title_label.pack(side="right")

    # عداد الـ Streak
    self.streak_badge = ctk.CTkLabel(
        self.header_frame,
        text="🔥 التتابع: 0 أيام",
        font=("Tajawal", 13, "bold"),
        text_color="#e67e22",
    )
    self.streak_badge.pack(side="left")

    # إطار التقدم والمؤشر
    self.progress_frame = ctk.CTkFrame(self, fg_color="#1a2e22", corner_radius=12)
    self.progress_frame.pack(fill="x", padx=25, pady=5)

    self.progress_label = ctk.CTkLabel(
        self.progress_frame,
        text="نسبة الإنجاز اليومي: 0%",
        font=("Tajawal", 14, "bold"),
        text_color="white",
    )
    self.progress_label.pack(anchor="w", padx=15, pady=(10, 2))

    self.progress_bar = ctk.CTkProgressBar(
        self.progress_frame, width=540, height=14, progress_color="#27ae60"
    )
    self.progress_bar.set(0)
    self.progress_bar.pack(padx=15, pady=5)

    # عبارة التحفيز الديناميكية
    self.quote_label = ctk.CTkLabel(
        self.progress_frame,
        text="💪 هيا نبدأ يومنا بكل نشاط وبركة!",
        font=("Tajawal", 12),
        text_color="#a3e4d7",
    )
    self.quote_label.pack(anchor="w", padx=15, pady=(2, 10))

    # إطار إضافة عادة جديدة
    self.add_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.add_frame.pack(fill="x", padx=25, pady=10)

    self.habit_entry = ctk.CTkEntry(
        self.add_frame,
        placeholder_text="أضف عادة جديدة لروتينك...",
        width=290,
        height=38,
        font=("Tajawal", 13),
    )
    self.add_frame_side = self.habit_entry.pack(
        side="left", padx=(5, 10), fill="x", expand=True
    )

    self.category_menu = ctk.CTkComboBox(
        self.add_frame,
        values=["طاعات", "تطوير ذات", "صحة", "إنتاجية", "عام"],
        width=110,
        height=38,
        font=("Tajawal", 12),
    )
    self.category_menu.pack(side="left", padx=5)
    self.category_menu.set("طاعات")

    self.add_btn = ctk.CTkButton(
        self.add_frame,
        text="إضافة",
        command=self.add_new_habit,
        width=80,
        height=38,
        fg_color="#27ae60",
        hover_color="#219653",
        font=("Tajawal", 13, "bold"),
    )
    self.add_btn.pack(side="left", padx=5)

    # منطقة العرض القابلة للتمرير (قائمة المهام)
    self.scrollable_frame = ctk.CTkScrollableFrame(
        self, width=540, height=360, corner_radius=12, fg_color="#121f18"
    )
    self.scrollable_frame.pack(pady=10, fill="both", expand=True, padx=25)

    # الفوتر السفلي (التاريخ)
    self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
    self.footer_frame.pack(fill="x", padx=25, pady=5)

    self.date_label = ctk.CTkLabel(
        self.footer_frame,
        text=f"📅 تاريخ اليوم: {date.today()}",
        font=("Tajawal", 12),
        text_color="#7f8c8d",
    )
    self.date_label.pack(side="right")

    # تحميل العادات
    self.load_habits()

  def load_habits(self):
    for widget in self.scrollable_frame.winfo_children():
      widget.destroy()

    habits = self.db.get_habits_with_status()
    completed_count = 0

    for habit_id, title, category, completed in habits:
      var = ctk.BooleanVar(value=bool(completed))
      if completed:
        completed_count += 1

      # إطار لكل عادة لتبدو منظمة
      item_frame = ctk.CTkFrame(
          self.scrollable_frame, fg_color="#1a2e22", corner_radius=8
      )
      item_frame.pack(fill="x", pady=5, padx=5)

      cb = ctk.CTkCheckBox(
          item_frame,
          text=f"  {title}",
          variable=var,
          command=lambda hid=habit_id, v=var: self.on_check_toggle(hid, v),
          font=("Tajawal", 14),
          checkmark_color="#ffffff",
          fg_color="#27ae60",
          hover_color="#219653",
      )
      cb.pack(side="right", padx=15, pady=10)

      # شارة التصنيف الملونة
      cat_badge = ctk.CTkLabel(
          item_frame,
          text=f" {category} ",
          font=("Tajawal", 11),
          fg_color="#0e1b14",
          text_color="#2ecc71",
          corner_radius=6,
      )
      cat_badge.pack(side="left", padx=15, pady=10)

    self.update_progress(completed_count, len(habits))

  def on_check_toggle(self, habit_id, var):
    self.db.toggle_habit(habit_id, var.get())
    habits = self.db.get_habits_with_status()
    completed_count = sum(1 for h in habits if h[3] == 1)
    self.update_progress(completed_count, len(habits))

  def add_new_habit(self):
    title = self.habit_entry.get().strip()
    category = self.category_menu.get()
    if title:
      self.db.add_custom_habit(title, category)
      self.habit_entry.delete(0, "end")
      self.load_habits()

  def update_progress(self, completed, total):
    ratio = completed / total if total > 0 else 0
    self.progress_bar.set(ratio)
    percentage = int(ratio * 100)

    self.progress_label.configure(
        text=f"نسبة الإنجاز اليومي: {percentage}%  ({completed}/{total})"
    )

    # تحديث الـ Streak
    current_streak = self.db.update_streak(percentage)
    self.streak_badge.configure(text=f"🔥 التتابع: {current_streak} أيام")

    # تغيير العبارات التحفيزية بناءً على نسبة الإنجاز
    if percentage == 100:
      self.quote_label.configure(
          text="🌟 مذهل! أتممت جميع مهامك اليومية، استمر في هذا التميز!"
      )
    elif percentage >= 70:
      self.quote_label.configure(
          text="💪 أداء رائع جداً، لم يتبقَ إلا القليل لإتمام يومك!"
      )
    elif percentage >= 30:
      self.quote_label.configure(
          text="🌱 بداية موفقة، واصل السير بخطى ثابتة نحو أهدافك."
      )
    else:
      self.quote_label.configure(
          text="☕ هيا ابدأ بإنجاز أول عادة، يومك مبارك!"
      )


if __name__ == "__main__":
  app = HabitTrackerApp()
  app.mainloop()