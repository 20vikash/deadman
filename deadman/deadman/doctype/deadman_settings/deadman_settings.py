# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DeadmanSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		deadman_token: DF.Password
		default_grace_multiplier: DF.Float
	# end: auto-generated types

	_DOCTYPE_NAME = "Deadman Settings"
