import logging
from pathlib import Path

dir = Path(__file__).parent.parent.parent

logger_controll = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, filename=dir /'example.log', format='%(levelname)s (%(asctime)s): %(message)s (Line: %(lineno)d) [%(filename)s]',
                    datefmt='%d/%m/%Y %H:%M:%S', encoding='utf-8')
