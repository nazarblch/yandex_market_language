from abc import ABC, abstractmethod
from typing import List

from .base import BaseModel, XMLElement, XMLSubElement
from .price import Price
from .fields import EnableAutoDiscountField
from ..exceptions import ValidationError


class BaseOffer(BaseModel, EnableAutoDiscountField, ABC):
    def __init__(
        self,
        offer_id,
        url,
        price: Price,
        currency: str,
        category_id,
        vendor=None,
        vendor_code=None,
        bid=None,
        old_price=None,
        enable_auto_discounts=None,
        pictures: List[str] = None,
        delivery=True,
        pickup=True,
    ):
        self.vendor = vendor
        self.vendor_code = vendor_code
        self.offer_id = offer_id
        self.bid = bid
        self.url = url
        self.price = price
        self.old_price = old_price
        self.enable_auto_discounts = enable_auto_discounts
        self.currency = currency
        self.category_id = category_id
        self.pictures = pictures
        self.delivery = delivery
        self.pickup = pickup

    @staticmethod
    def _value_to_bool(value, attr: str):
        if value in ["true", "false"]:
            return value
        elif value is True:
            return "true"
        elif value is False:
            return "false"
        else:
            raise ValidationError(
                "The {attr} parameter should be boolean. "
                "Got {t} instead.".format(attr=attr, t=type(value))
            )

    @property
    def delivery(self) -> bool:
        return True if self._delivery == "true" else False

    @delivery.setter
    def delivery(self, value):
        self._delivery = self._value_to_bool(value, "delivery")

    @property
    def pickup(self) -> bool:
        return True if self._delivery == "true" else False

    @pickup.setter
    def pickup(self, value):
        self._pickup = self._value_to_bool(value, "pickup")

    @abstractmethod
    def create_dict(self, **kwargs) -> dict:
        return dict(
            vendor=self.vendor,
            vendor_code=self.vendor_code,
            offer_id=self.offer_id,
            bid=self.bid,
            url=self.url,
            price=self.price,
            old_price=self.old_price,
            enable_auto_discounts=self.enable_auto_discounts,
            currency=self.currency,
            category_id=self.category_id,
            pictures=self.pictures,
            delivery=self.delivery,
            pickup=self.pickup,
            **kwargs
        )

    @abstractmethod
    def create_xml(self, **kwargs) -> XMLElement:
        offer_el = XMLElement("offer", {"id": self.offer_id})

        # Add offer bid attribute
        if self.bid:
            offer_el.attrib["bid"] = self.bid

        # Add simple values
        for tag, attr in (
            ("vendor", "vendor"),
            ("url", "url"),
            ("oldprice", "old_price"),
            ("enable_auto_discounts", "_enable_auto_discounts"),
            ("currencyId", "currency"),
            ("categoryId", "category_id"),
            ("delivery", "_delivery"),
            ("pickup", "_pickup"),
        ):
            value = getattr(self, attr)
            if value:
                el = XMLSubElement(offer_el, tag)
                el.text = value

        # Add vendor code
        if self.vendor_code:
            vendor_code_el = XMLSubElement(offer_el, "vendorCode")
            vendor_code_el.text = self.vendor_code

        # Add price
        self.price.to_xml(offer_el)

        # Add pictures
        if self.pictures:
            for url in self.pictures:
                picture_el = XMLSubElement(offer_el, "picture")
                picture_el.text = url

        return offer_el


class SimplifiedOffer(BaseOffer):
    def __init__(self, name, **kwargs):
        self.name = name
        super().__init__(**kwargs)

    def create_dict(self, **kwargs) -> dict:
        return super().create_dict(name=self.name)

    def create_xml(self, **kwargs) -> XMLElement:
        offer_el = super().create_xml()
        name_el = XMLElement("name")
        name_el.text = self.name
        offer_el.insert(0, name_el)
        return offer_el
