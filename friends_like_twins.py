import difflib
import re
import sys

import pygame


pygame.init()

WIDTH, HEIGHT = 1000, 700
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Friends Like Twins")
CLOCK = pygame.time.Clock()
FPS = 60

# Colors
BACKGROUND = (245, 242, 255)
PANEL = (255, 255, 255)
PURPLE = (105, 76, 180)
PURPLE_DARK = (72, 48, 135)
PINK = (235, 104, 160)
BLUE = (83, 150, 220)
GREEN = (73, 170, 115)
TEXT = (45, 42, 55)
MUTED = (110, 105, 125)
BORDER = (215, 207, 235)
WHITE = (255, 255, 255)

FONT_SMALL = pygame.font.SysFont("arial", 22)
FONT_TINY = pygame.font.SysFont("arial", 20)
FONT_MEDIUM = pygame.font.SysFont("arial", 30, bold=True)
FONT_LARGE = pygame.font.SysFont("arial", 48, bold=True)
FONT_TITLE = pygame.font.SysFont("arial", 62, bold=True)

QUESTIONS = [
    {
        "key": "color",
        "prompt": "What is your favorite color?",
        "type": "choice",
        "options": ["Red", "Blue", "Green", "Yellow", "Purple", "Pink"],
    },
    {
        "key": "activity",
        "prompt": "What is your favorite activity?",
        "type": "choice",
        "options": ["Swimming", "Football", "Gaming", "Drawing", "Reading", "Dancing"],
    },
    {
        "key": "country",
        "prompt": "What is your favorite country?",
        "type": "text",
        "placeholder": "Example: Morocco",
    },
    {
        "key": "city",
        "prompt": "What is your favorite city?",
        "type": "text",
        "placeholder": "Example: Rabat",
    },
    {
        "key": "free_time",
        "prompt": "What do you prefer in your free time?",
        "type": "choice",
        "options": [
            "Stay at home",
            "Practice a sport",
            "Go outside",
            "Meet friends",
            "Watch movies",
            "Make something",
        ],
    },
    {
        "key": "learning",
        "prompt": "What new thing would you like to learn?",
        "type": "choice",
        "options": [
            "A new language",
            "A new sport",
            "Music",
            "Programming",
            "Cooking",
            "Art",
        ],
    },
    {
        "key": "future",
        "prompt": "What do you want to be in the future?",
        "type": "text",
        "placeholder": "Example: Doctor, engineer, artist...",
    },
    {
        "key": "food",
        "prompt": "What is your favorite food?",
        "type": "text",
        "placeholder": "Example: Pizza, couscous, tacos...",
    },
    {
        "key": "music",
        "prompt": "What music do you enjoy most?",
        "type": "choice",
        "options": ["Pop", "Rap", "Rock", "Classical", "Amazigh", "No music"],
    },
    {
        "key": "happy_place",
        "prompt": "Where do you feel happiest?",
        "type": "choice",
        "options": [
            "At home",
            "At school",
            "With family",
            "With friends",
            "Outside",
            "By the sea",
        ],
    },
]


def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    SCREEN.blit(surface, rect)
    return rect


def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current = ""

    for word in words:
        test = word if not current else current + " " + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def draw_wrapped_text(text, font, color, x, y, max_width, line_gap=6, center=False):
    lines = wrap_text(text, font, max_width)
    current_y = y

    for line in lines:
        if center:
            draw_text(line, font, color, x, current_y, center=True)
        else:
            draw_text(line, font, color, x, current_y)
        current_y += font.get_height() + line_gap


