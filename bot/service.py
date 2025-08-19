from base_service.base import BaseService
from bot.models import InviterModel, VisitorModel


class InviterService(BaseService):
    model = InviterModel


class VisitorService(BaseService):
    model = VisitorModel