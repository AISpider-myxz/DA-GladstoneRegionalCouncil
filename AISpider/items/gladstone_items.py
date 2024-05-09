from scrapy import Field
from . import BaseItem


class GladstoneItem(BaseItem):
    application_id = Field()
    description = Field()
    submit = Field()
    status = Field()
    address = Field()
    site_address = Field()
    decision = Field()
    names = Field()
    documents = Field()

    class Meta:
        table = 'gladstone'
        unique_fields = ['application_id',]