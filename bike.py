"""Bike class for TRON Lightcycles game."""
import math


class Bike:
	"""Represents a lightcycle with position, direction, trail, and status effects."""

	def __init__(self, sprite, color, name, mask=None):
		self.sprite = sprite
		self.mask = mask  # Mask for pixel-perfect collision detection
		self.color = color
		self.name = name
		self.pos = [0, 0]  # Back position of bike
		self.dir = (0, 0)  # Direction vector
		self.trail = []  # List for rendering (ordered)
		self.trail_set = set()  # Set for fast collision detection
		self.frozen_until = 0
		self.slow_until = 0
		self.fast_until = 0
		self.last_turn_time = 0
		self.last_turn_direction = None  # Track the last turn made (LEFT, RIGHT, UP, DOWN)

	def reset_trail(self):
		"""Clear the bike's trail."""
		self.trail = []
		self.trail_set = set()

	def reset_status(self):
		"""Clear all status effects."""
		self.frozen_until = 0
		self.slow_until = 0
		self.last_turn_time = 0
		self.last_turn_direction = None

	def get_front_pos(self, sprite_width, back_margin=4):
		"""Calculate the front position of the bike."""
		dx, dy = self.dir
		mag = math.hypot(dx, dy)
		if mag == 0:
			return self.pos
		nx, ny = dx / mag, dy / mag
		length = sprite_width - back_margin
		front_x = self.pos[0] + nx * length
		front_y = self.pos[1] + ny * length
		return [front_x, front_y]

	def add_trail_point(self, pos):
		"""Add a position to the trail (only if different from last)."""
		if len(self.trail) == 0 or self.trail[-1] != pos:
			self.trail.append(pos)
			self.trail_set.add(pos)

	def is_frozen(self, current_time):
		"""Check if bike is currently frozen."""
		return current_time < self.frozen_until

	def is_slowed(self, current_time):
		"""Check if bike is currently slowed."""
		return current_time < self.slow_until
	
	def is_fast(self, current_time):
		"""Check if bike is currently fast."""
		return current_time < self.fast_until

	def get_effective_speed(self, base_speed, current_time):
		"""Get the effective speed considering status effects."""
		if self.is_frozen(current_time):
			return 0
		if self.is_slowed(current_time):
			return base_speed // 2
		return base_speed

	def can_turn(self, current_time, cooldown):
		"""Check if enough time has passed since last turn."""
		return current_time - self.last_turn_time >= cooldown

	def is_zigzag(self, new_direction, dirs, current_time, zigzag_window=200):
		"""
		Check if the new direction would be a zigzag move.
		A zigzag is when you turn to the same direction as your last turn within a short time window.
		For example: turning LEFT then LEFT again within 200ms.

		Args:
			new_direction: The direction to check
			dirs: Dictionary of direction vectors
			current_time: Current game time in milliseconds
			zigzag_window: Time window in milliseconds to check for zigzag (default 200ms)
		"""
		if self.last_turn_direction is None:
			return False

		# Only check for zigzag if within the time window
		time_since_last_turn = current_time - self.last_turn_time
		if time_since_last_turn > zigzag_window:
			return False

		# Define same direction pairs (turning the same way twice rapidly)
		same_direction_pairs = [
			(dirs["LEFT"], dirs["LEFT"]),
			(dirs["RIGHT"], dirs["RIGHT"]),
			(dirs["UP"], dirs["UP"]),
			(dirs["DOWN"], dirs["DOWN"])
		]

		# Check if trying to turn in the same direction as last turn
		for last_dir, same_dir in same_direction_pairs:
			if self.last_turn_direction == last_dir and new_direction == same_dir:
				return True

		return False

	def render(self, screen, blit_func, back_margin=4):
		"""Render the bike sprite on the screen."""
		blit_func(screen, self.sprite, self.pos, self.dir, back_margin)
