"""Vercel serverless entrypoint — reuses VaiRequestHandler from local UI."""

from vai.server import VaiRequestHandler


class handler(VaiRequestHandler):
    pass