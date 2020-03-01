
import logging
from logging import StreamHandler, FileHandler
from datetime import datetime

now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

logging.basicConfig( 
	handlers = [ StreamHandler()], # , FileHandler( filename= f"errors_{now}.log")],
	format = "%(levelname)s | %(message)s"
	)

logging.error('This is an error message')
logging.debug('This is an error message')