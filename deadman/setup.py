import frappe

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from deadman.deadman.doctype.deadman_settings.deadman_settings import DeadmanSettings


def initialize_deadman(secret: str):
	settings: DeadmanSettings = frappe.get_single("Deadman Settings")

	settings.deadman_password = secret
	settings.save(ignore_permissions=True)

	default_capabilities = [
		("incident_validation", 300),
		("incident_resolution", 300),
		("prometheus", 300),
		("alertmanager", 300),
		("twilio", 300),
	]

	for capability_name, heartbeat_interval in default_capabilities:
		if frappe.db.exists(
			"Capability",
			{
				"capability_name": capability_name,
			},
		):
			continue

		frappe.get_doc(
			{
				"doctype": "Capability",
				"capability_name": capability_name,
				"heartbeat_interval": heartbeat_interval,
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
