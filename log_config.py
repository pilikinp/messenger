import logging
import logging.handlers
import sys
import time

# Определяем формат
format = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

# Создаем обработчик

debug_hand = logging.handlers.TimedRotatingFileHandler('app.log', when= 'midnight', backupCount= 3)
debug_hand.setLevel((logging.DEBUG))
debug_hand.setFormatter(format)

# создать регистратор

app_log = logging.getLogger('app')
app_log.setLevel(logging.DEBUG)
app_log.addHandler(debug_hand)

