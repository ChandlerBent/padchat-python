import logging
import tornado.log


logger = logging.getLogger('padchat')
#
# logger_format = '%(levelname)s %(asctime)s %(filename)s %(module)s ' + \
#                 '%(funcName)s %(lineno)d %(message)s'

tornado.log.enable_pretty_logging()
# logger.setLevel(logging.DEBUG)
