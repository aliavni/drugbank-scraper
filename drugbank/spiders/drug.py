from datetime import datetime

import scrapy

from drugbank.items import ActionItem, DrugItem, ExternalIdentifierItem, TargetItem

SCRAPED_AT = datetime.utcnow()


class DrugSpider(scrapy.Spider):
    name = "drug"
    allowed_domains = ["drugbank.ca"]
    start_urls = [
        "https://www.drugbank.ca/drugs/DB00619",
        "https://www.drugbank.ca/drugs/DB01048",
        "https://www.drugbank.ca/drugs/DB14093",
        "https://www.drugbank.ca/drugs/DB00173",
        "https://www.drugbank.ca/drugs/DB00734",
        "https://www.drugbank.ca/drugs/DB00218",
        "https://www.drugbank.ca/drugs/DB05196",
        "https://www.drugbank.ca/drugs/DB09095",
        "https://www.drugbank.ca/drugs/DB01053",
        "https://www.drugbank.ca/drugs/DB00274",
    ]

    def parse(self, response):

        drug = DrugItem()

        drugbank_id = response.url.split("/")[-1]
        drug["id"] = drugbank_id

        # Smiles
        drug["smiles"] = response.xpath(
            '//dt[@id="smiles"]/following-sibling::dd/div/text()'
        ).extract_first()
        drug["scraped_at"] = SCRAPED_AT

        yield drug

        # Targets
        targets = response.xpath(
            '//*[@id="targets"]//div[contains(@class, "bond card")]'
        )

        for target in targets:
            target_item = TargetItem()

            target_id = target.xpath("@id").extract_first()
            target_item["target_id"] = target_id
            target_item["drug_id"] = drugbank_id

            # Gene name
            if gene_name_labels := target.xpath('.//dt[@id="gene-name"]'):
                gene_name_value = (
                    gene_name_labels[0]
                    .xpath("following-sibling::dd/text()")
                    .extract_first()
                )
                target_item["gene_name"] = gene_name_value

            target_item["scraped_at"] = SCRAPED_AT
            yield target_item

            # Actions
            if action_labels := target.xpath('.//dt[@id="actions"]'):
                actions = action_labels[0].xpath("following-sibling::dd/div")

                _action_items = []
                for action in actions:
                    _action = ActionItem(target_id=target_id)
                    _action["name"] = action.xpath("text()").extract_first()
                    _action["scraped_at"] = SCRAPED_AT
                    yield _action

            if target_details_link := target.xpath(
                './/div[@class="card-header"]/a/@href'
            ).get():

                yield scrapy.Request(
                    response.urljoin(target_details_link),
                    callback=self.process_target_details,
                    meta={"target_item": target_item, "drug": drug},
                )

    def process_target_details(self, response):
        target_item = response.meta["target_item"]
        external_identifiers = response.xpath(
            '//*[@id="external-identifiers"]/tbody//tr'
        )

        for identifier in external_identifiers:
            resource, link = identifier.xpath(".//td")

            item = ExternalIdentifierItem()
            item["target_id"] = target_item["target_id"]
            item["name"] = resource.xpath("text()").get()
            item["value"] = link.xpath("a/text()").get()
            item["url"] = link.xpath("a/@href").get()

            item["scraped_at"] = SCRAPED_AT

            yield item
