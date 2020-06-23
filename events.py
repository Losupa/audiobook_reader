from enum import Enum

class AppState(Enum):
	INPUT = 1
	SPEAKING = 2
	

class MathOperation(Enum):

	ADD = 1
	SUBTRACT = 2
	MULTIPLY = 3
	DIVIDE = 4
	EQUALS = 5

class SoundLib(Enum):
	C5 = "Piano.mf.C5.aiff"
	D5 = "Piano.mf.D5.aiff"
	E5 = "Piano.mf.E5.aiff"
	F5 = "Piano.mf.F5.aiff"
	G5 = "Piano.mf.G5.aiff"
