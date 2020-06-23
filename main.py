def main():

	isRunning = True
	while(isRunning):
		input = readInput()
		isRunning = GameLogic.doLogic()
		camera.update()
		world.update()
		gui.update()
		ai.update()
		audio.play()
		render.draw()

if __name__ == "__main__":
	main()