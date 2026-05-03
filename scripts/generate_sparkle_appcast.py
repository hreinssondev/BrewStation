#!/usr/bin/env python3

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import pathlib
from email.utils import format_datetime


def iso_to_rfc2822(value: str) -> str:
    normalized = value.replace("Z", "+00:00")
    published = dt.datetime.fromisoformat(normalized)
    if published.tzinfo is None:
        published = published.replace(tzinfo=dt.timezone.utc)
    return format_datetime(published)


def build_appcast(
    *,
    app_name: str,
    release_title: str,
    release_notes_url: str,
    asset_url: str,
    asset_length: int,
    signature: str,
    short_version: str,
    bundle_version: str,
    minimum_system_version: str,
    published_at: str,
) -> str:
    title = html.escape(release_title or f"{app_name} {short_version}")
    notes = html.escape(release_notes_url, quote=True)
    enclosure_url = html.escape(asset_url, quote=True)
    sparkle_signature = html.escape(signature, quote=True)
    short_version_attr = html.escape(short_version, quote=True)
    bundle_version_attr = html.escape(bundle_version, quote=True)
    minimum_system_version_attr = html.escape(minimum_system_version, quote=True)
    pub_date = html.escape(iso_to_rfc2822(published_at))

    return f"""<?xml version="1.0" encoding="utf-8"?>
<rss version="2.0"
     xmlns:sparkle="http://www.andymatuschak.org/xml-namespaces/sparkle"
     xmlns:dc="http://purl.org/dc/elements/1.1/">
  <channel>
    <title>{html.escape(app_name)} Appcast</title>
    <link>{notes}</link>
    <description>Latest updates for {html.escape(app_name)}</description>
    <language>en</language>
    <item>
      <title>{title}</title>
      <pubDate>{pub_date}</pubDate>
      <sparkle:version>{bundle_version_attr}</sparkle:version>
      <sparkle:shortVersionString>{short_version_attr}</sparkle:shortVersionString>
      <sparkle:minimumSystemVersion>{minimum_system_version_attr}</sparkle:minimumSystemVersion>
      <sparkle:releaseNotesLink>{notes}</sparkle:releaseNotesLink>
      <enclosure
        url="{enclosure_url}"
        sparkle:edSignature="{sparkle_signature}"
        length="{asset_length}"
        type="application/octet-stream" />
    </item>
  </channel>
</rss>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a minimal Sparkle appcast.xml file.")
    parser.add_argument("--release-json", required=True, help="Path to the GitHub release JSON payload.")
    parser.add_argument("--output", required=True, help="Path to write appcast.xml.")
    parser.add_argument("--app-name", required=True)
    parser.add_argument("--asset-url", required=True)
    parser.add_argument("--asset-length", required=True, type=int)
    parser.add_argument("--signature", required=True)
    parser.add_argument("--short-version", required=True)
    parser.add_argument("--bundle-version", required=True)
    parser.add_argument("--minimum-system-version", required=True)
    args = parser.parse_args()

    release = json.loads(pathlib.Path(args.release_json).read_text())
    appcast = build_appcast(
        app_name=args.app_name,
        release_title=release.get("name") or release.get("tag_name") or f"{args.app_name} {args.short_version}",
        release_notes_url=release["html_url"],
        asset_url=args.asset_url,
        asset_length=args.asset_length,
        signature=args.signature,
        short_version=args.short_version,
        bundle_version=args.bundle_version,
        minimum_system_version=args.minimum_system_version,
        published_at=release.get("published_at") or release.get("created_at") or dt.datetime.now(dt.timezone.utc).isoformat(),
    )

    output_path = pathlib.Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(appcast, encoding="utf-8")


if __name__ == "__main__":
    main()
