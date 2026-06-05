import frappe

import requests
from typing import TYPE_CHECKING

from twilio.rest import Client

if TYPE_CHECKING:
	from deadman.deadman.doctype.deadman_settings.deadman_settings import DeadmanSettings


def get_twilio_client():
	settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")

	return Client(
		settings.twilio_api_key_sid,
		settings.get_password("twilio_api_key_secret"),
		settings.twilio_account_sid,
	)


def call_human(phone: str, message: str):
	settings: DeadmanSettings = frappe.get_cached_doc("Deadman Settings")

	client = get_twilio_client()

	return client.calls.create(
		to=phone,
		from_=settings.twilio_phone_number,
		twiml=f"""
		<Response>
			<Say>{message}<Say>
		</Response>
		""",
	)


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
