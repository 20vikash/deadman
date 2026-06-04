import frappe
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def ping():
	return {"status": "ok"}


def verify_password(password):
	settings = frappe.get_cached_doc("Deadman Settings")

	if password != settings.get_password("deadman_password"):
		raise frappe.PermissionError("Invalid password")


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_capability_heartbeat(capability_name, password):
	verify_password(password)

	if not frappe.db.exists("Capability", capability_name):
		frappe.throw(f"Capability {capability_name} does not exist")

	now = now_datetime()

	heartbeat_name = frappe.db.get_value(
		"Capability Heartbeat",
		{"capability": capability_name},
		"name",
	)

	if heartbeat_name:
		frappe.db.set_value(
			"Capability Heartbeat",
			heartbeat_name,
			"last_seen",
			now,
			update_modified=False,
		)
	else:
		frappe.get_doc(
			{
				"doctype": "Capability Heartbeat",
				"capability": capability_name,
				"last_seen": now,
			}
		).insert(ignore_permissions=True)

	return {
		"success": True,
		"capability": capability_name,
		"timestamp": now,
	}
