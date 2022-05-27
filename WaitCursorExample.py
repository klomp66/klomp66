def testFunction():
	import time

	# do whatever it is you want to do here
	print("Start fnc")
	time.sleep(5)
	print("stop fnc")

#
# Runs a function in a wait cursor
#
def runWithWaitCursor(fnc):
	from java.awt import Cursor
	from com.innovit.ice.client.ui import AdminController

	glassPane = AdminController.getIceFrame().getGlassPane();

	try:
		# set the wait cursor
		glassPane.setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR));
		glassPane.setVisible(true)

		# call the function now
		message = "Please try to stay awake while Jeff talks about what macros and edit rules can do"
		showInfoDialogWithTitle("Macro Button Example", message)
		#testFunction()

	except:
		# reset the cursor
		glassPane.setCursor(Cursor.getDefaultCursor());
		glassPane.setVisible(false)

	finally:
		# reset the cursor
		glassPane.setCursor(Cursor.getDefaultCursor());
		glassPane.setVisible(false)

#
# Starts here
#
runWithWaitCursor(testFunction)
