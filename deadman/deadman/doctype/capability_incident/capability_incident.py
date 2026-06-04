# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CapabilityIncident(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		capability: DF.Link
		reason: DF.SmallText | None
		resolved_at: DF.Datetime | None
		started_at: DF.Datetime
		status: DF.Literal["Open", "Resolved"]
	# end: auto-generated types

	_DOCTYPE_NAME = "Capability Incident"
