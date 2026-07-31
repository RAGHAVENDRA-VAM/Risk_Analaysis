"""Stable test configuration independent of local deployment .env values."""
import os

os.environ["DEBUG"] = "false"
