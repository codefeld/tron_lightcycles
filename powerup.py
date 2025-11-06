"""PowerUp class for TRON Lightcycles game."""
import pygame
from main import *

class PowerUp:
	"""Represents a power-up on the grid."""

	TYPES = ["freeze", "slow", "fast"]
	COLORS = {"freeze": (0, 200, 255), "slow": (0, 255, 100)}

	def __init__(self, x, y, size, ptype, theme):
		self.x = x
		self.y = y
		self.size = size
		self.type = ptype
		self.color = (255, 192, 203)
		if theme == "ARES":
			self.color = (255, 0, 0)
		elif theme == "LEGACY":
			self.color = (0, 200, 255)
		elif theme == "82":
			self.color = (128, 0, 128)
		elif theme == "RECONFIGURED":
			self.color = (0, 255, 0)
		else:
			self.color = PowerUp.COLORS[ptype]

	def contains_point(self, x, y):
		"""Check if a point is inside this power-up."""
		return self.x <= x <= self.x + self.size and self.y <= y <= self.y + self.size

	def apply_effect(self, bike, current_time):
		"""Apply this power-up's effect to a bike."""
		if self.type == "freeze":
			bike.frozen_until = current_time + 3000
		elif self.type == "slow":
			bike.slow_until = current_time + 5000
		elif self.type == "fast":
			bike.fast_until = current_time + 3000

	def render(self, screen, theme):
		"""Render the power-up on the screen."""
		pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
		if theme == "ARES":
			pygame.draw.rect(screen, (128, 128, 128), (self.x, self.y, self.size, self.size), 2)
		elif theme == "82":
			pygame.draw.rect(screen, (122, 189, 255), (self.x, self.y, self.size, self.size), 2)
		elif theme == "LEGACY":
			pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.size, self.size), 2)
		elif theme == "RECONFIGURED":
			pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.size, self.size), 2)
