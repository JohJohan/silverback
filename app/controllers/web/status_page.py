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

# Standard Library
import os

# Third Party Library
from django.http import Http404
from django.views import View
from django.shortcuts import render

# Local Library
from app.modules.core.context import Context
from app.modules.entity.option_entity import OptionEntity
from app.modules.core.decorators import redirect_if_not_installed
from app.modules.core.status_page import StatusPage as StatusPageModule


class StatusPageIndex(View):
    """Status Page Index Page Controller"""

    template_name = 'templates/status_page_index.html'

    @redirect_if_not_installed
    def get(self, request):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__context = Context()
        self.__option_entity = OptionEntity()
        self.__status_page_module = StatusPageModule()

        self.__context.autoload_options()
        self.__context.push({
            "page_title": self.__context.get("app_name", os.getenv("APP_NAME", "Silverback")),
            "is_authenticated": request.user and request.user.is_authenticated,
            "system_status": self.__status_page_module.get_system_status(),
            "about_site": self.__status_page_module.get_about_site(),
            "logo_url": self.__status_page_module.get_logo_url(),
            "favicon_url": self.__status_page_module.get_favicon_url(),
            "past_incidents": self.__status_page_module.get_past_incidents(7),
            "system_metrics": self.__status_page_module.get_system_metrics(),
            "services": self.__status_page_module.get_services()
        })

        return render(request, self.template_name, self.__context.get())


class StatusPageHistory(View):
    """Status Page History Page Controller"""

    template_name = 'templates/status_page_history.html'

    @redirect_if_not_installed
    def get(self, request, period):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__context = Context()
        self.__option_entity = OptionEntity()
        self.__status_page_module = StatusPageModule()

        period = int(period)

        if period < 1:
            raise Http404("History period not found.")

        data = self.__status_page_module.get_incidents_for_period(period)

        if not data:
            raise Http404("History period not found.")

        self.__context.autoload_options()
        self.__context.push({
            "page_title": self.__context.get("app_name", os.getenv("APP_NAME", "Silverback")),
            "logo_url": self.__status_page_module.get_logo_url(),
            "favicon_url": self.__status_page_module.get_favicon_url(),
            "is_authenticated": request.user and request.user.is_authenticated,
            "prev_link": period + 1,
            "next_link": period - 1 if period > 1 else 0,
            "history_period": data["period"],
            "past_incidents": data["incidents"],
        })

        return render(request, self.template_name, self.__context.get())


class StatusPageSingle(View):
    """Status Page Single Page Controller"""

    template_name = 'templates/status_page_single.html'

    @redirect_if_not_installed
    def get(self, request, uri):

        self.__correlation_id = request.META["X-Correlation-ID"] if "X-Correlation-ID" in request.META else ""
        self.__context = Context()
        self.__option_entity = OptionEntity()
        self.__status_page_module = StatusPageModule()

        incident = self.__status_page_module.get_incident_by_uri(uri)

        if not incident:
            raise Http404("Incident not found.")

        self.__context.autoload_options()
        self.__context.push({
            "page_title": self.__context.get("app_name", os.getenv("APP_NAME", "Silverback")),
            "logo_url": self.__status_page_module.get_logo_url(),
            "favicon_url": self.__status_page_module.get_favicon_url(),
            "is_authenticated": request.user and request.user.is_authenticated,
            "uri": uri,
            "incident": incident
        })

        return render(request, self.template_name, self.__context.get())
