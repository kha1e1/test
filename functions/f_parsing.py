import logging
import re


def parsing_service_new(
        service: str
):
    try:
        pattern = "\s\d+\s\w{3}\s\(⏱\s\d{2}\sмин.\)"
        service = re.sub(pattern, "", service)
        return service

    except Exception as e:
        logging.info(e)


def parsing_service(
        service: str
):
    pattern = "✅"
    service = re.sub(pattern, "", service)
    return service
