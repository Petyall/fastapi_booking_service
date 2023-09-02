import logging
from datetime import datetime
from pythonjsonlogger import jsonlogger

from app.config import settings


# Создание логгера
logger = logging.getLogger()

# Хэндлер, обозначивающий вывод логов в консоль
logHandler = logging.StreamHandler()

# Создание формата логгера
class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get("timestamp"):
            now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
            log_record["timestamp"] = now
        if log_record.get("level"):
            log_record["level"] = log_record["level"].upper()
        else:
            log_record["level"] = record.levelname
  

formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"
)

# Прикрепление форматтера к хэндлеру
logHandler.setFormatter(formatter)
# Добавление хэндлера к логгеру
logger.addHandler(logHandler)
# Установка уровня логгирования
logger.setLevel(settings.LOG_LEVEL)