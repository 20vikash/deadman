# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CapabilityHeartbeat(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		capability: DF.Link
		last_seen: DF.Datetime
	# end: auto-generated types

	_DOCTYPE_NAME = "Capability Heartbeat"
