# Copyright 2019 Silverbackhq
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Third Party Library
from django.views import View
from django.http import JsonResponse
from django.utils.translation import gettext as _

# Local Library
from pyvalitron.form import Form
from app.modules.util.helpers import Helpers
from app.modules.core.request import Request
from app.modules.core.response import Response
from app.modules.validation.extension import ExtraRules
from app.modules.core.decorators import stop_request_if_authenticated
from app.modules.core.forgot_password import ForgotPassword as ForgotPasswordModule


class ForgotPassword(View):
    """Forgot Password Private Endpoint Controller"""

    def __init__(self):
        self.__request = Request()
        self.__response = Response()
        self.__helpers = Helpers()
        self.__form = Form()
        self.__forgot_password = ForgotPasswordModule()
        self.__logger = self.__helpers.get_logger(__name__)
        self.__correlation_id = ""
        self.__form.add_validator(ExtraRules())

    @stop_request_if_authenticated
    def post(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__request.set_request(request)

        request_data = self.__request.get_request_data("post", {
            "email": ""
        })

        self.__form.add_inputs({
            'email': {
                'value': request_data["email"],
                'sanitize': {
                    'strip': {}
                },
                'validate': {
                    'sv_email': {
                        'error': _('Error! Email is invalid.')
                    }
                }
            }
        })

        self.__form.process()

        if not self.__form.is_passed():
            return JsonResponse(self.__response.send_errors_failure(self.__form.get_errors(), {}, self.__correlation_id))

        if not self.__forgot_password.check_email(self.__form.get_sinput("email")):
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Email is not exist.")
            }], {}, self.__correlation_id))

        reset_request = self.__forgot_password.reset_request_exists(self.__form.get_sinput("email"))

        if reset_request:
            if self.__forgot_password.is_spam(reset_request):
                return JsonResponse(self.__response.send_private_failure([{
                    "type": "error",
                    "message": _("Sorry! You already exceeded the maximum number of reset requests!")
                }], {}, self.__correlation_id))
            token = self.__forgot_password.update_request(reset_request)
        else:
            token = self.__forgot_password.create_request(self.__form.get_sinput("email"))

        if not token:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while creating reset request.")
            }], {}, self.__correlation_id))

        message = self.__forgot_password.send_message(self.__form.get_sinput("email"), token)

        if not message:
            return JsonResponse(self.__response.send_private_failure([{
                "type": "error",
                "message": _("Error! Something goes wrong while sending reset instructions.")
            }], {}, self.__correlation_id))
        else:
            return JsonResponse(self.__response.send_private_success([{
                "type": "success",
                "message": _("Reset instructions sent successfully.")
            }], {}, self.__correlation_id))
