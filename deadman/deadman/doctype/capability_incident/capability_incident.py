# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


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

	def after_insert(self):
		#TODO: Fan out alerts to notification channels
		pass


def create_incident(capability: str, reason: str):
	incident = frappe.get_doc(
		{
			"doctype": "Capability Incident",
			"capability": capability,
			"started_at": now_datetime(),
			"status": "Open",
			"reason": reason,
		}
	)

	incident.insert(ignore_permissions=True)

	return incident


def resolve_incident(incident_name: str):
	if not incident_name:
		return None

	incident = frappe.get_doc(
		"Capability Incident",
		incident_name,
	)

	incident.status = "Resolved"
	incident.resolved_at = now_datetime()

	incident.save(ignore_permissions=True)

	return incident
