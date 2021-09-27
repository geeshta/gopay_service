from typing import Tuple, Dict, Union, List
from datetime import date

numeric = Union[str, int]
token_or_credentials = Union[str, List[Dict], Tuple[str]]
api_response = Union[Dict, str]
api_date = Union[str, date]
