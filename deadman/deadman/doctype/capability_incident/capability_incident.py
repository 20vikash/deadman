# Copyright (c) 2026, vikash and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

from typing import TYPE_CHECKING

from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import requests
from functools import cached_property
from tenacity import RetryError, retry, stop_after_attempt, wait_fixed
from tenacity.retry import retry_if_not_result

if TYPE_CHECKING:
	from deadman.deadman.doctype.deadman_settings.deadman_settings import DeadmanSettings
	from twilio.rest.api.v2010.account.call import CallInstance


class CapabilityIncident(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		acknowledged_by: DF.Link | None
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

	@cached_property
	def twilio_client(self):
		settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")

		return Client(
			settings.twilio_api_key_sid,
			settings.get_password("twilio_api_key_secret"),
			settings.twilio_account_sid,
		)

	@cached_property
	def twilio_phone_number(self):
		settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")
		return settings.twilio_phone_number

	def get_humans(self):
		settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")
		users = settings.notification_users

		ret = list(users)
		if self.status == "Acknowledged":  # repeat the acknowledged user to be the first
			for user in users:
				if user.user == self.acknowledged_by:
					ret.remove(user)
					ret.insert(0, user)
		return ret
	
	@retry(
		retry=retry_if_not_result(
			lambda result: result in ["canceled", "completed", "failed", "busy", "no-answer", "in-progress"]
		),
		wait=wait_fixed(1),
		stop=stop_after_attempt(30),
	)
	def wait_for_pickup(self, call: CallInstance):
		return call.fetch().status  # will eventually be no-answer

	def call_human(self, phone: str, message: str) -> CallInstance:
		settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")

		try:
			client = self.twilio_client

			return client.calls.create(
				to=phone,
				from_=settings.twilio_phone_number,
				twiml=f"""
				<Response>
					<Say>{message}</Say>
				</Response>
				""",
			)
		except TwilioRestException:
			raise

	def call_humans(self, message: str):
		frappe.enqueue_doc(
			self.doctype,
			self.name,
			"_call_humans",
			message=message,
		)

	def _call_humans(self, message: str):
		for human in self.get_humans():
			if not (call := self.call_human(human.phone, message)):
				return  # can't twilio
			status = str(call.status)
			try:
				status = str(self.wait_for_pickup(call))
			except RetryError:
				status = "timeout"  # not Twilio's status; mostly translates to no-answer
			else:
				if status in ["in-progress", "completed"]:  # call was picked up
					self.status = "Acknowledged"
					self.acknowledged_by = human.user
					self.save(ignore_permissions=True)
					break

	def send_twilio_sms(self, message: str):
		frappe.enqueue_doc(
			self.doctype,
			self.name,
			"_send_twilio_sms",
			message=message,
		)

	def _send_twilio_sms(self, message: str):
		for human in self.get_humans():
			self.twilio_client.messages.create(to=human.phone, from_=self.twilio_phone_number, body=message)

	def send_telegram_message(self, message: str):
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


def create_incident(capability, reason: str, status: str) -> CapabilityIncident:
	existing_incident = frappe.db.exists(
		"Capability Incident",
		{
			"capability": capability,
			"status": ("in", ["Validating", "Confirmed", "Acknowledged"]),
		},
	)
	if existing_incident and status == existing_incident.status:
		return frappe.get_doc("Capability Incident", existing_incident)
	elif existing_incident and status != existing_incident.status:
		doc = frappe.get_doc(
			"Capability Incident",
			existing_incident,
		)
		doc.status = status # Eg. Validating -> Confirmed
		doc.reason = reason
		doc.save(ignore_permissions=True)
		return doc
	else:
		return frappe.get_doc(
			{
				"doctype": "Capability Incident",
				"capability": capability,
				"started_at": now_datetime(),
				"reason": reason,
				"status": status,
			}
		).insert(ignore_permissions=True)


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