def draw_heart(x, y, size, color):
    radius = size // 4
    pygame.draw.circle(SCREEN, color, (x - radius, y - radius // 2), radius)
    pygame.draw.circle(SCREEN, color, (x + radius, y - radius // 2), radius)
    points = [
        (x - size // 2, y - radius // 2),
        (x + size // 2, y - radius // 2),
        (x, y + size // 2),
    ]
    pygame.draw.polygon(SCREEN, color, points)


class Button:
    def __init__(self, rect, text, color=PURPLE, text_color=WHITE):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, selected=False):
        mouse_over = self.rect.collidepoint(pygame.mouse.get_pos())
        color = self.color

        if selected:
            color = PINK
        elif mouse_over:
            color = tuple(max(0, value - 15) for value in self.color)

        pygame.draw.rect(SCREEN, color, self.rect, border_radius=16)
        draw_text(
            self.text,
            FONT_SMALL,
            self.text_color,
            self.rect.centerx,
            self.rect.centery,
            center=True,
        )

    def clicked(self, event):
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class TextBox:
    def __init__(self, rect, placeholder="", max_length=30):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.max_length = max_length

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "submit"
            elif event.unicode.isprintable() and len(self.text) < self.max_length:
                self.text += event.unicode

        return None

    def draw(self):
        border_color = PURPLE if self.active else BORDER
        pygame.draw.rect(SCREEN, PANEL, self.rect, border_radius=14)
        pygame.draw.rect(SCREEN, border_color, self.rect, width=3, border_radius=14)

        shown_text = self.text if self.text else self.placeholder
        shown_color = TEXT if self.text else MUTED
        draw_text(
            shown_text,
            FONT_SMALL,
            shown_color,
            self.rect.x + 16,
            self.rect.centery - FONT_SMALL.get_height() // 2,
        )


def normalize_answer(answer):
    answer = answer.lower().strip()
    answer = re.sub(r"[^a-z0-9]+", "", answer)
    return answer


def answers_match(real_answer, guessed_answer, question_type):
    real = normalize_answer(real_answer)
    guessed = normalize_answer(guessed_answer)

    if not real or not guessed:
        return False

    if question_type == "choice":
        return real == guessed

    # Text answers accept small spelling differences.
    return difflib.SequenceMatcher(None, real, guessed).ratio() >= 0.82


def format_score(score):
    if score == int(score):
        return str(int(score))
    return f"{score:.1f}"


def friendship_paragraph(players, percentage):
    first, second = players

    if percentage >= 85:
        return (
            f"{first} and {second} are friends who truly pay attention to each other. "
            "They remember the little things, understand each other's choices, "
            "and make their friendship feel warm and trusted."
        )
    if percentage >= 65:
        return (
            f"{first} and {second} know many sweet and important things about each other. "
            "Their friendship is growing with every answer, every laugh, "
            "and every moment they share together."
        )
    if percentage >= 40:
        return (
            f"{first} and {second} have a friendship with many nice things still to discover. "
            "When they ask more questions and listen with care, "
            "they can become even closer."
        )

    return (
        f"{first} and {second} are at the start of learning each other's world. "
        "A good friendship grows slowly with honest answers, kind words, "
        "and more time spent together."
    )


class FriendsLikeTwinsGame:
    def __init__(self):
        self.state = "welcome"
        self.players = ["", ""]
        self.name_boxes = [
            TextBox((250, 290, 500, 58), "Friend 1 name"),
            TextBox((250, 380, 500, 58), "Friend 2 name"),
        ]

        self.real_answers = [{}, {}]
        self.guesses = [{}, {}]

        self.phase_index = 0
        self.question_index = 0
        self.selected_choice = None
        self.answer_box = TextBox((210, 400, 580, 62), "", max_length=40)

        # Each friend answers about themselves, then the other friend guesses.
        self.phases = [
            {"answerer": 0, "target": 0, "mode": "real"},
            {"answerer": 1, "target": 0, "mode": "guess"},
            {"answerer": 1, "target": 1, "mode": "real"},
            {"answerer": 0, "target": 1, "mode": "guess"},
        ]

        self.start_button = Button((350, 475, 300, 70), "Start")
        self.names_button = Button((350, 500, 300, 65), "Continue")
        self.next_button = Button((370, 575, 260, 62), "Next")
        self.restart_button = Button((350, 630, 300, 52), "Play Again")

    def reset(self):
        self.__init__()

    def current_phase(self):
        return self.phases[self.phase_index]

    def current_question(self):
        return QUESTIONS[self.question_index]

    def phase_title(self):
        phase = self.current_phase()
        answerer = self.players[phase["answerer"]]
        target = self.players[phase["target"]]

        if phase["mode"] == "real":
            return f"{answerer}, answer about yourself"
        return f"{answerer}, guess {target}'s answer"

    def save_current_answer(self):
        question = self.current_question()
        phase = self.current_phase()

        if question["type"] == "choice":
            answer = self.selected_choice
        else:
            answer = self.answer_box.text.strip()

        if not answer:
            return False

        target = phase["target"]
        if phase["mode"] == "real":
            self.real_answers[target][question["key"]] = answer
        else:
            self.guesses[target][question["key"]] = answer

        self.question_index += 1
        self.selected_choice = None
        self.answer_box.text = ""
        self.answer_box.active = False

        if self.question_index >= len(QUESTIONS):
            self.question_index = 0
            self.phase_index += 1

            if self.phase_index >= len(self.phases):
                self.state = "results"
            else:
                self.state = "pass"

        return True

    def get_scores(self):
        round_scores = []
        detailed_results = []

        for target in range(2):
            score = 0
            details = []

            for question in QUESTIONS:
                real_answer = self.real_answers[target].get(question["key"], "")
                guessed_answer = self.guesses[target].get(question["key"], "")
                matched = answers_match(real_answer, guessed_answer, question["type"])
                if matched:
                    score += 1

                details.append(
                    {
                        "prompt": question["prompt"],
                        "real": real_answer,
                        "guess": guessed_answer,
                        "matched": matched,
                    }
                )

            round_scores.append(score)
            detailed_results.append(details)

        return round_scores, detailed_results

    def handle_event(self, event):
        if self.state == "welcome":
            if self.start_button.clicked(event):
                self.state = "names"

        elif self.state == "names":
            for box in self.name_boxes:
                box.handle_event(event)

            if self.names_button.clicked(event):
                first = self.name_boxes[0].text.strip()
                second = self.name_boxes[1].text.strip()

                if first and second:
                    self.players = [first, second]
                    self.state = "pass"

        elif self.state == "pass":
            if self.start_button.clicked(event):
                self.state = "question"

        elif self.state == "question":
            question = self.current_question()

            if question["type"] == "choice":
                for option, button in self.get_option_buttons():
                    if button.clicked(event):
                        self.selected_choice = option
            else:
                result = self.answer_box.handle_event(event)
                if result == "submit":
                    self.save_current_answer()

            if self.next_button.clicked(event):
                self.save_current_answer()

        elif self.state == "results":
            if self.restart_button.clicked(event):
                self.reset()

    def get_option_buttons(self):
        question = self.current_question()
        buttons = []

        for index, option in enumerate(question.get("options", [])):
            col = index % 2
            row = index // 2
            x = 180 + col * 340
            y = 345 + row * 72
            button = Button((x, y, 300, 56), option, BLUE)
            buttons.append((option, button))

        return buttons

    def draw_background(self):
        SCREEN.fill(BACKGROUND)
        pygame.draw.circle(SCREEN, (230, 220, 252), (80, 70), 95)
        pygame.draw.circle(SCREEN, (255, 222, 238), (920, 640), 130)
        draw_heart(900, 80, 54, PINK)
        draw_heart(115, 620, 40, PURPLE)

    def draw_header(self):
        draw_text("Friends Like Twins", FONT_MEDIUM, PURPLE_DARK, 36, 26)
        pygame.draw.line(SCREEN, BORDER, (36, 72), (964, 72), 2)

    def draw_welcome(self):
        self.draw_background()
        draw_heart(500, 135, 90, PINK)
        draw_text("Friends Like Twins", FONT_TITLE, PURPLE_DARK, 500, 245, center=True)
        draw_text(
            "Discover how well your friend knows you, out of 10!",
            FONT_SMALL,
            MUTED,
            500,
            315,
            center=True,
        )

        pygame.draw.rect(SCREEN, PANEL, (235, 360, 530, 80), border_radius=18)
        draw_text(
            "Answer, guess, compare, and read a sweet friendship paragraph.",
            FONT_SMALL,
            TEXT,
            500,
            400,
            center=True,
        )
        self.start_button.text = "Start"
        self.start_button.draw()

    def draw_names(self):
        self.draw_background()
        self.draw_header()
        draw_text("Enter the players' names", FONT_LARGE, TEXT, 500, 160, center=True)
        draw_text(
            "Two friends will answer and guess each other's preferences.",
            FONT_SMALL,
            MUTED,
            500,
            215,
            center=True,
        )

        for box in self.name_boxes:
            box.draw()

        self.names_button.draw()
        draw_text(
            "Click a box to type. Both names are required.",
            FONT_SMALL,
            MUTED,
            500,
            590,
            center=True,
        )

    def draw_pass_screen(self):
        self.draw_background()
        self.draw_header()

        phase = self.current_phase()
        answerer = self.players[phase["answerer"]]
        target = self.players[phase["target"]]

        draw_text("Pass the computer", FONT_LARGE, PURPLE_DARK, 500, 170, center=True)

        if phase["mode"] == "real":
            message = f"Only {answerer} should look at the screen now."
            instruction = "Answer honestly about yourself."
        else:
            message = f"Only {answerer} should look at the screen now."
            instruction = f"Try to guess what {target} answered."

        draw_wrapped_text(message, FONT_MEDIUM, TEXT, 500, 280, 680, center=True)
        draw_text(instruction, FONT_SMALL, MUTED, 500, 350, center=True)

        self.start_button.text = "I am ready"
        self.start_button.draw()

    def draw_progress(self):
        progress = (self.question_index + 1) / len(QUESTIONS)
        x, y, w, h = 170, 255, 660, 14

        pygame.draw.rect(SCREEN, BORDER, (x, y, w, h), border_radius=7)
        pygame.draw.rect(SCREEN, PURPLE, (x, y, int(w * progress), h), border_radius=7)

        draw_text(
            f"Question {self.question_index + 1} of {len(QUESTIONS)}",
            FONT_SMALL,
            MUTED,
            500,
            225,
            center=True,
        )

    def draw_question(self):
        self.draw_background()
        self.draw_header()
        draw_text(self.phase_title(), FONT_MEDIUM, PURPLE_DARK, 500, 125, center=True)
        self.draw_progress()

        question = self.current_question()
        draw_wrapped_text(
            question["prompt"],
            FONT_LARGE,
            TEXT,
            500,
            310,
            780,
            line_gap=4,
            center=True,
        )

        if question["type"] == "choice":
            for option, button in self.get_option_buttons():
                button.draw(selected=(option == self.selected_choice))
        else:
            self.answer_box.placeholder = question.get("placeholder", "Type your answer")
            self.answer_box.draw()

        self.next_button.draw()

    def draw_results(self):
        self.draw_background()
        self.draw_header()

        round_scores, details = self.get_scores()
        total_score = sum(round_scores)
        max_score = len(QUESTIONS) * 2
        percentage = round((total_score / max_score) * 100)
        friendship_score = round((total_score / max_score) * 10, 1)

        if percentage >= 85:
            title = "Almost Twins!"
            message = "You know each other extremely well."
        elif percentage >= 65:
            title = "Great Friends!"
            message = "You know many important things about each other."
        elif percentage >= 40:
            title = "Good Start!"
            message = "Keep talking and discovering new things together."
        else:
            title = "Time to Learn More!"
            message = "Ask more questions and play again later."

        description = friendship_paragraph(self.players, percentage)

        draw_text(title, FONT_LARGE, PURPLE_DARK, 500, 120, center=True)
        draw_text(message, FONT_SMALL, MUTED, 500, 170, center=True)

        pygame.draw.rect(SCREEN, PANEL, (115, 205, 770, 110), border_radius=20)
        draw_text(
            f"{format_score(friendship_score)} / 10",
            FONT_TITLE,
            PINK,
            500,
            247,
            center=True,
        )
        draw_text(
            f"Friendship points: {total_score} / {max_score} correct guesses",
            FONT_SMALL,
            TEXT,
            500,
            290,
            center=True,
        )

        cards = [
            (145, f"{self.players[0]} guessed {self.players[1]}", round_scores[1]),
            (525, f"{self.players[1]} guessed {self.players[0]}", round_scores[0]),
        ]

        for x, label, score in cards:
            pygame.draw.rect(SCREEN, PANEL, (x, 345, 330, 150), border_radius=18)
            draw_wrapped_text(label, FONT_SMALL, TEXT, x + 165, 380, 285, center=True)
            draw_text(
                f"{score} / {len(QUESTIONS)}",
                FONT_LARGE,
                GREEN if score >= 7 else BLUE,
                x + 165,
                445,
                center=True,
            )

        matches = sum(
            1 for player_details in details for item in player_details if item["matched"]
        )
        draw_text(
            f"Correct guesses: {matches}    |    Missed guesses: {max_score - matches}",
            FONT_TINY,
            MUTED,
            500,
            512,
            center=True,
        )

        draw_text(
            "Friendship paragraph",
            FONT_TINY,
            PINK,
            500,
            542,
            center=True,
        )

        draw_wrapped_text(
            description,
            FONT_TINY,
            PURPLE_DARK,
            500,
            570,
            830,
            line_gap=2,
            center=True,
        )

        self.restart_button.draw()

    def draw(self):
        if self.state == "welcome":
            self.draw_welcome()
        elif self.state == "names":
            self.draw_names()
        elif self.state == "pass":
            self.draw_pass_screen()
        elif self.state == "question":
            self.draw_question()
        elif self.state == "results":
            self.draw_results()

        pygame.display.flip()

    def run(self):
        while True:
            CLOCK.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.handle_event(event)

            self.draw()


if __name__ == "__main__":
    FriendsLikeTwinsGame().run()
