from sqlalchemy.orm import sessionmaker

from drugbank.exceptions import UnknownItemException
from drugbank.items import ActionItem, DrugItem, ExternalIdentifierItem, TargetItem
from drugbank.models import (
    Action,
    Drug,
    ExternalIdentifier,
    Target,
    create_table,
    db_connect,
)


class DrugbankPipeline:
    def __init__(self):
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        self.session = self.Session()

    def process_item(self, item, spider):

        if isinstance(item, DrugItem):
            db_item = Drug(**item)
        elif isinstance(item, ActionItem):
            db_item = Action(**item)
        elif isinstance(item, TargetItem):
            db_item = Target(**item)
        elif isinstance(item, ExternalIdentifierItem):
            db_item = ExternalIdentifier(**item)
        else:
            raise UnknownItemException

        self.session.add(db_item)
        self.session.commit()
        self.session.close()

        return item
