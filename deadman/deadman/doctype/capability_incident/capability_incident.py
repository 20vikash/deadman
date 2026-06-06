# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from typing import TYPE_CHECKING

from twilio.rest import Client
import requests

if TYPE_CHECKING:
	from deadman.deadman.doctype.deadman_settings.deadman_settings import DeadmanSettings


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
		status: DF.Literal["Validating", "Confirmed", "Acknowledged", "Resolved"]
	# end: auto-generated types

	_DOCTYPE_NAME = "Capability Incident"

	def after_insert(self):
		#TODO: Fan out alerts to notification channels
		pass

	@property
	def twilio_client(self):
		settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")

		return Client(
			settings.twilio_api_key_sid,
			settings.get_password("twilio_api_key_secret"),
			settings.twilio_account_sid,
		)


	@property
	def twilio_phone_number(self):
		pass

	def get_humans(self):
		pass

	def call_human(self):
		pass

	def call_humans(self):
		pass

	def send_twilio_sms(self):
		pass


	def send_telegram_message(message: str):
		settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")

		token = settings.get_password("telegram_bot_token")
		chat_id = settings.telegram_chat_id

		response = requests.post(
			f"https://api.telegram.org/bot{token}/sendMessage",
			json={
				"chat_id": chat_id,
				"text": message,
			},
			timeout=30,
		)

		response.raise_for_status()

		return response.json()


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
