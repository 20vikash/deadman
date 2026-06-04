import frappe
from frappe.utils import now_datetime


@frappe.whitelist(allow_guest=True)
def ping():
    return {"status": "ok"}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def update_capability_heartbeat(capability_name):
	#TODO: Read token from header and authenticate

	if not frappe.db.exists("Capability", capability_name):
		frappe.throw(f"Capability {capability_name} does not exist")

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
			now_datetime(),
			update_modified=False,
		)
	else:
		frappe.get_doc(
			{
				"doctype": "Capability Heartbeat",
				"capability": capability_name,
				"last_seen": now_datetime(),
			}
		).insert(ignore_permissions=True)

	frappe.db.commit()
