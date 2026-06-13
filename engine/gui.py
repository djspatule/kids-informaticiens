"""
engine/gui.py — MissionWindow
Beautiful space-themed tkinter GUI for the kids' treasure hunt.

Design:
  - Deep-space navy background (#0B0B2E)
  - Animated star field with twinkling
  - Per-player colour themes (Romy: purple, Oscar: teal)
  - Animated score counter, mission progress stars
  - Full-window success overlay with falling stars
  - Final celebration screen with fireworks
  - Parent mode (Ctrl+Shift+P) showing raw state
  - Idle pulse animation after 60 s of no interaction
  - Keyboard shortcuts help panel
"""

from __future__ import annotations

import logging
import math
import random
import tkinter as tk
import traceback
from datetime import datetime, timezone
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Colour constants
# ---------------------------------------------------------------------------
BG_DEEP        = "#0B0B2E"   # main background — deep space
BG_PANEL       = "#12123E"   # slightly lighter panel bg
BG_PANEL2      = "#1A1A52"   # card / section bg
BORDER_DIM     = "#2A2A6E"   # faint border / separator
TEXT_WHITE     = "#E8E8FF"   # primary text (slightly off-white)
TEXT_DIM       = "#8888AA"   # secondary / dim text
GOLD           = "#FFD700"   # completed star, score
GOLD_DIM       = "#806B00"   # dimmed gold
STAR_DONE      = "★"
STAR_TODO      = "☆"
HINT_COLOR     = "#AAAACC"
HINT_PENALTY   = "#FF8C42"
SUCCESS_BG     = "#0D3320"
FINAL_BG       = "#0D0D00"
OVERLAY_GOLD   = "#FFD700"

# Idle timeout before gentle pulse animation (ms)
IDLE_TIMEOUT_MS = 60_000

# Score count-up animation step interval (ms)
SCORE_ANIM_MS = 40


# ---------------------------------------------------------------------------
# Helper: geometry — place window in top-right corner
# ---------------------------------------------------------------------------

def _top_right(win: tk.Tk, w: int, h: int) -> None:
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    margin = 16
    x = sw - w - margin
    y = margin
    win.geometry(f"{w}x{h}+{x}+{y}")


# ---------------------------------------------------------------------------
# MissionWindow
# ---------------------------------------------------------------------------

