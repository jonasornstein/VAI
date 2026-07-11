"""Vercel serverless entrypoint — reuses AtgRequestHandler from local UI."""

from atg.server import AtgRequestHandler


class handler(AtgRequestHandler):
    pass