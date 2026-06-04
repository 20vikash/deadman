# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from deadman.deadman.doctype.capability_incident.capability_incident import (
    create_incident,
    resolve_incident,
)


class Capability(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		capability_name: DF.Data
		grace_multiplier: DF.Float
		heartbeat_interval: DF.Int
	# end: auto-generated types

	_DOCTYPE_NAME = "Capability"


def check_heartbeat():
	now = now_datetime()

	settings = frappe.get_cached_doc("Deadman Settings")
	default_grace_multiplier = settings.default_grace_multiplier

	capabilities = frappe.get_all(
		"Capability",
		fields=[
			"name",
			"heartbeat_interval",
			"grace_multiplier",
		],
	)

	for capability in capabilities:
		heartbeat = frappe.db.get_value(
			"Capability Heartbeat",
			{"capability": capability.name},
			["name", "last_seen"],
			as_dict=True,
		)

		if not heartbeat:
			continue

		grace_multiplier = (
			capability.grace_multiplier
			or default_grace_multiplier
		)

		allowed_delay = (
			capability.heartbeat_interval
			* grace_multiplier
		)

		seconds_since_last_heartbeat = (
			now - heartbeat.last_seen
		).total_seconds()

		open_incident = frappe.db.exists(
			"Capability Incident",
			{
				"capability": capability.name,
				"status": "Open",
			},
		)

		if seconds_since_last_heartbeat > allowed_delay:
			if not open_incident:
				create_incident(
					capability=capability.name,
					reason=(
						f"Heartbeat missing. "
						f"Expected every {capability.heartbeat_interval} seconds. "
						f"Last seen at {heartbeat.last_seen}."
					),
				)
		else:
			if open_incident:
				resolve_incident(open_incident)

	frappe.db.commit()
