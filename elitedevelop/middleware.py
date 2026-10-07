# middleware.py
import time
from .models import RequestLog
from bs4 import BeautifulSoup, NavigableString
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.html import escape

from django.http import HttpResponsePermanentRedirect


class OldDomainRedirectMiddleware:

    """

    Permanently redirect the old PythonAnywhere domain

    to the new canonical EliteDevelop domain.

    """

    OLD_DOMAIN = "elitedevelop.pythonanywhere.com"

    NEW_DOMAIN = "elitedevelop.org"

    def __init__(self, get_response):

        self.get_response = get_response

    def __call__(self, request):

        if request.get_host().split(":")[0].lower() == self.OLD_DOMAIN:

            new_url = f"https://{self.NEW_DOMAIN}{request.get_full_path()}"

            return HttpResponsePermanentRedirect(new_url)

        return self.get_response(request)

class RequestLoggerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = (time.time() - start_time) * 1000

        # Avoid logging the status dashboard itself to prevent endless loops!
        if not request.path.startswith('/admindash/'):
            RequestLog.objects.create(
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=round(duration, 2)
            )

        return response

class OrganizationIdentityMiddleware:
    """
    Automatically replaces standalone organization usernames in HTML
    responses with the organization's logo, name, and verification badge.

    Example:

        google

    becomes:

        [logo] Google ✓
    """

    SKIP_TAGS = {
        "script",
        "style",
        "textarea",
        "code",
        "pre",
        "noscript",
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process normal HTML responses.
        content_type = response.get("Content-Type", "")

        if "text/html" not in content_type:
            return response

        # Don't touch streaming responses.
        if getattr(response, "streaming", False):
            return response

        # Don't touch responses without a body.
        if not response.content:
            return response

        # Build a username -> organization mapping.
        organization_users = (
            User.objects
            .select_related("profile", "profile__organization")
            .filter(
                profile__is_organization_account=True,
                profile__organization__isnull=False,
            )
        )

        identity_map = {}

        for user in organization_users:
            organization = user.profile.organization

            if not organization:
                continue
            identity_map[user.username] = {
                "name": user.username,
                "logo": organization.logo.url if organization.logo else None,
                "verified": organization.verified,
            }

        if not identity_map:
            return response

        soup = BeautifulSoup(
            response.content,
            "html.parser"
        )

        for text_node in soup.find_all(string=True):

            parent = text_node.parent

            if not parent:
                continue

            # Don't modify code, scripts, styles, etc.
            if parent.name in self.SKIP_TAGS:
                continue

            text = str(text_node).strip()

            if text not in identity_map:
                continue

            identity = identity_map[text]

            # Don't replace text inside attributes or weird elements.
            if parent.name in {"title", "option"}:
                continue

            # Create the identity wrapper.
            wrapper = soup.new_tag(
                "span",
                attrs={"class": "ed-identity"}
            )

            if identity["logo"]:
                img = soup.new_tag(
                    "img",
                    src=identity["logo"],
                    alt="",
                    attrs={
                        "class": "ed-identity-logo",
                        "aria-hidden": "true",
                    },
                )
                wrapper.append(img)

            name = soup.new_tag(
                "span",
                attrs={"class": "ed-identity-name"}
            )
            name.string = identity["name"]
            wrapper.append(name)

            if identity["verified"]:
                badge = soup.new_tag(
                    "i",
                    attrs={
                        "class": "fa-solid fa-circle-check ed-verified-badge",
                        "title": "Verified organization",
                        "aria-label": "Verified organization",
                    },
                )
                wrapper.append(badge)

            text_node.replace_with(wrapper)

        response.content = str(soup).encode(response.charset or "utf-8")

        return response