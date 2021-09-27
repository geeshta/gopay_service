from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Dict, List
from requests import Session
from functools import wraps
from .gopay_types import api_date, api_response, numeric
from . import rest


@dataclass
class GopayResponse:
    """
    Class wrapper around the response dict, return by the rest module functions
    """

    success: bool
    status: int
    content_type: str
    body: api_response = field(repr=False)


@dataclass
class Gopay:
    """
    Main class for interacting with the GoPay payment system. Token is created
    and refreshed automatically when needed.
    """

    client_id: str
    client_secret: str = field(repr=False)
    goid: numeric
    api_root: str = "https://gw.sandbox.gopay.com"
    scope: str = field(repr=False, default="payment-all")
    _session: Session = field(repr=False, default_factory=Session)
    _token: str = field(repr=False, init=False)
    _token_created: datetime = field(repr=False, init=False)
    _last_response: GopayResponse = field(repr=False, init=False)
    _enabled_payment_instruments: Dict = field(repr=False, init=False)
    _enabled_swifts: Dict = field(repr=False, init=False)

    @property
    def last_response(self) -> GopayResponse:
        """
        Returns GopayResponse of the last API operation
        """
        return self._last_response

    @property
    def payment_instruments(self) -> Dict:
        """
        Returns dict of payment instruments. Keys are available currencies
        and values are list of dicts, containing the payment instruments
        name, label and image url
        """
        return self._get_entries(self._enabled_payment_instruments)

    @property
    def enabled_swifts(self) -> Dict[str, List[str]]:
        """
        Returns dict of swifts. Keys are available currencies
        and values are list of dicts, containing the swift name, label
        and image url
        """
        return self._get_entries(self._enabled_swifts, swifts=True)

    @property
    def _token_expired(self) -> bool:
        diff = datetime.now() - self._token_created
        return diff.seconds > 1800

    def api_request(func):
        """
        Refreshes the auth token if needed, supplies some args and converts the
        REST response dict to a GopayResponse object
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs) -> GopayResponse:
            if self._token_expired:
                self._get_token()
            response = func(
                self,
                *args,
                **kwargs,
                api_root=self.api_root,
                token=self._token,
                session=self._session,
            )
            return self._handle_response(response)

        return wrapper

    def _handle_response(self, response: Dict) -> GopayResponse:
        gopay_response = GopayResponse(**response)
        self._last_response = gopay_response
        return gopay_response

    def _get_token(self) -> None:
        body = {"scope": self.scope, "grant_type": "client_credentials"}
        self._token_created = datetime.now()
        response = rest.get_token(
            self.api_root,
            self.client_id,
            self.client_secret,
            body,
            session=self._session,
        )
        self._handle_response(response)
        if response["success"]:
            self._token = response["body"].get("access_token")

    def _parse_entry(self, key: str, value: Dict) -> Dict:
        return {
            "name": key,
            "label": value.get("label").get("cs"),
            "image": value.get("image").get("large"),
            "currencies": value.get("currencies"),
        }

    def _parse_entries(self, gopay_entries: Dict) -> List[Dict]:
        return [self._parse_entry(key, value) for key, value in gopay_entries.items()]

    def _filter_out_currency(self, instrument: Dict) -> Dict:
        return {key: value for key, value in instrument.items() if key != "currencies"}

    def _get_entries(self, parsed_entries: List, swifts: bool = False) -> Dict:
        currencies = []
        if not swifts:
            for instrument in parsed_entries:
                currencies.extend(instrument["currencies"])
        else:
            for instrument in parsed_entries:
                currencies.extend(instrument["currencies"].keys())

        currencies = sorted(list(set(currencies)))

        final_entries = {}
        for currency in currencies:
            final_entries[currency] = [
                self._filter_out_currency(instrument)
                for instrument in parsed_entries
                if currency in instrument["currencies"]
            ]

        return final_entries

    def _get_payment_methods(self) -> None:
        response = self.fetch_payment_methods()
        if response.success:
            enabled_payment_instruments = response.body.get("enabledPaymentInstruments")
            enabled_swifts = enabled_payment_instruments.get("BANK_ACCOUNT").get(
                "enabledSwifts"
            )
            self._enabled_payment_instruments = self._parse_entries(
                enabled_payment_instruments
            )
            self._enabled_swifts = self._parse_entries(enabled_swifts)

    def __post_init__(self) -> None:
        self._get_token()
        self._get_payment_methods()

    def reload(self) -> None:
        """
        Refresh the token and payment methods. This can be useful if the
        allowed payment methods changed in GoPay
        """
        self._get_token()
        self._get_payment_methods()

    @api_request
    def create_payment(self, body: Dict, **config) -> GopayResponse:
        """
        Create a payment. The request body is the same as described
        on https://doc.gopay.com/#payment-creation, except you can
        leave out the `target` object
        """
        body.setdefault("target", {"type": "ACCOUNT", "goid": self.goid})
        return rest.create_payment(body=body, **config)

    @api_request
    def payment_status(self, id: numeric, **config) -> GopayResponse:
        """
        Payment status inquiry
        """
        return rest.payment_status(id=id, **config)

    @api_request
    def payment_eet_receipts(self, id=id, **config) -> GopayResponse:
        """
        Get EET Receipts for a single payment
        """
        return rest.payment_eet_receipts(id=id, **config)

    @api_request
    def refund_payment(self, id: numeric, amount: int, **config) -> GopayResponse:
        """
        Refund a payment
        """
        body = {"amount": amount}
        return rest.refund_payment(id=id, body=body, **config)

    @api_request
    def create_recurrence(self, id: numeric, body: Dict, **config) -> GopayResponse:
        """
        Create an on-demand recurrence. The request body is the same as
        on https://doc.gopay.com/#recurring-on-demand
        """
        return rest.create_recurrence(id=id, body=body, **config)

    @api_request
    def void_recurrence(self, id: numeric, **config) -> GopayResponse:
        """
        Cancel a payment recurrence
        """
        return rest.void_recurrence(id=id, **config)

    @api_request
    def capture_preauthorization(self, id: numeric, **config) -> GopayResponse:
        """
        Capture a preauthorized payment
        """
        return rest.capture_preauthorization(id=id, **config)

    @api_request
    def capture_preauthorization_partial(
        self, id: numeric, body: Dict, **config
    ) -> GopayResponse:
        """
        Capture a part of a preauthorized payment. The request body is the same
        as on https://doc.gopay.com/#partially-capturing-a-preauthorized-payment
        """
        return rest.capture_preauthorization_partial(id=id, body=body, **config)

    @api_request
    def void_preauthorization(self, id: numeric, **config) -> GopayResponse:
        """
        Void a payment preauthorization
        """
        return rest.void_preauthorization(id=id, **config)

    @api_request
    def fetch_payment_methods(self, currency: str = None, **config) -> GopayResponse:
        """
        Get a list of payment methods. This method is called internally upon
        initialization. The payment methods and swifts are parsed and saved
        in object instance properties
        """
        return rest.get_payment_methods(goid=self.goid, currency=currency, **config)

    @api_request
    def account_statement(
        self,
        currency: str,
        format: str,
        date_from: api_date,
        date_to: api_date = date.today(),
        **config,
    ) -> GopayResponse:
        """
        Download an account statement. The date can be either a 'YYYY-MM-RR'
        string or a python datetime.Date object instance
        """
        body = {
            "date_from": str(date_from),
            "date_to": str(date_to),
            "goid": self.goid,
            "currency": currency,
            "format": format,
        }
        return rest.account_statement(body=body, **config)

    @api_request
    def eet_receipts(
        self,
        id_provozovny: numeric,
        date_from: api_date,
        date_to: api_date = date.today(),
        **config,
    ) -> GopayResponse:
        """
        Get EET receipts for a given time span on an account
        """
        body = {
            "date_from": str(date_from),
            "date_to": str(date_to),
            "id_provozovny": id_provozovny,
        }
        return rest.eet_receipts(body=body, **config)
