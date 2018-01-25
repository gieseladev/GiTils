"""Webiesela manager.

Terminology:
    gitoken - "Giesela Instance Token" A token used to identify Giesela instances
    regtoken - "Registration Token" A short token generated to determine the identity of a web user.
"""

import logging

from flask import Blueprint, jsonify, request

from GiTils.gitils import mongo_database

log = logging.getLogger(__name__)


blueprint = Blueprint("Webiesela", __name__, url_prefix="/webiesela")


@blueprint.route("/server/login/<gitoken>")
def server_login(token):
    """Login with a gitoken."""
    # TODO: login
    pass


@blueprint.route("/server/register")
def server_register():
    """Register a Giesela instance."""
    # TODO: register and return token
    pass


@blueprint.route("/endpoint/<token>")
def get_endpoint(token):
    """Get the appropriate address for a Giesela instance identified by the token."""
    # TODO: find corresponding Giesela instance data and return it
    pass


@blueprint.route("/registration/register")
def register_user():
    """Start the registration progress for a user."""
    # TODO: Generate registration token and return it
    pass


@blueprint.route("/registration/check/<regtoken>")
def check_registration(regtoken):
    """Check whether regtoken has been registered."""
    # TODO: Check the status of the token
    pass


@blueprint.route("/registration/claim")
def claim_token():
    """Giesela instance claim regtoken."""
    gitoken = request.args.get("gitoken", None)
    regtoken = request.args.get("regtoken", None)
    # TODO: Do the stuff
    pass
