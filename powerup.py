"""PowerUp class for TRON Lightcycles game."""
import pygame


class PowerUp:
	"""Represents a power-up on the grid."""

	TYPES = ["freeze", "slow"]
	COLORS = {"freeze": (0, 200, 255), "slow": (0, 255, 100)}

	def __init__(self, x, y, size, ptype):
		self.x = x
		self.y = y
		self.size = size
		self.type = ptype
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

	def render(self, screen):
		"""Render the power-up on the screen."""
		pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))
		pygame.draw.rect(screen, (255, 255, 255), (self.x, self.y, self.size, self.size), 2)
