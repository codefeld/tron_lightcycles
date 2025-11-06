"""Obstacle class for TRON Lightcycles game."""
import pygame
from main import *

class Obstacle:
	"""Represents an obstacle on the grid."""

	def __init__(self, x, y, size):
		self.x = x
		self.y = y
		self.size = size

	def contains_point(self, x, y):
		"""Check if a point is inside this obstacle."""
		return self.x <= x <= self.x + self.size and self.y <= y <= self.y + self.size

	def overlaps_with(self, other):
		"""Check if this obstacle overlaps with another obstacle."""
		return (self.x < other.x + other.size and
		        self.x + self.size > other.x and
		        self.y < other.y + other.size and
		        self.y + self.size > other.y)

	def is_near_position(self, pos, margin):
		"""Check if a position is within margin distance of this obstacle."""
		return (abs(self.x - pos[0]) < margin and abs(self.y - pos[1]) < margin)

	def render(self, screen, theme):
		"""Render the obstacle on the screen."""
		core = pygame.Rect(self.x, self.y, self.size, self.size)
		if theme == "LEGACY":
			pygame.draw.rect(screen, (0, 0, 0), core)
			pygame.draw.rect(screen, (255, 255, 255), core, 2)
		elif theme == "RECONFIGURED":
			pygame.draw.rect(screen, (0, 0, 0), core)
			pygame.draw.rect(screen, (144, 238, 144), core, 2)
		elif theme == "82":
			pygame.draw.rect(screen, (13, 54, 77), core)
			pygame.draw.rect(screen, (113, 0, 0), core, 2)
		elif theme == "ARES":
			pygame.draw.rect(screen, (0, 0, 0), core)
			pygame.draw.rect(screen, (255, 180, 180), core, 2)
		elif theme == "UPRISING":
			pygame.draw.rect(screen, (0, 0, 0), core)
			pygame.draw.rect(screen, (255, 255, 255), core, 2)
