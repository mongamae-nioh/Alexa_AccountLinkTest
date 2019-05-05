# coding: UTF-8
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.utils.request_util import get_account_linking_access_token
from ask_sdk_model.services import ServiceException
from ask_sdk.standard import StandardSkillBuilder

import json
import requests

sb = StandardSkillBuilder(table_name="AccountLinkTest01", auto_create_table=True)

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speech_text = 'ようこそ'
        
        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class AccountLinkTestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AccountLinkTestIntent")(handler_input)

    def handle(self, handler_input):
        # The method retrieves the user’s accessToken from the input request. Once a user successfully enables a
        # skill and links their Alexa account to the skill, the input request will have the user’s access token. A None
        # value is returned if there is no access token in the input request. More information on this can be found here :
        # https://developer.amazon.com/docs/account-linking/add-account-linking-logic-custom-skill.html

        accessToken = get_account_linking_access_token(handler_input)
        attr = handler_input.attributes_manager.persistent_attributes

        if not attr:
            attr['games_played'] = 0

        handler_input.attributes_manager.session_attributes = attr
        
        if accessToken is None:
            speech_text = 'ログインを許可してください'
        else:
            session_attr = handler_input.attributes_manager.session_attributes

            url = "https://api.amazon.com/user/profile?access_token=" + accessToken
            req = requests.get(url)
            body = json.loads(req.text)
            name = body["name"]
            
            session_attr['games_played'] += 1
            handler_input.attributes_manager.persistent_attributes = session_attr
            handler_input.attributes_manager.save_persistent_attributes()
            times_is = int(attr['games_played'])
            
            speech_text = "{}さん、こんにちは。{}回目のプレイです。".format(name,times_is)

        handler_input.response_builder.speak(speech_text).ask(speech_text)
        return handler_input.response_builder.response

class AllExceptionHandler(AbstractExceptionHandler):

    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):

        # Log the exception in CloudWatch Logs
        print(exception)

        speech = "すみません、わかりませんでした。もう一度言ってください。"
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(AccountLinkTestIntentHandler())

sb.add_exception_handler(AllExceptionHandler())

handler = sb.lambda_handler()