class MissionWindow(tk.Tk):
    """
    Main game window.

    Constructor args:
        player_name   — raw player key, e.g. "romy"
        config        — player config dict (from config/romy.json)
        state_manager — engine.state.StateManager instance
        mission_loader— engine.missions.MissionLoader instance
        check_runner  — engine.checker.CheckRunner instance
    """

    WIN_W = 480
    WIN_H = 560

    def __init__(
        self,
        player_name: str,
        config: dict,
        state_manager,
        mission_loader,
        check_runner,
    ):
        super().__init__()

        self.player_name   = player_name
        self.config        = config
        self.state_manager = state_manager
        self.mission_loader = mission_loader
        self.check_runner  = check_runner

        # -- runtime state --
        self.state: dict         = state_manager.load()
        self.current_mission: dict = {}
        self.hint_visible: bool  = False
        self._score_display: int = self.state.get("score", 0)
        self._score_target: int  = self._score_display
        self._overlay_active: bool = False
        self._final_shown: bool  = False
        self._idle_job: Optional[str] = None
        self._pulse_job: Optional[str] = None
        self._parent_mode: bool  = False
        self._current_photo      = None  # keeps PIL PhotoImage alive

        # -- PIL availability (for mission images) --
        try:
            from PIL import Image as PILImage, ImageTk
            self._pil_available = True
        except ImportError:
            self._pil_available = False

        # -- per-player theme --
        self.theme_color = config.get("color_theme", "#CE93D8")
        self.display_name = config.get("display_name", player_name.capitalize())
        self.role_title   = config.get("role_title", "Capitaine")
        self.total_missions = config.get("total_missions", 8)

        # -- star field data (x, y, base_colour, canvas_id, twinkle_phase) --
        self._stars: list[dict] = []
        self._drifters: list[dict] = []  # slowly drifting particles

        self._build_window()
        self._build_fonts()
        self._build_star_canvas()
        self._build_progress_section()
        self._build_mission_panel()
        self._build_bottom_buttons()
        self._bind_shortcuts()

        # Position top-right
        _top_right(self, self.WIN_W, self.WIN_H)

        # Initial render
        self._refresh_ui()

        # Start animations
        self._animate_stars()
        self._animate_drifters()

        # Start poll loop
        self._start_idle_timer()
        self.after(2000, self._poll)

    # ===================================================================
    # Window construction
    # ===================================================================

    def _build_window(self) -> None:
        self.title("🚀 Mission Espace")
        self.configure(bg=BG_DEEP)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        # Try to set a text icon — works on some WMs
        try:
            self.iconname("🚀")
        except tk.TclError:
            pass

    def _build_fonts(self) -> None:
        self.font_hero    = tkfont.Font(family="DejaVu Sans", size=17, weight="bold")
        self.font_title   = tkfont.Font(family="DejaVu Sans", size=14, weight="bold")
        self.font_body    = tkfont.Font(family="DejaVu Sans", size=12)
        self.font_small   = tkfont.Font(family="DejaVu Sans", size=10)
        self.font_tiny    = tkfont.Font(family="DejaVu Sans", size=9)
        self.font_stars   = tkfont.Font(family="DejaVu Sans", size=16)
        self.font_code    = tkfont.Font(family="DejaVu Sans Mono", size=26, weight="bold")
        self.font_trophy  = tkfont.Font(family="DejaVu Sans", size=22, weight="bold")

    # ---------------------------------------------------------------
    # Star-field canvas (top section, 480×130)
    # ---------------------------------------------------------------

    def _build_star_canvas(self) -> None:
        self.star_canvas = tk.Canvas(
            self,
            width=self.WIN_W,
            height=130,
            bg=BG_DEEP,
            highlightthickness=0,
        )
        self.star_canvas.pack(side="top", fill="x")

        # Draw static star field (60 tiny dots)
        for _ in range(65):
            x = random.randint(2, self.WIN_W - 2)
            y = random.randint(2, 128)
            r = random.choice([1, 1, 1, 2])
            # Some stars are slightly yellowish
            color = random.choice(["#FFFFFF", "#FFFFFF", "#FFFACD", "#EEEEFF"])
            cid = self.star_canvas.create_oval(
                x - r, y - r, x + r, y + r,
                fill=color, outline="",
            )
            # 12 of them will twinkle
            twinkle = len(self._stars) < 12
            self._stars.append({
                "id": cid,
                "base": color,
                "phase": random.uniform(0, math.tau),
                "speed": random.uniform(0.04, 0.09),
                "twinkle": twinkle,
            })

        # Slowly drifting particles (very faint, add depth)
        for _ in range(18):
            x = random.uniform(0, self.WIN_W)
            y = random.uniform(0, 130)
            cid = self.star_canvas.create_oval(
                x, y, x + 1, y + 1,
                fill="#3333AA", outline="",
            )
            self._drifters.append({
                "id": cid,
                "x": x, "y": y,
                "vx": random.uniform(-0.3, 0.3),
                "vy": random.uniform(-0.15, 0.15),
            })

        # Player title text — glowing effect using two overlapping texts
        cx = self.WIN_W // 2
        shadow_offset = 2
        self.star_canvas.create_text(
            cx + shadow_offset, 52 + shadow_offset,
            text=f"🚀 {self.role_title.upper()} {self.display_name.upper()}",
            font=self.font_hero,
            fill="#000033",
            tags="hero_shadow",
        )
        # Glow ring (slightly larger, faded theme colour)
        glow = self._lighten(self.theme_color, factor=0.3)
        self.star_canvas.create_text(
            cx - 1, 52 - 1,
            text=f"🚀 {self.role_title.upper()} {self.display_name.upper()}",
            font=self.font_hero,
            fill=glow,
            tags="hero_glow",
        )
        self.star_canvas.create_text(
            cx, 52,
            text=f"🚀 {self.role_title.upper()} {self.display_name.upper()}",
            font=self.font_hero,
            fill=self.theme_color,
            tags="hero_text",
        )

        # Subtitle line
        self.star_canvas.create_text(
            cx, 80,
            text="✦  Chasse au trésor spatiale  ✦",
            font=self.font_small,
            fill=TEXT_DIM,
            tags="subtitle",
        )

        # Thin accent line at bottom of canvas
        self.star_canvas.create_line(
            20, 110, self.WIN_W - 20, 110,
            fill=self.theme_color, width=1,
        )

        # "?" help button in top-right corner
        help_btn = tk.Label(
            self.star_canvas,
            text="❓",
            bg=BG_DEEP,
            fg=TEXT_DIM,
            font=self.font_small,
            cursor="hand2",
        )
        help_btn.place(x=self.WIN_W - 28, y=4)
        help_btn.bind("<Button-1>", lambda _: self._show_help())

    # ---------------------------------------------------------------
    # Progress section
    # ---------------------------------------------------------------

    def _build_progress_section(self) -> None:
        prog_frame = tk.Frame(self, bg=BG_PANEL, pady=6)
        prog_frame.pack(fill="x", padx=0)

        # Stars row + score on same line
        inner = tk.Frame(prog_frame, bg=BG_PANEL)
        inner.pack()

        self.lbl_stars = tk.Label(
            inner,
            text="",
            bg=BG_PANEL,
            fg=GOLD,
            font=self.font_stars,
        )
        self.lbl_stars.pack(side="left", padx=(12, 8))

        self.lbl_score = tk.Label(
            inner,
            text="Score: 0 pts",
            bg=BG_PANEL,
            fg=GOLD_DIM,
            font=self.font_small,
        )
        self.lbl_score.pack(side="left", padx=(0, 12))

        # Mission counter below stars
        self.lbl_counter = tk.Label(
            prog_frame,
            text="Mission 1 sur 8",
            bg=BG_PANEL,
            fg=TEXT_DIM,
            font=self.font_tiny,
        )
        self.lbl_counter.pack()

        # Thin separator
        sep = tk.Frame(self, bg=BORDER_DIM, height=1)
        sep.pack(fill="x")

    # ---------------------------------------------------------------
    # Mission panel (scrollable text area)
    # ---------------------------------------------------------------

    def _build_mission_panel(self) -> None:
        panel = tk.Frame(self, bg=BG_PANEL2, padx=16, pady=12)
        panel.pack(fill="both", expand=True, padx=8, pady=(8, 4))
        self._mission_panel = panel

        # Image panel (above title; hidden until a mission provides an image)
        self._img_label = tk.Label(panel, bg=BG_PANEL2, bd=0, highlightthickness=0)
        # Not packed here — _update_mission_image() packs it when an image is available

        # Mission title
        self.lbl_mission_title = tk.Label(
            panel,
            text="",
            bg=BG_PANEL2,
            fg=self.theme_color,
            font=self.font_title,
            wraplength=self.WIN_W - 64,
            justify="left",
            anchor="w",
        )
        self.lbl_mission_title.pack(fill="x", pady=(0, 6))

        # Separator under title
        sep = tk.Frame(panel, bg=self.theme_color, height=1)
        sep.pack(fill="x", pady=(0, 10))

        # Scrollable description using Text widget (readonly)
        txt_frame = tk.Frame(panel, bg=BG_PANEL2)
        txt_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(txt_frame, orient="vertical", bg=BG_PANEL2)
        scrollbar.pack(side="right", fill="y")

        self.txt_description = tk.Text(
            txt_frame,
            bg=BG_PANEL2,
            fg=TEXT_WHITE,
            font=self.font_body,
            wrap="word",
            relief="flat",
            bd=0,
            padx=4,
            pady=4,
            height=7,
            state="disabled",
            cursor="arrow",
            yscrollcommand=scrollbar.set,
            selectbackground=BG_PANEL2,
            insertbackground=BG_PANEL2,
            exportselection=False,
        )
        self.txt_description.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.txt_description.yview)

        # Hint area (hidden by default)
        self.hint_frame = tk.Frame(panel, bg=BG_PANEL2)
        self.hint_frame.pack(fill="x", pady=(8, 0))

        self.lbl_hint = tk.Label(
            self.hint_frame,
            text="",
            bg=BG_PANEL2,
            fg=HINT_COLOR,
            font=tkfont.Font(family="DejaVu Sans", size=10, slant="italic"),
            wraplength=self.WIN_W - 80,
            justify="left",
            anchor="w",
        )
        self.lbl_hint.pack(side="left", fill="x", expand=True)

        self.lbl_hint_penalty = tk.Label(
            self.hint_frame,
            text="",
            bg=BG_PANEL2,
            fg=HINT_PENALTY,
            font=self.font_tiny,
        )
        self.lbl_hint_penalty.pack(side="right")

    # ---------------------------------------------------------------
    # Bottom buttons
    # ---------------------------------------------------------------

    def _build_bottom_buttons(self) -> None:
        btn_frame = tk.Frame(self, bg=BG_DEEP, pady=10)
        btn_frame.pack(fill="x", padx=12)

        # "💡 Indice" button
        self.btn_hint = tk.Button(
            btn_frame,
            text="💡 Indice",
            command=self._toggle_hint,
            bg=BG_PANEL,
            fg=HINT_COLOR,
            activebackground=BORDER_DIM,
            activeforeground=HINT_COLOR,
            font=self.font_body,
            relief="flat",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
        )
        self.btn_hint.pack(side="left", padx=(0, 8))

        # "✓ Vérifier" button
        self.btn_check = tk.Button(
            btn_frame,
            text="✓ Vérifier",
            command=self._manual_check,
            bg=self.theme_color,
            fg=BG_DEEP,
            activebackground=self._lighten(self.theme_color),
            activeforeground=BG_DEEP,
            font=tkfont.Font(family="DejaVu Sans", size=12, weight="bold"),
            relief="flat",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
        )
        self.btn_check.pack(side="right")

        # Status bar at very bottom
        self.lbl_status = tk.Label(
            self,
            text="En attente de ta prochaine action...",
            bg=BG_DEEP,
            fg=TEXT_DIM,
            font=self.font_tiny,
        )
        self.lbl_status.pack(pady=(0, 6))

    # ===================================================================
    # Keyboard bindings
    # ===================================================================

    def _bind_shortcuts(self) -> None:
        # Parent mode: Ctrl+Shift+P
        self.bind("<Control-Shift-P>", self._toggle_parent_mode)
        self.bind("<Control-Shift-p>", self._toggle_parent_mode)
        # Reset idle timer on any interaction
        self.bind_all("<Any-KeyPress>", self._reset_idle)
        self.bind_all("<Any-ButtonPress>", self._reset_idle)

    # ===================================================================
    # UI refresh
    # ===================================================================

    def _refresh_ui(self) -> None:
        """Update all GUI elements to reflect current state."""
        try:
            self._update_progress_stars()
            self._update_mission_panel()
            self._update_status_bar()
        except Exception:  # noqa: BLE001
            logger.error("Error refreshing UI:\n%s", traceback.format_exc())

    def _update_progress_stars(self) -> None:
        completed = self.state.get("completed", [])
        n_done    = len(completed)
        total     = self.total_missions
        level     = self.state.get("current_level", 1)

        stars_str = ""
        for i in range(total):
            if i < n_done:
                stars_str += STAR_DONE
            else:
                stars_str += STAR_TODO

        self.lbl_stars.config(text=stars_str)
        self.lbl_counter.config(
            text=f"Niv. {level}  •  Mission {min(n_done + 1, total)} / {total}"
        )

        # Score label (may lag behind during count-up animation)
        self.lbl_score.config(
            text=f"Score : {self._score_display} pts",
            fg=GOLD if self._score_display > 0 else GOLD_DIM,
        )

    def _update_mission_panel(self) -> None:
        mission_id = self.state.get("current_mission", "")
        if not mission_id:
            return

        self.current_mission = self.mission_loader.load_mission(mission_id)

        title = self.current_mission.get("title", mission_id)
        desc  = self.current_mission.get("description", "")

        self._update_mission_image(self.current_mission)
        self.lbl_mission_title.config(text=title)

        # Update scrollable text
        self.txt_description.config(state="normal")
        self.txt_description.delete("1.0", "end")
        self.txt_description.insert("1.0", desc)
        self.txt_description.config(state="disabled")

        # Update hint (if visible)
        if self.hint_visible:
            self._show_hint_text()

    def _update_mission_image(self, mission: dict) -> None:
        """Load and display the mission image, or hide the panel if none."""
        image_rel = mission.get("image", "")
        if not image_rel or not self._pil_available:
            self._img_label.config(image="")
            self._img_label.pack_forget()
            return

        source_dir = Path(__file__).parent.parent
        image_path = source_dir / image_rel

        if not image_path.exists():
            self._img_label.config(image="")
            self._img_label.pack_forget()
            return

        try:
            from PIL import Image as PILImage, ImageTk
            img = PILImage.open(image_path).resize((460, 200))
            self._current_photo = ImageTk.PhotoImage(img)
            self._img_label.config(image=self._current_photo)
            self._img_label.pack(fill="x", pady=(0, 4), before=self.lbl_mission_title)
        except Exception as e:
            logger.warning("Could not load mission image %s: %s", image_path, e)
            self._img_label.pack_forget()

    def _show_level_complete(self, level_id: int, level_name: str, reward_code: str) -> None:
        """Show a celebratory modal window when a level is completed."""
        win = tk.Toplevel(self)
        win.title(f"Niveau {level_id} terminé !")
        win.configure(bg=BG_DEEP)
        win.resizable(False, False)
        win.attributes("-topmost", True)
        win.geometry("420x340")

        # Centre over parent
        self.update_idletasks()
        px = self.winfo_x() + (self.WIN_W - 420) // 2
        py = self.winfo_y() + (self.WIN_H - 340) // 2
        win.geometry(f"420x340+{px}+{py}")

        # Heading
        tk.Label(
            win,
            text=f"⭐ NIVEAU {level_id} TERMINÉ ! ⭐",
            bg=BG_DEEP,
            fg=GOLD,
            font=tkfont.Font(family="DejaVu Sans", size=17, weight="bold"),
        ).pack(pady=(24, 4))

        # Level name
        tk.Label(
            win,
            text=level_name,
            bg=BG_DEEP,
            fg=self.theme_color,
            font=tkfont.Font(family="DejaVu Sans", size=13, weight="bold"),
        ).pack(pady=(0, 16))

        # Separator
        tk.Frame(win, bg=GOLD, height=1).pack(fill="x", padx=40, pady=(0, 16))

        # Reward code label
        tk.Label(
            win,
            text="Ton code de niveau est :",
            bg=BG_DEEP,
            fg=TEXT_WHITE,
            font=tkfont.Font(family="DejaVu Sans", size=12),
        ).pack()

        # Code box
        code_frame = tk.Frame(win, bg="#1A1500", bd=2, relief="flat",
                              highlightbackground=GOLD, highlightthickness=2)
        code_frame.pack(pady=10, padx=60, fill="x")
        tk.Label(
            code_frame,
            text=reward_code or "???",
            bg="#1A1500",
            fg=GOLD,
            font=tkfont.Font(family="DejaVu Sans Mono", size=18, weight="bold"),
            pady=8,
        ).pack()

        # Next level button
        btn = tk.Button(
            win,
            text="Prêt pour le niveau suivant ? 🚀",
            command=win.destroy,
            bg=self.theme_color,
            fg=BG_DEEP,
            font=tkfont.Font(family="DejaVu Sans", size=12, weight="bold"),
            relief="flat",
            padx=14,
            pady=8,
            cursor="hand2",
        )
        btn.pack(pady=(12, 0))

        # Auto-close after 15 seconds
        win.after(15000, lambda: win.destroy() if win.winfo_exists() else None)

    def _update_status_bar(self) -> None:
        last_check = self.state.get("last_check", "")
        if last_check:
            try:
                dt = datetime.fromisoformat(last_check)
                t = dt.astimezone().strftime("%H:%M:%S")
                self.lbl_status.config(text=f"Dernière vérification : {t}")
            except (ValueError, OSError):
                pass

    # ===================================================================
    # Poll loop (called every 2 s via after())
    # ===================================================================

    def _poll(self) -> None:
        if self._overlay_active or self._final_shown:
            # During overlay, keep rescheduling but don't process
            self.after(2000, self._poll)
            return

        try:
            self._do_poll()
        except Exception:  # noqa: BLE001
            logger.error("Poll error:\n%s", traceback.format_exc())
            self._show_error()

        self.after(2000, self._poll)

    def _do_poll(self) -> None:
        # Refresh state from disk in case of external edit
        self.state = self.state_manager.load()

        # Update last_check timestamp
        self.state["last_check"] = datetime.now(timezone.utc).isoformat()

        if self.state.get("final_reward_unlocked"):
            self.state_manager.save(self.state)
            self._show_final_reward()
            return

        mission_id = self.state.get("current_mission", "")
        if not mission_id:
            self.state_manager.save(self.state)
            return

        mission = self.mission_loader.load_mission(mission_id)
        check_spec = mission.get("check", {"type": "never"})

        # Update runner's state reference
        self.check_runner.state = self.state

        passed = self.check_runner.run(check_spec)

        if passed:
            self._on_mission_complete(mission)
        else:
            self.state_manager.save(self.state)
            self._refresh_ui()

    def _on_mission_complete(self, mission: dict) -> None:
        """Award points, advance mission, show overlay."""
        from engine import notifier

        points = mission.get("points", 10)
        if self.state.get("hints_used", 0) > 0:
            penalty = self.config.get("hint_penalty_points", 5)
            points = max(0, points - penalty * self.state["hints_used"])

        self.state["score"] = self.state.get("score", 0) + points
        mission_id = mission.get("id", self.state.get("current_mission", ""))

        completed: list = self.state.setdefault("completed", [])
        if mission_id not in completed:
            completed.append(mission_id)

        # Determine next mission
        all_missions = self.mission_loader.list_missions()
        try:
            idx = all_missions.index(mission_id)
            next_id = all_missions[idx + 1] if idx + 1 < len(all_missions) else None
        except (ValueError, IndexError):
            next_id = None

        # Detect level transition
        current_level = self.state.get("current_level", 1)
        next_mission_level = current_level  # default

        if next_id:
            try:
                next_mission = self.mission_loader.load_mission(next_id)
                next_mission_level = next_mission.get("level", current_level)
            except Exception:
                pass

            self.state["current_mission"] = next_id
            self.state["mission_start_time"] = datetime.now(timezone.utc).isoformat()
            self.state["hints_used"] = 0

            if next_mission_level > current_level:
                # Level completed — store reward and advance level
                levels_config = self.config.get("levels", [])
                level_config = next(
                    (l for l in levels_config if l["id"] == current_level), {}
                )
                reward = level_config.get("reward", "")
                level_name = level_config.get("name", f"Niveau {current_level}")

                self.state["level_rewards"][str(current_level)] = reward
                if current_level not in self.state.get("completed_levels", []):
                    self.state.setdefault("completed_levels", []).append(current_level)
                self.state["current_level"] = next_mission_level
                self.state_manager.save(self.state)

                self.after(500, lambda lid=current_level, lname=level_name, rwd=reward:
                           self._show_level_complete(lid, lname, rwd))
            else:
                self.state_manager.save(self.state)
        else:
            # All missions done!
            levels_config = self.config.get("levels", [])
            last_level = levels_config[-1] if levels_config else {}
            reward = last_level.get("reward", self.config.get("secret_code", ""))
            level_name = last_level.get("name", "")
            level_id = last_level.get("id", current_level)

            self.state["level_rewards"][str(level_id)] = reward
            if level_id not in self.state.get("completed_levels", []):
                self.state.setdefault("completed_levels", []).append(level_id)
            self.state["current_level"] = level_id
            self.state["final_reward_unlocked"] = True
            self.state["secret_code"] = self.config.get("secret_code", "")

            self.state_manager.save(self.state)

        # Start score animation
        self._score_target = self.state["score"]
        self._animate_score()

        # Notifications & sound
        success_msg = mission.get("success_message", "Bravo !")
        notifier.send_notification(
            f"🎉 Mission accomplie, {self.display_name} !",
            success_msg,
            timeout_ms=6000,
            urgency="normal",
        )
        notifier.play_sound("success")
        notifier.log_event(
            self.player_name, "MISSION_COMPLETE",
            f"mission={mission_id} points={points} score={self.state['score']}"
        )

        # Show success overlay
        self._show_success_overlay(success_msg, points)
        self.hint_visible = False

    # ===================================================================
    # Manual check (Vérifier button)
    # ===================================================================

    def _manual_check(self) -> None:
        self._reset_idle()
        if self._overlay_active or self._final_shown:
            return
        self._do_poll()

    # ===================================================================
    # Hint toggle
    # ===================================================================

    def _toggle_hint(self) -> None:
        self._reset_idle()
        from engine import notifier

        if not self.hint_visible:
            self.hint_visible = True
            # Increment hints_used only the first time per mission
            already_penalised = self.state.get("hints_used", 0) > 0
            if not already_penalised:
                self.state["hints_used"] = self.state.get("hints_used", 0) + 1
                self.state_manager.save(self.state)
                notifier.log_event(self.player_name, "HINT_USED",
                                   self.state.get("current_mission", ""))
            self._show_hint_text()
        else:
            self.hint_visible = False
            self.lbl_hint.config(text="")
            self.lbl_hint_penalty.config(text="")

    def _show_hint_text(self) -> None:
        hint = self.current_mission.get("hint", "Pas d'indice disponible.")
        self.lbl_hint.config(text=f"💡 {hint}")
        penalty = self.config.get("hint_penalty_points", 5)
        self.lbl_hint_penalty.config(text=f"(-{penalty} pts)")

    # ===================================================================
    # Animations
    # ===================================================================

    # ---- Star twinkling ----

    def _animate_stars(self) -> None:
        """Cycle through twinkle phases for selected stars."""
        for star in self._stars:
            if not star["twinkle"]:
                continue
            star["phase"] = (star["phase"] + star["speed"]) % math.tau
            brightness = 0.55 + 0.45 * math.sin(star["phase"])
            c = self._dim_white(brightness)
            try:
                self.star_canvas.itemconfig(star["id"], fill=c)
            except tk.TclError:
                pass
        self.after(80, self._animate_stars)

    @staticmethod
    def _dim_white(factor: float) -> str:
        v = int(255 * max(0.0, min(1.0, factor)))
        return f"#{v:02x}{v:02x}{min(255, v + 20):02x}"

    # ---- Drifting particles ----

    def _animate_drifters(self) -> None:
        """Move subtle drifting particles across the star canvas."""
        for d in self._drifters:
            d["x"] = (d["x"] + d["vx"]) % self.WIN_W
            d["y"] = (d["y"] + d["vy"]) % 130
            try:
                self.star_canvas.coords(
                    d["id"],
                    d["x"], d["y"], d["x"] + 1, d["y"] + 1,
                )
            except tk.TclError:
                pass
        self.after(60, self._animate_drifters)

    # ---- Score count-up ----

    def _animate_score(self) -> None:
        """Smoothly count up the displayed score."""
        if self._score_display < self._score_target:
            step = max(1, (self._score_target - self._score_display) // 6)
            self._score_display = min(self._score_display + step, self._score_target)
            self.lbl_score.config(text=f"Score : {self._score_display} pts", fg=GOLD)
            self.after(SCORE_ANIM_MS, self._animate_score)
        else:
            self._score_display = self._score_target
            self.lbl_score.config(text=f"Score : {self._score_display} pts", fg=GOLD)

    # ---- Idle pulse ----

    def _start_idle_timer(self) -> None:
        if self._idle_job:
            self.after_cancel(self._idle_job)
        self._idle_job = self.after(IDLE_TIMEOUT_MS, self._start_pulse)

    def _reset_idle(self, _event=None) -> None:
        self._stop_pulse()
        self._start_idle_timer()

    def _start_pulse(self) -> None:
        self._pulse_phase = 0.0
        self._do_pulse()

    def _do_pulse(self) -> None:
        if self._final_shown or self._overlay_active:
            return
        self._pulse_phase = (self._pulse_phase + 0.08) % math.tau
        factor = 0.7 + 0.3 * math.sin(self._pulse_phase)
        r, g, b = self._hex_to_rgb(self.theme_color)
        pulsed = f"#{int(r*factor):02x}{int(g*factor):02x}{int(b*factor):02x}"
        try:
            self.lbl_mission_title.config(fg=pulsed)
        except tk.TclError:
            return
        self._pulse_job = self.after(60, self._do_pulse)

    def _stop_pulse(self) -> None:
        if self._pulse_job:
            self.after_cancel(self._pulse_job)
            self._pulse_job = None
        try:
            self.lbl_mission_title.config(fg=self.theme_color)
        except tk.TclError:
            pass

    # ===================================================================
    # Success overlay
    # ===================================================================

    def _show_success_overlay(self, message: str, points: int) -> None:
        self._overlay_active = True
        self._stop_pulse()

        overlay = tk.Toplevel(self)
        overlay.overrideredirect(True)
        overlay.configure(bg=SUCCESS_BG)
        overlay.attributes("-topmost", True)

        # Position over our window
        self.update_idletasks()
        ox = self.winfo_x()
        oy = self.winfo_y()
        overlay.geometry(f"{self.WIN_W}x{self.WIN_H}+{ox}+{oy}")

        # Falling stars canvas
        canvas = tk.Canvas(
            overlay,
            width=self.WIN_W,
            height=self.WIN_H,
            bg=SUCCESS_BG,
            highlightthickness=0,
        )
        canvas.pack(fill="both", expand=True)

        # Central message
        cx, cy = self.WIN_W // 2, self.WIN_H // 2 - 30
        canvas.create_text(
            cx, cy - 60,
            text="🎉",
            font=tkfont.Font(family="DejaVu Sans", size=48),
            fill=GOLD,
        )
        canvas.create_text(
            cx, cy,
            text="Mission accomplie !",
            font=tkfont.Font(family="DejaVu Sans", size=22, weight="bold"),
            fill=GOLD,
        )
        canvas.create_text(
            cx, cy + 48,
            text=message,
            font=tkfont.Font(family="DejaVu Sans", size=13),
            fill=TEXT_WHITE,
            width=self.WIN_W - 60,
        )
        canvas.create_text(
            cx, cy + 100,
            text=f"+{points} points !",
            font=tkfont.Font(family="DejaVu Sans", size=18, weight="bold"),
            fill=GOLD,
        )

        # Falling stars
        falling: list[dict] = []
        for _ in range(30):
            x = random.randint(10, self.WIN_W - 10)
            y = random.randint(-60, -5)
            cid = canvas.create_text(
                x, y,
                text=random.choice(["★", "✦", "✧", "✨"]),
                font=tkfont.Font(family="DejaVu Sans", size=random.randint(10, 22)),
                fill=random.choice([GOLD, "#FFFACD", self.theme_color]),
            )
            falling.append({
                "id": cid, "x": x, "y": y,
                "vy": random.uniform(2.5, 6.0),
                "rot": random.uniform(-3, 3),
            })

        def _fall_step():
            for star in falling:
                star["y"] += star["vy"]
                try:
                    canvas.coords(star["id"], star["x"], star["y"])
                except tk.TclError:
                    pass

        _fall_handle = [None]

        def _fall_loop():
            _fall_step()
            _fall_handle[0] = canvas.after(30, _fall_loop)

        _fall_loop()

        def _close_overlay():
            if _fall_handle[0]:
                try:
                    canvas.after_cancel(_fall_handle[0])
                except tk.TclError:
                    pass
            overlay.destroy()
            self._overlay_active = False
            # Refresh underlying window
            self._refresh_ui()
            if self.state.get("final_reward_unlocked"):
                self.after(300, self._show_final_reward)
            else:
                self._start_idle_timer()

        self.after(3000, _close_overlay)

    # ===================================================================
    # Final reward screen
    # ===================================================================

    def _show_final_reward(self) -> None:
        if self._final_shown:
            return
        self._final_shown = True
        self._stop_pulse()

        from engine import notifier
        notifier.play_sound("unlock")
        notifier.log_event(self.player_name, "FINAL_REWARD", "all missions complete")

        # Destroy normal content
        for widget in self.winfo_children():
            widget.destroy()

        self.configure(bg=FINAL_BG)

        # Main canvas for the celebration
        canvas = tk.Canvas(
            self,
            width=self.WIN_W,
            height=self.WIN_H,
            bg=FINAL_BG,
            highlightthickness=0,
        )
        canvas.pack(fill="both", expand=True)

        cx = self.WIN_W // 2
        secret_code = self.state.get("secret_code") or self.config.get("secret_code", "???")

        # Trophy
        canvas.create_text(cx, 55, text="🏆", font=tkfont.Font(family="DejaVu Sans", size=48))

        # Main heading
        canvas.create_text(
            cx, 115,
            text="MISSION ACCOMPLIE !",
            font=tkfont.Font(family="DejaVu Sans", size=20, weight="bold"),
            fill=GOLD,
        )

        # Player name
        canvas.create_text(
            cx, 150,
            text=f"{self.role_title} {self.display_name.upper()}",
            font=tkfont.Font(family="DejaVu Sans", size=14, weight="bold"),
            fill=self.theme_color,
        )

        # Score
        score = self.state.get("score", 0)
        canvas.create_text(
            cx, 180,
            text=f"Score final : {score} points",
            font=tkfont.Font(family="DejaVu Sans", size=11),
            fill=GOLD_DIM,
        )

        # Separator
        canvas.create_line(40, 205, self.WIN_W - 40, 205, fill=GOLD_DIM, width=1)

        # Code label
        canvas.create_text(
            cx, 235,
            text="Ton code secret est :",
            font=tkfont.Font(family="DejaVu Sans", size=13),
            fill=TEXT_WHITE,
        )

        # Secret code — large, bold, gold, in a box
        box_x1, box_y1 = 60, 255
        box_x2, box_y2 = self.WIN_W - 60, 305
        canvas.create_rectangle(
            box_x1, box_y1, box_x2, box_y2,
            fill="#1A1500", outline=GOLD, width=2,
        )
        canvas.create_text(
            cx, (box_y1 + box_y2) // 2,
            text=secret_code,
            font=tkfont.Font(family="DejaVu Sans Mono", size=19, weight="bold"),
            fill=GOLD,
        )

        # Call-to-action
        canvas.create_text(
            cx, 330,
            text="Va voir Papa pour ton cadeau ! 🎁",
            font=tkfont.Font(family="DejaVu Sans", size=13, weight="bold"),
            fill=self.theme_color,
        )

        # Firework / star burst particles
        fw_particles: list[dict] = []

        def _burst(bx: int, by: int, color: str, n: int = 18) -> None:
            for i in range(n):
                angle = math.tau * i / n + random.uniform(-0.2, 0.2)
                speed = random.uniform(1.5, 5.0)
                cid = canvas.create_oval(
                    bx - 2, by - 2, bx + 2, by + 2,
                    fill=color, outline="",
                )
                fw_particles.append({
                    "id": cid,
                    "x": float(bx), "y": float(by),
                    "vx": math.cos(angle) * speed,
                    "vy": math.sin(angle) * speed,
                    "life": 1.0,
                    "decay": random.uniform(0.015, 0.035),
                })

        # Schedule bursts
        burst_colors = [GOLD, self.theme_color, "#FF6B9D", "#80CBC4", "#FFFACD"]
        burst_positions = [
            (cx - 120, 390), (cx + 120, 390), (cx, 420),
            (cx - 60, 460), (cx + 60, 460),
            (cx - 150, 500), (cx + 150, 500), (cx, 490),
        ]

        def _schedule_burst(idx: int = 0) -> None:
            if idx < len(burst_positions):
                bx, by = burst_positions[idx]
                color = burst_colors[idx % len(burst_colors)]
                _burst(bx, by, color)
                canvas.after(350, lambda: _schedule_burst(idx + 1))

        canvas.after(200, _schedule_burst)

        # Also scatter raining stars from top
        raining: list[dict] = []
        for _ in range(25):
            x = random.randint(5, self.WIN_W - 5)
            cid = canvas.create_text(
                x, random.randint(-40, -5),
                text=random.choice(["★", "✦", "✧"]),
                font=tkfont.Font(family="DejaVu Sans", size=random.randint(8, 16)),
                fill=random.choice([GOLD, self.theme_color, "#FFFACD"]),
            )
            raining.append({
                "id": cid, "x": x,
                "y": random.uniform(-40, -5),
                "vy": random.uniform(0.8, 2.2),
            })

        def _anim_final() -> None:
            # Rain
            for r in raining:
                r["y"] = (r["y"] + r["vy"])
                if r["y"] > self.WIN_H + 20:
                    r["y"] = random.uniform(-40, -5)
                    r["x"] = random.randint(5, self.WIN_W - 5)
                try:
                    canvas.coords(r["id"], r["x"], r["y"])
                except tk.TclError:
                    pass

            # Firework particles
            dead = []
            for p in fw_particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                p["vy"] += 0.12  # gravity
                p["life"] -= p["decay"]
                if p["life"] <= 0:
                    dead.append(p)
                    try:
                        canvas.delete(p["id"])
                    except tk.TclError:
                        pass
                else:
                    try:
                        s = max(1, int(p["life"] * 3))
                        canvas.coords(
                            p["id"],
                            p["x"] - s, p["y"] - s,
                            p["x"] + s, p["y"] + s,
                        )
                    except tk.TclError:
                        pass
            for p in dead:
                fw_particles.remove(p)

            try:
                canvas.after(30, _anim_final)
            except tk.TclError:
                pass

        canvas.after(30, _anim_final)

    # ===================================================================
    # Parent mode
    # ===================================================================

    def _toggle_parent_mode(self, _event=None) -> None:
        self._parent_mode = not self._parent_mode
        if self._parent_mode:
            self._show_parent_panel()

    def _show_parent_panel(self) -> None:
        win = tk.Toplevel(self)
        win.title("Mode Parent — État du jeu")
        win.configure(bg=BG_DEEP)
        win.resizable(True, True)
        win.geometry("520x400")
        win.attributes("-topmost", True)

        import json as _json

        title = tk.Label(
            win,
            text="🔒 Mode Parent",
            bg=BG_DEEP,
            fg=self.theme_color,
            font=self.font_title,
        )
        title.pack(pady=(10, 4))

        frame = tk.Frame(win, bg=BG_PANEL)
        frame.pack(fill="both", expand=True, padx=10, pady=6)

        sb = tk.Scrollbar(frame)
        sb.pack(side="right", fill="y")

        txt = tk.Text(
            frame,
            bg=BG_PANEL,
            fg=TEXT_WHITE,
            font=tkfont.Font(family="DejaVu Sans Mono", size=9),
            relief="flat",
            yscrollcommand=sb.set,
            wrap="word",
        )
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)

        state_json = _json.dumps(self.state, indent=2, ensure_ascii=False)
        config_json = _json.dumps(self.config, indent=2, ensure_ascii=False)
        content = f"=== ÉTAT ===\n{state_json}\n\n=== CONFIG ===\n{config_json}"
        txt.insert("1.0", content)
        txt.config(state="disabled")

        def _close():
            self._parent_mode = False
            win.destroy()

        tk.Button(
            win, text="Fermer", command=_close,
            bg=self.theme_color, fg=BG_DEEP,
            font=self.font_small, relief="flat", padx=10, pady=4,
        ).pack(pady=8)

        win.protocol("WM_DELETE_WINDOW", _close)

    # ===================================================================
    # Help panel
    # ===================================================================

    def _show_help(self) -> None:
        win = tk.Toplevel(self)
        win.title("Aide — Raccourcis")
        win.configure(bg=BG_DEEP)
        win.resizable(False, False)
        win.geometry("340x240")
        win.attributes("-topmost", True)

        tk.Label(
            win,
            text="⌨️ Raccourcis clavier",
            bg=BG_DEEP,
            fg=self.theme_color,
            font=self.font_title,
        ).pack(pady=(12, 6))

        shortcuts = [
            ("Ctrl+Shift+P", "Mode Parent (voir l'état)"),
            ("💡 Indice",     "Afficher / cacher l'indice"),
            ("✓ Vérifier",   "Vérifier maintenant"),
            ("❓",            "Cette fenêtre d'aide"),
        ]

        for key, desc in shortcuts:
            row = tk.Frame(win, bg=BG_DEEP)
            row.pack(fill="x", padx=16, pady=3)
            tk.Label(
                row,
                text=key,
                bg=BG_PANEL,
                fg=GOLD,
                font=self.font_small,
                width=16,
                anchor="w",
                padx=4,
                pady=2,
            ).pack(side="left")
            tk.Label(
                row,
                text=desc,
                bg=BG_DEEP,
                fg=TEXT_WHITE,
                font=self.font_small,
            ).pack(side="left", padx=8)

        tk.Button(
            win, text="OK", command=win.destroy,
            bg=self.theme_color, fg=BG_DEEP,
            font=self.font_small, relief="flat", padx=12, pady=4,
        ).pack(pady=12)

    # ===================================================================
    # Error display
    # ===================================================================

    def _show_error(self) -> None:
        """Show a friendly, non-scary error message to the kids."""
        try:
            self.lbl_status.config(
                text="Oups, erreur ! Appelle Papa. 🛸",
                fg=HINT_PENALTY,
            )
        except tk.TclError:
            pass

    # ===================================================================
    # Utility
    # ===================================================================

    @staticmethod
    def _lighten(hex_color: str, factor: float = 0.25) -> str:
        """Return a lighter version of a hex colour."""
        r, g, b = MissionWindow._hex_to_rgb(hex_color)
        r2 = int(r + (255 - r) * factor)
        g2 = int(g + (255 - g) * factor)
        b2 = int(b + (255 - b) * factor)
        return f"#{r2:02x}{g2:02x}{b2:02x}"

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
        h = hex_color.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
