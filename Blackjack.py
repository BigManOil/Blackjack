import pygame
import sys
import random
import math
from typing import List, Optional, Tuple
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 580
CARD_WIDTH = 100
CARD_HEIGHT = 140
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 50
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 100, 0)
RED = (220, 0, 0)
BLUE = (0, 0, 220)
GOLD = (255, 215, 0)

# Fonts
FONT = pygame.font.Font(None, 36)
CARD_FONT = pygame.font.Font(None, 50)

class Suit(Enum):
    HEARTS = "H"
    DIAMONDS = "D"
    CLUBS = "C"
    SPADES = "S"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank
        self.image = self.load_image()
        self.pos = (0, 0)
        self.target_pos = (0, 0)
        self.angle = 0
        self.target_angle = 0

    def load_image(self) -> pygame.Surface:
        surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        surface.fill(WHITE)
        pygame.draw.rect(surface, BLACK, surface.get_rect(), 2)
        
        rank_text = CARD_FONT.render(self.rank.name[0], True, BLACK)
        suit_text = CARD_FONT.render(self.suit.value, True, RED if self.suit in [Suit.HEARTS, Suit.DIAMONDS] else BLACK)
        
        surface.blit(rank_text, (10, 10))
        surface.blit(suit_text, (CARD_WIDTH - 30, CARD_HEIGHT - 40))
        
        # Add some decoration
        pygame.draw.rect(surface, GOLD, (5, 5, CARD_WIDTH - 10, CARD_HEIGHT - 10), 2)
        
        return surface

    def get_value(self) -> int:
        return min(self.rank.value, 10)

    def update(self):
        # Smoothly move the card to its target position
        self.pos = (self.pos[0] * 0.9 + self.target_pos[0] * 0.1,
                    self.pos[1] * 0.9 + self.target_pos[1] * 0.1)
        # Smoothly rotate the card to its target angle
        self.angle = self.angle * 0.9 + self.target_angle * 0.1

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        new_rect = rotated_image.get_rect(center=self.image.get_rect(topleft=self.pos).center)
        screen.blit(rotated_image, new_rect.topleft)

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self.build()

    def build(self) -> None:
        self.cards = [Card(suit, rank) for suit in Suit for rank in Rank]

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def deal(self) -> Optional[Card]:
        return self.cards.pop() if self.cards else None

class Player:
    def __init__(self, name: str, is_dealer: bool = False):
        self.name = name
        self.hand: List[Card] = []
        self.is_dealer = is_dealer
        self.chips = 1000 if not is_dealer else 0

    def add_card(self, card: Card) -> None:
        self.hand.append(card)

    def clear_hand(self) -> None:
        self.hand.clear()

    def get_hand_value(self) -> int:
        value = sum(card.get_value() for card in self.hand)
        num_aces = sum(1 for card in self.hand if card.rank == Rank.ACE)

        while value > 21 and num_aces:
            value -= 10
            num_aces -= 1

        return value

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, color: Tuple[int, int, int]):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface: pygame.Surface) -> None:
        color = [min(c + 20, 255) if self.hover else c for c in self.color]
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        text_surface = FONT.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)

class BlackjackGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Blackjack")
        self.clock = pygame.time.Clock()

        self.deck = Deck()
        self.player = Player("Player")
        self.dealer = Player("Dealer", is_dealer=True)
        self.bet = 0

        self.hit_button = Button(50, SCREEN_HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT, "Hit", GREEN)
        self.stand_button = Button(300, SCREEN_HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT, "Stand", RED)
        self.deal_button = Button(550, SCREEN_HEIGHT - 70, BUTTON_WIDTH, BUTTON_HEIGHT, "Deal", BLUE)

        self.game_state = "betting"
        self.message = "Enter bet amount:"

        # Background
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background.fill(GREEN)
        for i in range(20):
            start_pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            end_pos = (random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
            pygame.draw.line(self.background, (0, 80, 0), start_pos, end_pos, 2)

    def run(self) -> None:
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if self.game_state == "betting":
                    self.handle_bet_input(event)

    def handle_click(self, pos: Tuple[int, int]) -> None:
        if self.game_state == "player_turn":
            if self.hit_button.is_clicked(pos):
                self.player_hit()
            elif self.stand_button.is_clicked(pos):
                self.player_stand()
        elif self.game_state == "game_over":
            if self.deal_button.is_clicked(pos):
                self.start_new_round()

    def handle_bet_input(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_RETURN:
            self.place_bet()
        elif event.key == pygame.K_BACKSPACE:
            self.message = self.message[:-1]
        elif event.unicode.isdigit():
            self.message += event.unicode

    def update(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        self.hit_button.update(mouse_pos)
        self.stand_button.update(mouse_pos)
        self.deal_button.update(mouse_pos)

        if self.game_state == "dealing":
            self.deal_initial_cards()
        elif self.game_state == "dealer_turn":
            self.dealer_turn()

        for player in [self.player, self.dealer]:
            for i, card in enumerate(player.hand):
                if player.is_dealer:
                    card.target_pos = (50 + i * 30, 50)
                else:
                    card.target_pos = (50 + i * 30, SCREEN_HEIGHT - 250)
                card.target_angle = random.uniform(-5, 5)
                card.update()

    def draw(self) -> None:
        self.screen.blit(self.background, (0, 0))
        
        # Draw hands
        self.draw_hand(self.player.hand)
        self.draw_hand(self.dealer.hand, self.game_state != "dealer_turn")

        # Draw buttons
        if self.game_state == "player_turn":
            self.hit_button.draw(self.screen)
            self.stand_button.draw(self.screen)
        elif self.game_state == "game_over":
            self.deal_button.draw(self.screen)

        # Draw messages
        self.draw_text(f"Player Chips: {self.player.chips}", 110, 10)
        self.draw_text(f"Current Bet: {self.bet}", 83, 40)
        self.draw_text(self.message, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        pygame.display.flip()

    def draw_hand(self, hand: List[Card], hide_first: bool = False) -> None:
        for i, card in enumerate(hand):
            if i == 0 and hide_first:
                # Draw card back
                pygame.draw.rect(self.screen, BLUE, (*card.pos, CARD_WIDTH, CARD_HEIGHT), border_radius=5)
                pygame.draw.rect(self.screen, GOLD, (*card.pos, CARD_WIDTH, CARD_HEIGHT), 2, border_radius=5)
            else:
                card.draw(self.screen)

    def draw_text(self, text: str, x: int, y: int) -> None:
        text_surface = FONT.render(text, True, WHITE)
        text_rect = text_surface.get_rect(center=(x, y))
        self.screen.blit(text_surface, text_rect)

    def start_new_round(self) -> None:
        self.deck = Deck()
        self.deck.shuffle()
        self.player.clear_hand()
        self.dealer.clear_hand()
        self.message = "Enter bet amount:"
        self.game_state = "betting"
        self.bet = 0

    def place_bet(self) -> None:
        try:
            bet = int(self.message.split(":")[-1])
            if 0 < bet <= self.player.chips:
                self.bet = bet
                self.game_state = "dealing"
                self.message = "Dealing cards..."
            else:
                self.message = "Invalid bet. Enter bet amount:"
        except ValueError:
            self.message = "Invalid input. Enter bet amount:"

    def deal_initial_cards(self) -> None:
        for _ in range(2):
            self.deal_card(self.player)
            self.deal_card(self.dealer)
        self.game_state = "player_turn"
        self.message = "Your turn: Hit or Stand?"

    def deal_card(self, player: Player) -> None:
        card = self.deck.deal()
        if card:
            card.pos = (SCREEN_WIDTH // 2, 0)  # Start from the top center
            player.add_card(card)

    def player_hit(self) -> None:
        self.deal_card(self.player)
        if self.player.get_hand_value() > 21:
            self.message = "You busted! Dealer wins."
            self.player.chips -= self.bet
            self.game_state = "game_over"
        else:
            self.message = "Your turn: Hit or Stand?"

    def player_stand(self) -> None:
        self.game_state = "dealer_turn"
        self.message = "Dealer's turn..."

    def dealer_turn(self) -> None:
        if self.dealer.get_hand_value() < 17:
            self.deal_card(self.dealer)
        else:
            self.determine_winner()

    def determine_winner(self) -> None:
        player_value = self.player.get_hand_value()
        dealer_value = self.dealer.get_hand_value()

        if dealer_value > 21:
            self.message = "Dealer busted! You win!"
            self.player.chips += self.bet
        elif player_value > dealer_value:
            self.message = "You win!"
            self.player.chips += self.bet
        elif dealer_value > player_value:
            self.message = "Dealer wins."
            self.player.chips -= self.bet
        else:
            self.message = "It's a tie!"

        self.game_state = "game_over"

if __name__ == "__main__":
    game = BlackjackGame()
    game.run()