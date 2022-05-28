#!/usr/bin/env python3

MODELS = {}


class ModelWrapper:

	def __init__(self, name):
		self.name = name

	def __getattr__(self, item):
		return getattr(MODELS[self.name], item)


def set_model(name, model):
	MODELS[name] = model


def get_model(name):
	return ModelWrapper(name)
