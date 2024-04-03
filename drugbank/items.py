"""Models for scraped items."""

from scrapy.item import Field, Item


class DrugItem(Item):
    id = Field()
    smiles = Field()
    scraped_at = Field()


class TargetItem(Item):
    target_id = Field()
    drug_id = Field()
    gene_name = Field()
    scraped_at = Field()


class ActionItem(Item):
    target_id = Field()
    name = Field()
    scraped_at = Field()


class ExternalIdentifierItem(Item):
    target_id = Field()
    name = Field()
    value = Field()
    url = Field()
    scraped_at = Field()
