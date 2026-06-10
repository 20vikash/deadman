import frappe

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from deadman.deadman.doctype.deadman_settings.deadman_settings import DeadmanSettings


def initialize_setup(secret: str):
	settings: DeadmanSettings = frappe.get_single("Deadman Settings")

	settings.deadman_password = secret

	settings.save(ignore_permissions=True)

	frappe.db.commit()
