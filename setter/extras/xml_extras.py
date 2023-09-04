"""setter.extras.xml_extras"""

import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dependencies_met = False
try:
    dependencies_met = True
except ImportError:
    msg = "dependencies not met for 'xml_extras', install with setter[dataframe]"
    logger.warning(msg)
