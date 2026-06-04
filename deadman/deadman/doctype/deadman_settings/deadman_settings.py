# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class DeadmanSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from deadman.deadman.doctype.notification_users.notification_users import NotificationUsers
		from frappe.types import DF

		deadman_password: DF.Password
		default_grace_multiplier: DF.Float
		notification_users: DF.Table[NotificationUsers]
		telegram_bot_token: DF.Password | None
		telegram_chat_id: DF.Data | None
		twilio_account_sid: DF.Data | None
		twilio_api_key_secret: DF.Password | None
		twilio_api_key_sid: DF.Data | None
		twilio_phone_number: DF.Data | None
	# end: auto-generated types

	_DOCTYPE_NAME = "Deadman Settings"
