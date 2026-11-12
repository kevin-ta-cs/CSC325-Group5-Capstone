import random
import re
from datetime import date
from uuid import uuid4

from django.contrib.messages import get_messages
from django.middleware.csrf import get_token
from django.urls import reverse
from django.utils.formats import date_format
from django.utils.html import format_html, format_html_join

from .models import BUILDING_CHOICES, FoundItem, ITEM_CATEGORY_CHOICES


REPORTS = (
    {
        "type": "found",
        "category": "Electronics",
        "title": "Black Sony noise-canceling headphones",
        "description": "Black over-ear Sony headphones in a hard zip case. Found after the evening study period.",
        "building": "Greenley Library",
        "date": "2026-10-20",
        "image": "https://disc-fire-90145878.figma.site/api/media/file/black-headphones-original.jpg?w=960",
        "alt": "Black over-ear headphones",
    },
    {
        "type": "lost",
        "category": "Electronics",
        "title": "Sony headphones in black hard case",
        "description": "Lost black Sony wireless headphones with a zippered hard case while studying in the library.",
        "building": "Greenley Library",
        "date": "2026-10-20",
        "image": "",
        "alt": "",
    },
    {
        "type": "lost",
        "category": "Bags & Luggage",
        "title": "Navy backpack with laptop sleeve",
        "description": "Navy commuter backpack with a padded laptop sleeve and a silver water bottle in the side pocket.",
        "building": "Lupton Hall",
        "date": "2026-10-19",
        "image": "https://disc-fire-90145878.figma.site/api/media/file/campus-backpack-original.jpg?w=960",
        "alt": "Backpack and study essentials",
    },
    {
        "type": "found",
        "category": "Accessories",
        "title": "Brown leather card wallet",
        "description": "Slim brown leather wallet with several campus cards inside. No cash details are shown publicly.",
        "building": "Campus Center",
        "date": "2026-10-18",
        "image": "https://disc-fire-90145878.figma.site/api/media/file/leather-wallet-original.jpg?w=960",
        "alt": "Brown leather wallet",
    },
    {
        "type": "found",
        "category": "Accessories",
        "title": "Silver analog wristwatch",
        "description": "Silver metal-band analog watch found beside the indoor courts after recreation hours.",
        "building": "Nold Athletic Complex",
        "date": "2026-10-17",
        "image": "https://disc-fire-90145878.figma.site/api/media/file/silver-watch-original.jpg?w=960",
        "alt": "Silver wristwatch",
    },
    {
        "type": "found",
        "category": "Keys",
        "title": "Brass key ring with three keys",
        "description": "Three brass-colored keys on a small round key ring found after a rehearsal.",
        "building": "Memorial Hall",
        "date": "2026-10-16",
        "image": "https://disc-fire-90145878.figma.site/api/media/file/key-ring-original.jpg?w=960",
        "alt": "Vintage keys and key ring",
    },
)


HOME_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#014d48">
  <meta name="description" content="Report lost or found belongings and help your campus community reconnect with them.">
  <title>FindIt — Campus Lost &amp; Found</title>
  <style>
    :root {
      color-scheme: dark;
      --teal: #014d48;
      --teal-deep: #003e3a;
      --teal-bright: #66d8c6;
      --action-green: #014d48;
      --section-muted: rgba(255, 255, 255, .78);
      --white: #fff;
      --ink: #171b1b;
      --muted: #64716e;
      --paper: #fff;
      --line: #e5e9e8;
      --card: #fff;
      --header: #090a0b;
    }

    * { box-sizing: border-box; }
    html { scroll-behavior: smooth; scroll-padding-top: 80px; }
    body {
      margin: 0;
      background: var(--teal);
      color: var(--white);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light {
      color-scheme: light;
      --teal: #e5f4f0;
      --teal-deep: #d7eee9;
      --teal-bright: #087c70;
      --action-green: #003e3a;
      --section-muted: rgba(20, 59, 55, .78);
      --white: #143b37;
      --paper: #f7faf9;
      --line: #dce8e5;
    }
    body.theme-dark {
      color-scheme: dark;
      --teal: #0b211f;
      --teal-deep: #071917;
      --teal-bright: #66d8c6;
      --action-green: #075d56;
      --section-muted: rgba(238, 245, 243, .76);
      --white: #eef5f3;
      --paper: #111918;
      --ink: #eef5f3;
      --muted: #b3c0bd;
      --line: #34423f;
      --card: #111918;
    }
    a { color: inherit; }
    button, input, select { font: inherit; }
    .wrap { width: min(1280px, calc(100% - 64px)); margin-inline: auto; }
    .site-header {
      position: sticky;
      z-index: 10;
      top: 0;
      min-height: 64px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      background: rgba(9, 10, 11, 0.96);
      color: #fff;
      backdrop-filter: blur(14px);
    }
    .header-inner { display: grid; min-height: 64px; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 24px; }
    .brand { display: inline-flex; align-items: center; gap: 10px; justify-self: start; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .brand-mark {
      position: relative; display: grid; width: 36px; height: 36px; place-items: center;
      border-radius: 12px; background: #075d56; color: #fff; font-size: 0;
    }
    .brand-mark::before {
      width: 13px; height: 13px; transform: translate(-2px, -2px);
      border: 2.5px solid currentColor; border-radius: 50%; content: "";
    }
    .brand-mark::after {
      position: absolute; width: 7px; height: 2.5px; transform: translate(5px, 5px) rotate(45deg);
      border-radius: 2px; background: currentColor; content: "";
    }
    .primary-nav, .header-actions { display: flex; align-items: center; gap: 24px; }
    .primary-nav { justify-self: center; }
    .header-actions { justify-self: end; }
    .primary-nav a, .header-actions a { color: #f7f7f7; font-size: 0.9rem; font-weight: 600; text-decoration: none; }
    .primary-nav a:hover, .header-actions a:hover { color: var(--teal-bright); }
    .header-actions form { margin: 0; }
    .header-actions form button { padding: 0; border: 0; background: none; color: #f7f7f7; font-weight: 650; cursor: pointer; }
    .account-menu { position: relative; }
    .account-menu summary {
      padding: 6px 9px; border-radius: 8px; color: #f7f7f7;
      font-size: .9rem; font-weight: 600; cursor: pointer; list-style: none;
    }
    .account-menu summary:hover, .account-menu summary:focus-visible {
      background: rgba(140,232,216,.14); color: #8ce8d8;
    }
    .account-menu summary:focus-visible { outline: 2px solid #8ce8d8; outline-offset: 2px; }
    .account-menu summary:hover .account-username,
    .account-menu summary:focus-visible .account-username { color: #fff; text-decoration: underline; text-underline-offset: 3px; }
    .account-menu summary::-webkit-details-marker { display: none; }
    .account-menu summary::after {
      display: inline-block; width: 7px; height: 7px; margin: 0 0 3px 7px;
      transform: rotate(45deg); border-right: 1.5px solid currentColor;
      border-bottom: 1.5px solid currentColor; content: "";
    }
    .account-menu-panel {
      position: absolute; z-index: 20; top: 100%; right: 0; display: none;
      min-width: 180px; gap: 12px; padding: 14px; border: 1px solid #34423f;
      border-radius: 12px; background: #090a0b; box-shadow: 0 12px 28px rgba(0,0,0,.25);
    }
    .account-menu:hover .account-menu-panel,
    .account-menu:focus-within .account-menu-panel,
    .account-menu[open] .account-menu-panel { display: grid; }
    .account-menu-panel form button { font: inherit; text-align: left; }
    .theme-link { border: 0; background: transparent; color: #fff !important; font-size: 1.2rem !important; cursor: pointer; }
    .header-actions .header-cta {
      padding: 9px 18px; border-radius: 999px; background: #fff; color: var(--action-green); font-weight: 750;
    }
    .header-actions button.header-cta {
      border: 0; font: inherit; font-size: .9rem; cursor: pointer;
    }
    .header-actions .header-cta:hover { background: #e4f2ef; color: var(--action-green); }
    .hero {
      position: relative;
      overflow: hidden;
      background-color: var(--teal);
      background-image: radial-gradient(rgba(196, 255, 242, 0.16) 1px, transparent 1.5px);
      background-position: 0 0;
      background-size: 26px 26px;
      color: var(--white);
    }
    .hero-inner {
      display: grid;
      min-height: 660px;
      grid-template-columns: 1.05fr 0.95fr;
      align-items: center;
      gap: 48px;
      padding-block: 72px 88px;
    }
    .hero-copy { max-width: 650px; }
    .eyebrow {
      display: inline-flex; align-items: center; gap: 10px; margin: 0 0 22px;
      color: var(--teal-bright); font-size: 0.8rem; font-weight: 800;
      letter-spacing: 0.14em; text-transform: uppercase;
    }
    .eyebrow-pill {
      padding: 8px 14px; border: 1px solid rgba(255,255,255,.2);
      border-radius: 999px; background: rgba(255,255,255,.08); color: var(--white);
    }
    h1, h2, h3, p { margin-top: 0; }
    .hero h1 {
      max-width: 640px; margin-bottom: 20px; font-size: clamp(3rem, 5.5vw, 4.5rem);
      font-weight: 900; letter-spacing: -0.055em; line-height: 1.02;
    }
    .hero-description { max-width: 600px; margin-bottom: 28px; color: var(--section-muted); font-size: 1.15rem; }
    .hero-actions { display: flex; flex-wrap: wrap; gap: 12px; }
    .pill-button {
      display: inline-flex; min-height: 48px; align-items: center; justify-content: center;
      gap: 9px; padding: 12px 22px; border: 1px solid transparent; border-radius: 999px;
      background: #fff; color: var(--action-green); font-size: .94rem; font-weight: 800; text-decoration: none;
      transition: transform 160ms ease, background 160ms ease;
    }
    .pill-button:hover { transform: translateY(-2px); background: #e7f7f3; }
    .pill-button.outline { border-color: rgba(255,255,255,.28); background: rgba(255,255,255,.1); color: var(--white); }
    .pill-button.outline:hover { background: rgba(255,255,255,.18); }
    body.theme-light .pill-button {
      border-color: var(--action-green); background: var(--action-green); color: #fff;
    }
    body.theme-light .pill-button:hover { background: #002f2c; }
    body.theme-light .pill-button.outline {
      border-color: var(--action-green); background: #fff; color: var(--action-green);
    }
    body.theme-light .pill-button.outline:hover { background: #d7eee9; }
    body.theme-dark .header-actions .header-cta {
      border: 1px solid #66d8c6; background: #075d56; color: #fff;
    }
    body.theme-dark .header-actions .header-cta:hover { background: #087c70; color: #fff; }
    body.theme-dark .pill-button {
      border-color: #66d8c6; background: #66d8c6; color: #082f2b;
    }
    body.theme-dark .pill-button:hover { background: #8ce8d8; }
    body.theme-dark .pill-button.outline {
      border-color: #66d8c6; background: rgba(9, 10, 11, .35); color: #fff;
    }
    body.theme-dark .pill-button.outline:hover { background: rgba(9, 10, 11, .6); }
    .trust-list { display: flex; flex-wrap: wrap; gap: 22px; margin: 28px 0 0; padding: 0; list-style: none; }
    .trust-list li { color: var(--section-muted); font-size: .88rem; font-weight: 650; }
    .trust-list li::before { margin-right: 8px; color: #72e0cb; content: "✓"; font-weight: 900; }
    .hero-art { position: relative; min-height: 480px; }
    .hero-art > img { position: absolute; width: 100%; height: 100%; border-radius: 30px; object-fit: cover; object-position: center; }
    .match-card {
      position: absolute; right: -16px; bottom: -24px; width: min(340px, 85%);
      padding: 18px 20px; border: 1px solid #34423f; border-radius: 20px;
      background: #111918; color: #eef5f3; box-shadow: 0 20px 50px rgba(0,0,0,.25);
    }
    .match-card strong { display: block; margin-bottom: 6px; color: #8ce8d8; font-size: .77rem; letter-spacing: .1em; text-transform: uppercase; }
    .match-card p { margin: 0; color: #eef5f3; font-size: .9rem; }
    .match-card .match-score { margin-top: 3px; color: #b3c0bd; font-size: .82rem; }
    body.theme-light .match-card {
      border-color: #cfe7e1; background: #eaf7f4; color: #163d38;
    }
    body.theme-light .match-card strong { color: #168b7d; }
    body.theme-light .match-card p { color: #163d38; }
    body.theme-light .match-card .match-score { color: #596b67; }
    .light-section { background: var(--paper); color: var(--ink); }
    .section-inner { width: min(1280px, calc(100% - 64px)); margin-inline: auto; padding-block: 80px; }
    .section-heading { max-width: 720px; margin: 0 auto 34px; text-align: center; }
    .section-heading .eyebrow { margin-bottom: 4px; color: #168b7d; }
    .section-heading h2 { margin-bottom: 10px; font-size: clamp(2rem, 3.3vw, 2.8rem); font-weight: 800; letter-spacing: -.04em; line-height: 1.15; }
    .section-heading p:last-child { margin-bottom: 0; color: var(--muted); font-size: 1rem; }
    .steps { display: grid; grid-template-columns: repeat(3, 1fr); gap: 22px; }
    .step {
      min-height: 210px; padding: 26px; border: 1px solid var(--line);
      border-radius: 24px; background: #f8faf9;
    }
    .step-icon {
      display: grid; width: 48px; height: 48px; margin-bottom: 20px; place-items: center;
      border-radius: 15px; background: #e1f4ef; color: #087c70; font-size: 1.35rem; font-weight: 800;
    }
    .step h3 { margin-bottom: 8px; font-size: 1.08rem; font-weight: 750; }
    .step p { margin: 0; color: var(--muted); font-size: .92rem; }
    .catalog-section { background: var(--teal); color: var(--white); }
    .catalog-section .section-heading { max-width: 850px; margin-bottom: 42px; }
    .catalog-section .section-heading .eyebrow { color: var(--teal-bright); }
    .catalog-section .section-heading p:last-child { color: var(--section-muted); }
    .filters {
      display: grid; grid-template-columns: minmax(180px, 2fr) repeat(4, minmax(105px, 1fr));
      align-items: center; gap: 12px; margin-bottom: 26px; padding: 16px;
      border-radius: 20px; background: #fff; color: #171b1b;
    }
    .filters label { display: block; color: #58625f; font-size: .73rem; font-weight: 700; }
    .sr-only {
      position: absolute; width: 1px; height: 1px; overflow: hidden;
      clip: rect(0, 0, 0, 0); white-space: nowrap; clip-path: inset(50%);
    }
    .filters input, .filters select {
      width: 100%; min-height: 44px; padding: 9px 12px; border: 1px solid #dfe4e2;
      border-radius: 12px; background: #fff; color: #171b1b;
    }
    .filters select {
      padding-right: 36px; appearance: none;
      background-image:
        linear-gradient(45deg, transparent 50%, currentColor 50%),
        linear-gradient(135deg, currentColor 50%, transparent 50%);
      background-repeat: no-repeat;
      background-position: calc(100% - 17px) 50%, calc(100% - 13px) 50%;
      background-size: 4px 4px;
    }
    .search-field { position: relative; }
    .filters .search-field input { padding-right: 48px; }
    .filters input:focus, .filters select:focus { outline: 2px solid #43b9a7; outline-offset: 1px; }
    .filter-submit {
      position: absolute; top: 6px; right: 6px; width: 32px; min-height: 32px; padding: 0;
      border: 0; border-radius: 8px;
      background: #003e3a; color: #fff; font-weight: 750; cursor: pointer;
    }
    .report-summary { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin: 0 0 18px; }
    .report-summary strong { font-size: .95rem; }
    .report-summary span { color: var(--section-muted); font-size: .86rem; }
    .report-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
    .report-card-link { display: block; min-width: 0; color: inherit; text-decoration: none; }
    .report-card {
      overflow: hidden; border: 1px solid rgba(255,255,255,.16); border-radius: 18px;
      background: #fff; color: #1b2221; box-shadow: 0 8px 24px rgba(0,0,0,.1);
      transition: transform 160ms ease, box-shadow 160ms ease;
    }
    .report-card:hover { transform: translateY(-4px); box-shadow: 0 14px 32px rgba(0,0,0,.18); }
    .report-image { position: relative; display: grid; height: 190px; place-items: center; overflow: hidden; background: #102a28; }
    .report-image img { width: 100%; height: 100%; object-fit: cover; }
    .report-image .placeholder { color: rgba(255,255,255,.8); font-size: 2.3rem; font-weight: 800; }
    .report-badge {
      position: absolute; top: 14px; left: 14px; padding: 5px 13px;
      border-radius: 999px; background: #72e1d0; color: #064943; font-size: .75rem; font-weight: 800;
    }
    .report-badge.lost { background: #ffd84c; color: #352b00; }
    .report-content { padding: 18px; }
    .report-category { margin: 0 0 6px; color: #087c70; font-size: .7rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
    .report-content h3 { margin-bottom: 8px; font-size: 1.06rem; line-height: 1.3; }
    .report-description { min-height: 54px; margin-bottom: 14px; color: #626c69; font-size: .85rem; }
    .report-meta { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px; color: #626c69; font-size: .77rem; }
    .report-details-link {
      display: flex; justify-content: space-between; margin-top: 20px; padding: 14px 16px;
      border-radius: 14px; background: #f3f4f3; color: #1b2221; font-weight: 750;
    }
    .report-card-link:hover .report-details-link { background: #e8f8f4; color: #087c70; }
    .report-card-link:focus-visible { outline: 3px solid #43b9a7; outline-offset: 4px; border-radius: 18px; }
    .browse-link { display: flex; width: fit-content; margin: 28px auto 0; color: var(--white); font-weight: 750; text-decoration: none; }
    .dashboard-section .section-inner { padding-block: 72px; }
    .dashboard-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
    .dashboard-card { padding: 32px; border-radius: 24px; background: #090a0b; color: #fff; }
    .dashboard-card.secondary { border: 1px solid #cfe7e1; background: #eaf7f4; color: #163d38; }
    .dashboard-card .eyebrow { margin-bottom: 4px; color: #75ddca; }
    .dashboard-card.secondary .eyebrow { color: #168b7d; }
    .dashboard-card h2 { margin-bottom: 12px; font-size: 1.75rem; letter-spacing: -.035em; line-height: 1.2; }
    .dashboard-card p { margin-bottom: 22px; color: rgba(255,255,255,.75); font-size: .93rem; }
    .dashboard-card.secondary p { color: #596b67; }
    .dashboard-card a, .dashboard-card .dashboard-action {
      color: #8ce8d8; font-weight: 750; text-decoration: none;
    }
    .dashboard-card .dashboard-action {
      padding: 0; border: 0; background: none; font: inherit; font-weight: 750; text-align: left; cursor: pointer;
    }
    .dashboard-card.secondary a, .dashboard-card.secondary .dashboard-action { color: #087c70; }
    body.theme-light .dashboard-card:not(.secondary) {
      border: 1px solid #cfe7e1; background: #eaf7f4; color: #163d38;
    }
    body.theme-light .dashboard-card:not(.secondary) .eyebrow { color: #168b7d; }
    body.theme-light .dashboard-card:not(.secondary) p { color: #596b67; }
    body.theme-light .dashboard-card:not(.secondary) a,
    body.theme-light .dashboard-card:not(.secondary) .dashboard-action { color: #087c70; }
    .site-footer { background: #090a0b; color: #b6c0be; }
    .footer-inner { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 40px; padding-block: 54px 30px; }
    .footer-brand { color: #fff; font-size: 1.15rem; font-weight: 800; }
    .footer-about p { max-width: 360px; margin: 12px 0 0; color: #a4afac; font-size: .88rem; }
    .footer-column h2 { margin-bottom: 14px; color: #fff; font-size: .86rem; }
    .footer-column a { display: block; margin: 8px 0; color: #b6c0be; font-size: .85rem; text-decoration: none; }
    .footer-column a:hover { color: #8ce8d8; }
    .copyright { padding: 18px 0 24px; border-top: 1px solid #252a2a; color: #9ba5a3; font-size: .78rem; text-align: center; }
    .empty-state { grid-column: 1 / -1; padding: 32px; border: 1px solid rgba(255,255,255,.2); border-radius: 18px; color: rgba(255,255,255,.8); text-align: center; }
    body.theme-dark .step { border-color: #34423f; background: #111918; }
    body.theme-dark .step-icon { background: #263a36; color: #8ce8d8; }
    body.theme-dark .filters { background: #111918; color: #eef5f3; }
    body.theme-dark .filters label { color: #c1ceca; }
    body.theme-dark .filters input,
    body.theme-dark .filters select {
      border-color: #34423f; background-color: #192321; color: #eef5f3; color-scheme: dark;
    }
    body.theme-dark .report-card { border-color: #34423f; background: #111918; color: #eef5f3; }
    body.theme-dark .report-category { color: #8ce8d8; }
    body.theme-dark .report-description,
    body.theme-dark .report-meta { color: #b3c0bd; }
    body.theme-dark .report-details-link { background: #111918; color: #eef5f3; }
    body.theme-dark .report-card-link:hover .report-details-link { background: #263a36; color: #8ce8d8; }
    body.theme-dark .dashboard-card.secondary {
      border-color: #34423f; background: #111918; color: #eef5f3;
    }
    body.theme-dark .dashboard-card:not(.secondary) { border: 1px solid #34423f; background: #111918; }
    body.theme-dark .dashboard-card.secondary .eyebrow { color: #8ce8d8; }
    body.theme-dark .dashboard-card.secondary p { color: #b3c0bd; }
    body.theme-dark .dashboard-card.secondary a,
    body.theme-dark .dashboard-card.secondary .dashboard-action { color: #8ce8d8; }
    @media (max-width: 1120px) {
      .header-inner { display: flex; flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; }
    }
    @media (max-width: 1000px) {
      .primary-nav { gap: 14px; }
      .header-inner { gap: 14px; }
      .hero-inner { min-height: 580px; gap: 30px; }
      .hero-art { min-height: 420px; }
      .report-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    }
    @media (max-width: 860px) {
      .filters { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .search-field { grid-column: 1 / -1; }
    }
    @media (max-width: 700px) {
      .wrap, .section-inner { width: min(100% - 36px, 560px); }
      .header-inner { flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; gap: 10px; }
      .primary-nav a { font-size: .78rem; }
      .header-actions { gap: 12px; }
      .header-actions .header-cta { padding: 8px 12px; font-size: .78rem; }
      .hero-inner { min-height: auto; grid-template-columns: 1fr; gap: 36px; padding-block: 54px 68px; }
      .hero h1 { font-size: clamp(2.8rem, 13vw, 4rem); }
      .hero-description { font-size: 1rem; }
      .hero-art { min-height: 340px; }
      .match-card { right: 8px; bottom: -22px; }
      .section-inner { padding-block: 60px; }
      .steps, .dashboard-grid { grid-template-columns: 1fr; }
      .step { min-height: auto; }
      .filters { grid-template-columns: 1fr 1fr; padding: 12px; }
      .report-grid { grid-template-columns: 1fr; }
      .report-summary { align-items: flex-start; flex-direction: column; gap: 4px; }
      .footer-inner { grid-template-columns: 1fr 1fr; gap: 28px; }
      .footer-about { grid-column: 1 / -1; }
    }
    @media (max-width: 390px) {
      .primary-nav { flex-wrap: wrap; justify-content: center; column-gap: 14px; }
      .header-actions a:not(.header-cta) { font-size: .8rem; }
      .pill-button { width: 100%; }
      .filters { grid-template-columns: 1fr; }
      .search-field { grid-column: auto; }
      .footer-inner { grid-template-columns: 1fr; }
      .footer-about { grid-column: auto; }
    }
    @media (prefers-reduced-motion: reduce) {
      *, *::before, *::after { scroll-behavior: auto !important; transition-duration: .01ms !important; }
    }
  </style>
</head>
<body class="__THEME__">
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="/" aria-label="FindIt home"><span class="brand-mark" aria-hidden="true"></span>FindIt</a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="#how-it-works">How it works</a>
        <a href="__BROWSE_ITEMS_URL__">Browse items</a>
      </nav>
      <div class="header-actions">
        <button class="theme-link" type="button" data-theme-toggle aria-label="Switch to light mode" aria-pressed="false">☀</button>
        __ACCOUNT_LINK__
        <a class="header-cta" href="__FOUND_REPORT_URL__">Report an item</a>
      </div>
    </div>
  </header>
  <main>
    <section class="hero" id="report-actions">
      <div class="wrap hero-inner">
        <div class="hero-copy">
          <p class="eyebrow eyebrow-pill">⌕ &nbsp; Campus-powered recovery</p>
          <h1>Lost something? Your campus is already looking.</h1>
          <p class="hero-description">Report lost or found belongings, discover smart matches, and verify ownership without exposing private contact details.</p>
          <div class="hero-actions">
            <a class="pill-button" href="__REPORT_URL__">Report a lost item <span aria-hidden="true">→</span></a>
            <a class="pill-button outline" href="__FOUND_REPORT_URL__">I found something</a>
          </div>
          <ul class="trust-list">
            <li>Free to use</li>
            <li>Secure claims</li>
            <li>Smart matching</li>
          </ul>
        </div>
        <div class="hero-art">
          <img src="https://disc-fire-90145878.figma.site/campus-findit.jpg" alt="Student carrying a backpack on campus">
          <div class="match-card">
            <strong>Smart match found</strong>
            <p>Black backpack · Library</p>
            <p class="match-score">92% confidence</p>
          </div>
        </div>
      </div>
    </section>
    <section class="light-section" id="how-it-works">
      <div class="section-inner">
        <div class="section-heading">
          <p class="eyebrow">How it works</p>
          <h2>From report to return, safely.</h2>
        </div>
        <div class="steps">
          <article class="step">
            <span class="step-icon" aria-hidden="true">＋</span>
            <h3>1. Report the details</h3>
            <p>Choose lost or found, category, campus building, date, and distinguishing information.</p>
          </article>
          <article class="step">
            <span class="step-icon" aria-hidden="true">⌕</span>
            <h3>2. Review smart matches</h3>
            <p>FindIt compares opposite report types using category, location, date, and description signals.</p>
          </article>
          <article class="step">
            <span class="step-icon" aria-hidden="true">✓</span>
            <h3>3. Verify and return</h3>
            <p>Private proof questions help the finder or staff confirm ownership before a safe handoff.</p>
          </article>
        </div>
      </div>
    </section>
    <section class="catalog-section" id="recent-items">
      <div class="section-inner">
        <div class="section-heading">
          <p class="eyebrow">Live campus catalog</p>
          <h2>Recently reported near you</h2>
          <p>Filter by item type, category, or campus building. Every report is managed by its owner and tracked through a verified return workflow.</p>
        </div>
        __FILTERS__
        <div class="report-summary">
          <strong>Showing __DISPLAY_COUNT__ of __REPORT_COUNT__ active reports</strong>
          <span>✳ &nbsp;Smart matches compare category, place, date, and description</span>
        </div>
        <div class="report-grid">__REPORT_CARDS__</div>
        <a class="browse-link" href="__BROWSE_ITEMS_URL__">Browse all reports &nbsp;→</a>
      </div>
    </section>
    <section class="light-section dashboard-section">
      <div class="section-inner">
        <div class="dashboard-grid">
          <article class="dashboard-card">
            <p class="eyebrow">For students and staff</p>
            <h2>One dashboard for every report.</h2>
            <p>Edit or delete reports, track status, monitor claims, and see new smart matches as the catalog grows.</p>
            <a class="dashboard-action" href="__USER_DASHBOARD_URL__">Open your dashboard &nbsp;→</a>
          </article>
          <article class="dashboard-card secondary">
            <p class="eyebrow">For campus teams</p>
            <h2>Central report management.</h2>
            <p>Authorized staff can manage reports, categories, buildings, claim reviews, and item statuses in Payload Admin.</p>
            <a href="/admin/">Open staff admin &nbsp;→</a>
          </article>
        </div>
      </div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-about">
        <div class="footer-brand">⌕ &nbsp; FindIt</div>
        <p>A campus-powered network that helps lost belongings make their way home safely.</p>
      </div>
      <div class="footer-column">
        <h2>Take action</h2>
        <a href="__REPORT_URL__">Report a lost item</a>
        <a href="__FOUND_REPORT_URL__">Report a found item</a>
        <a href="__BROWSE_ITEMS_URL__">Search the catalog</a>
      </div>
      <div class="footer-column">
        <h2>Account</h2>
        <a href="__ACCOUNT_URL__">Register or log in</a>
        <a href="__DASHBOARD_URL__">Your dashboard</a>
        <a href="/admin/">Staff administration</a>
      </div>
    </div>
    <div class="wrap copyright">© __YEAR__ FindIt. Built for safer campus returns.</div>
  </footer>
  __THEME_SCRIPT__
</body>
</html>"""


def _report_card(report):
    image = (
        format_html('<img src="{}" alt="{}" loading="lazy">', report["image"], report["alt"])
        if report["image"]
        else format_html('<span class="placeholder" aria-hidden="true">{}</span>', "E")
    )
    badge_class = "report-badge lost" if report["type"] == "lost" else "report-badge"
    found_time = (
        format_html("<span>◷ &nbsp;{}</span>", report["time"])
        if report.get("time")
        else ""
    )
    details_link = format_html(
        '<span class="report-details-link">{}</span>',
        "View details →",
    )
    card = format_html(
        '<article class="report-card"><div class="report-image">{}'
        '<span class="{}">{}</span></div><div class="report-content">'
        '<p class="report-category">{}</p><h3>{}</h3><p class="report-description">{}</p>'
        '<div class="report-meta"><span>⌖ &nbsp;{}</span>{}<time datetime="{}">{}</time></div>{}'
        '</div></article>',
        image,
        badge_class,
        report["type"].title(),
        report["category"],
        report["title"],
        report["description"],
        report["building"],
        found_time,
        report["date"],
        date.fromisoformat(report["date"]).strftime("%m/%d/%Y"),
        details_link,
    )
    return format_html(
        '<a class="report-card-link" href="{}" aria-label="View details for {}">{}</a>',
        reverse("found_item_detail", args=(report["item_id"],)),
        report["title"],
        card,
    )


def _filter_form(request, action):
    selected_type = request.GET.get("type", "")
    selected_category = request.GET.get("category", "")
    selected_building = request.GET.get("building", "")
    search = request.GET.get("q", "")[:100]
    def options(values, selected):
        return format_html_join(
            "",
            '<option value="{}"{}>{}</option>',
            (
                (
                    value,
                    format_html("{}", " selected") if value == selected else "",
                    label,
                )
                for value, label in values
            ),
        )

    return format_html(
        '<form class="filters" action="{}" method="get">'
        '<label class="search-field"><span class="sr-only">Search reports</span>'
        '<input type="search" name="q" value="{}" placeholder="Search item details">'
        '<button class="filter-submit" type="submit" aria-label="Search reports">⌕</button></label>'
        '<label><span class="sr-only">Report type</span><select name="type">{}</select></label>'
        '<label><span class="sr-only">Category</span><select name="category">{}</select></label>'
        '<label><span class="sr-only">Building</span><select name="building">{}</select></label>'
        '<label><span class="sr-only">Sort</span><select name="sort">{}</select></label>'
        '</form>',
        action,
        search,
        options((("", "Report type"), ("lost", "Lost"), ("found", "Found")), selected_type),
        options(
            (("", "Category"),) + tuple(sorted(ITEM_CATEGORY_CHOICES)),
            selected_category,
        ),
        options(
            (("", "Building"),) + BUILDING_CHOICES,
            selected_building,
        ),
        options((("newest", "Newest"), ("oldest", "Oldest"), ("title", "Title")), request.GET.get("sort", "newest")),
    )


def _catalog_reports():
    reports = [
        {**report, "item_id": f"sample-{index}"}
        for index, report in enumerate(REPORTS)
    ]
    reports.extend(
        {
            "type": item.report_type,
            "item_id": str(item.pk),
            "category": item.category,
            "title": item.item_name,
            "description": " ".join(
                part for part in (item.specific_area, item.description) if part
            ),
            "building": item.location,
            "date": item.date_found.isoformat(),
            "time": (
                item.time_found.strftime("%I:%M %p").lstrip("0")
                if item.time_found
                else ""
            ),
            "image": (
                reverse("found_item_image", args=(item.pk,))
                if item.image and item.image_approved
                else ""
            ),
            "alt": item.item_name,
        }
        for item in FoundItem.objects.all()
    )
    return reports


def _filter_reports(request, reports):
    selected_type = request.GET.get("type", "")
    selected_category = request.GET.get("category", "")
    selected_building = request.GET.get("building", "")
    search = request.GET.get("q", "").strip()[:100].casefold()
    reports = [
        report for report in reports
        if (not selected_type or report["type"] == selected_type)
        and (not selected_category or report["category"] == selected_category)
        and (not selected_building or report["building"] == selected_building)
        and (
            not search
            or search in " ".join(
                (report["title"], report["description"], report["category"], report["building"])
            ).casefold()
        )
    ]
    sort = request.GET.get("sort", "newest")
    if sort == "oldest":
        reports.sort(key=lambda report: report["date"])
    elif sort == "title":
        reports.sort(key=lambda report: report["title"].casefold())
    else:
        reports.sort(key=lambda report: report["date"], reverse=True)
    return reports


def _report_cards_markup(reports):
    if reports:
        return format_html_join("", "{}", ((_report_card(report),) for report in reports))
    return format_html(
        '<p class="empty-state">{}</p>',
        "No reports match those filters. Try another search.",
    )


def _account_navigation(request):
    account_url = reverse("login")
    dashboard_url = reverse("user_dashboard")
    dashboard_login_url = f"{account_url}?next={dashboard_url}"
    account_link = (
        format_html(
            '<details class="account-menu"><summary>Welcome, <span class="account-username">{}</span>!</summary>'
            '<div class="account-menu-panel"><a href="{}">Your dashboard</a>'
            '<form action="{}" method="post">{}'
            '<button type="submit">Log out</button></form></div></details>',
            request.user.get_username(),
            dashboard_url,
            reverse("logout"),
            csrf_input(request),
        )
        if request.user.is_authenticated
        else format_html('<a href="{}">Log in</a>', account_url)
    )
    return (
        account_link,
        account_url,
        dashboard_url if request.user.is_authenticated else dashboard_login_url,
    )


BROWSE_ITEMS_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#014d48">
  <meta name="description" content="Search and filter lost and found reports from the campus community.">
  <title>Browse items | FindIt</title>
  <style>
    :root {
      color-scheme: dark; --teal: #014d48; --teal-bright: #66d8c6; --paper: #fff;
      --ink: #171b1b; --muted: #64716e; --line: #e5e9e8; --card: #fff;
      --section-muted: rgba(255,255,255,.78);
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh; margin: 0; background: var(--teal); color: #fff;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light {
      color-scheme: light; --teal: #e5f4f0; --teal-bright: #087c70;
      --paper: #f7faf9; --ink: #143b37; --muted: #596b67; --line: #dce8e5;
      --section-muted: rgba(20,59,55,.78); background: var(--teal); color: var(--ink);
    }
    body.theme-dark {
      color-scheme: dark; --teal: #0b211f; --teal-bright: #66d8c6; --paper: #111918;
      --ink: #eef5f3; --muted: #b3c0bd; --line: #34423f; --card: #111918;
      --section-muted: rgba(238,245,243,.76); color: var(--ink);
    }
    a { color: inherit; }
    button, input, select { font: inherit; }
    .wrap { width: min(1280px, calc(100% - 64px)); margin-inline: auto; }
    .site-header { position: sticky; z-index: 10; top: 0; border-bottom: 1px solid rgba(255,255,255,.1); background: rgba(9,10,11,.96); color: #fff; backdrop-filter: blur(14px); }
    .header-inner { display: grid; min-height: 64px; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 24px; }
    .brand { display: inline-flex; align-items: center; gap: 10px; justify-self: start; color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .brand-mark { position: relative; display: grid; width: 36px; height: 36px; place-items: center; border-radius: 12px; background: #075d56; }
    .brand-mark::before { width: 13px; height: 13px; transform: translate(-2px,-2px); border: 2.5px solid #fff; border-radius: 50%; content: ""; }
    .brand-mark::after { position: absolute; width: 7px; height: 2.5px; transform: translate(5px,5px) rotate(45deg); border-radius: 2px; background: #fff; content: ""; }
    .primary-nav, .header-actions { display: flex; align-items: center; gap: 24px; }
    .primary-nav { justify-self: center; }
    .header-actions { justify-self: end; }
    .primary-nav a, .header-actions a { color: #f7f7f7; font-size: .9rem; font-weight: 600; text-decoration: none; }
    .primary-nav a:hover, .header-actions a:hover { color: var(--teal-bright); }
    .header-actions form { margin: 0; }
    .header-actions form button { padding: 0; border: 0; background: none; color: #f7f7f7; font-weight: 650; cursor: pointer; }
    .theme-link { border: 0; background: transparent; color: #fff; font-size: 1.2rem; cursor: pointer; }
    .account-menu { position: relative; }
    .account-menu summary { padding: 6px 9px; border-radius: 8px; color: #f7f7f7; font-size: .9rem; font-weight: 600; cursor: pointer; list-style: none; }
    .account-menu summary::-webkit-details-marker { display: none; }
    .account-menu-panel { position: absolute; z-index: 20; top: 100%; right: 0; display: none; min-width: 180px; gap: 12px; padding: 14px; border: 1px solid #34423f; border-radius: 12px; background: #090a0b; box-shadow: 0 12px 28px rgba(0,0,0,.25); }
    .account-menu:hover .account-menu-panel, .account-menu:focus-within .account-menu-panel, .account-menu[open] .account-menu-panel { display: grid; }
    .account-menu-panel a, .account-menu-panel form button { color: #f7f7f7; font: inherit; text-align: left; }
    .account-menu-panel form button:hover { color: var(--teal-bright); }
    .header-actions .header-cta { padding: 9px 18px; border-radius: 999px; background: #fff; color: #014d48; font-weight: 750; }
    body.theme-dark .header-actions .header-cta { border: 1px solid #34786f; background: #075d56; color: #eef5f3; }
    main { width: min(1280px, calc(100% - 64px)); margin: 0 auto; padding: 40px 0 76px; }
    .page-heading { margin-bottom: 28px; }
    .eyebrow { margin: 0 0 6px; color: var(--teal-bright); font-size: .78rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
    h1 { margin: 0; font-size: clamp(2.2rem, 4vw, 3.2rem); letter-spacing: -.045em; line-height: 1.12; }
    .catalog-panel { padding: clamp(22px, 4vw, 36px); border: 1px solid rgba(255,255,255,.12); border-radius: 24px; background: var(--paper); color: var(--ink); }
    .catalog-heading { max-width: 760px; margin-bottom: 26px; }
    .catalog-heading .eyebrow { margin-bottom: 4px; color: var(--teal-bright); }
    .catalog-heading h2 { margin: 0 0 8px; font-size: clamp(1.7rem, 3vw, 2.3rem); letter-spacing: -.035em; line-height: 1.18; }
    .catalog-heading p:last-child { margin: 0; color: var(--muted); }
    .filters {
      display: grid; grid-template-columns: minmax(180px, 2fr) repeat(4, minmax(105px, 1fr));
      align-items: center; gap: 12px; margin-bottom: 24px; padding: 16px;
      border: 1px solid var(--line); border-radius: 18px; background: #fff; color: #171b1b;
    }
    .filters label { display: block; color: #58625f; font-size: .73rem; font-weight: 700; }
    .sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; clip-path: inset(50%); }
    .filters input, .filters select {
      width: 100%; min-height: 44px; padding: 9px 12px; border: 1px solid #dfe4e2;
      border-radius: 12px; background: #fff; color: #171b1b;
    }
    .filters select {
      padding-right: 36px; appearance: none;
      background-image: linear-gradient(45deg, transparent 50%, currentColor 50%), linear-gradient(135deg, currentColor 50%, transparent 50%);
      background-repeat: no-repeat; background-position: calc(100% - 17px) 50%, calc(100% - 13px) 50%; background-size: 4px 4px;
    }
    .search-field { position: relative; }
    .filters .search-field input { padding-right: 48px; }
    .filters input:focus, .filters select:focus { outline: 2px solid #43b9a7; outline-offset: 1px; }
    .filter-submit { position: absolute; top: 6px; right: 6px; width: 32px; min-height: 32px; padding: 0; border: 0; border-radius: 8px; background: #003e3a; color: #fff; font-weight: 750; cursor: pointer; }
    .report-summary { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin: 0 0 18px; }
    .report-summary strong { font-size: .95rem; }
    .report-summary span { color: var(--muted); font-size: .86rem; }
    .report-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 20px; }
    .report-card-link { display: block; min-width: 0; color: inherit; text-decoration: none; }
    .report-card { overflow: hidden; border: 1px solid var(--line); border-radius: 18px; background: var(--card); color: var(--ink); box-shadow: 0 8px 24px rgba(0,0,0,.1); transition: transform 160ms ease, box-shadow 160ms ease; }
    .report-card:hover { transform: translateY(-4px); box-shadow: 0 14px 32px rgba(0,0,0,.18); }
    .report-image { position: relative; display: grid; height: 190px; place-items: center; overflow: hidden; background: #102a28; }
    .report-image img { width: 100%; height: 100%; object-fit: cover; }
    .report-image .placeholder { color: rgba(255,255,255,.8); font-size: 2.3rem; font-weight: 800; }
    .report-badge { position: absolute; top: 14px; left: 14px; padding: 5px 13px; border-radius: 999px; background: #72e1d0; color: #064943; font-size: .75rem; font-weight: 800; }
    .report-badge.lost { background: #ffd84c; color: #352b00; }
    .report-content { padding: 18px; }
    .report-category { margin: 0 0 6px; color: #087c70; font-size: .7rem; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; }
    .report-content h3 { margin: 0 0 8px; font-size: 1.06rem; line-height: 1.3; }
    .report-description { min-height: 54px; margin: 0 0 14px; color: var(--muted); font-size: .85rem; }
    .report-meta { display: flex; flex-wrap: wrap; justify-content: space-between; gap: 6px; color: var(--muted); font-size: .77rem; }
    .report-details-link { display: flex; justify-content: space-between; margin-top: 20px; padding: 14px 16px; border-radius: 14px; background: #f3f4f3; color: #1b2221; font-weight: 750; }
    .report-card-link:hover .report-details-link { background: #e8f8f4; color: #087c70; }
    .report-card-link:focus-visible { outline: 3px solid #43b9a7; outline-offset: 4px; border-radius: 18px; }
    .empty-state { grid-column: 1 / -1; padding: 32px; border: 1px dashed var(--line); border-radius: 18px; color: var(--muted); text-align: center; }
    body.theme-dark .filters { border-color: #34423f; background: #111918; color: #eef5f3; }
    body.theme-dark .filters label { color: #c1ceca; }
    body.theme-dark .filters input,
    body.theme-dark .filters select { border-color: #34423f; background-color: #192321; color: #eef5f3; color-scheme: dark; }
    body.theme-dark .report-category { color: #8ce8d8; }
    body.theme-dark .report-details-link { background: #111918; color: #eef5f3; }
    body.theme-dark .report-card-link:hover .report-details-link { background: #263a36; color: #8ce8d8; }
    .site-footer { background: #090a0b; color: #b6c0be; }
    .footer-inner { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 40px; padding-block: 42px 24px; }
    .footer-brand { color: #fff; font-size: 1.15rem; font-weight: 800; }
    .footer-about p { max-width: 360px; margin: 10px 0 0; color: #a4afac; font-size: .88rem; }
    .footer-column h2 { margin: 0 0 12px; color: #fff; font-size: .86rem; }
    .footer-column a { display: block; margin: 7px 0; color: #b6c0be; font-size: .85rem; text-decoration: none; }
    .footer-column a:hover { color: #8ce8d8; }
    .copyright { padding: 16px 0 22px; border-top: 1px solid #252a2a; color: #9ba5a3; font-size: .78rem; text-align: center; }
    @media (max-width: 1120px) {
      .header-inner { display: flex; flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; }
    }
    @media (max-width: 1000px) { .report-grid { grid-template-columns: repeat(2, minmax(0,1fr)); } }
    @media (max-width: 860px) {
      .filters { grid-template-columns: repeat(2, minmax(0,1fr)); }
      .search-field { grid-column: 1 / -1; }
      .primary-nav, .header-actions { gap: 14px; }
    }
    @media (max-width: 700px) {
      .wrap, main { width: min(100% - 36px, 560px); }
      .header-inner { flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; gap: 10px; }
      .primary-nav a { font-size: .78rem; }
      .header-actions { gap: 12px; }
      .header-actions .header-cta { padding: 8px 12px; font-size: .78rem; }
      main { padding: 30px 0 50px; }
      .report-grid { grid-template-columns: 1fr; }
      .footer-inner { grid-template-columns: 1fr 1fr; gap: 24px; }
      .footer-about { grid-column: 1 / -1; }
    }
    @media (max-width: 390px) {
      .primary-nav { flex-wrap: wrap; justify-content: center; column-gap: 14px; }
      .header-actions a:not(.header-cta) { font-size: .8rem; }
      .filters { grid-template-columns: 1fr; }
      .search-field { grid-column: auto; }
      .footer-inner { grid-template-columns: 1fr; }
      .footer-about { grid-column: auto; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home"><span class="brand-mark" aria-hidden="true"></span>FindIt</a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="__HOME_URL__#how-it-works">How it works</a>
        <a href="__BROWSE_ITEMS_URL__" aria-current="page">Browse items</a>
      </nav>
      <div class="header-actions">
        <button class="theme-link" type="button" data-theme-toggle aria-label="Switch to light mode" aria-pressed="false">☀</button>
        __ACCOUNT_LINK__
        <a class="header-cta" href="__FOUND_REPORT_URL__">Report an item</a>
      </div>
    </div>
  </header>
  <main>
    <header class="page-heading">
      <p class="eyebrow">Campus inventory</p>
      <h1>Find what went missing.</h1>
    </header>
    <section class="catalog-panel" aria-labelledby="catalog-heading">
      <div class="catalog-heading">
        <p class="eyebrow">Live campus catalog</p>
        <h2 id="catalog-heading">Search lost and found reports</h2>
        <p>Filter by item type, category, or campus building. Every report is managed by its owner and tracked through a verified return workflow.</p>
      </div>
      __FILTERS__
      <div class="report-summary">
        <strong>__REPORT_COUNT__ active reports</strong>
        <span>✳ &nbsp;Smart matches compare category, place, date, and description</span>
      </div>
      <div class="report-grid">__REPORT_CARDS__</div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-about">
        <div class="footer-brand">⌕ &nbsp; FindIt</div>
        <p>A campus-powered network that helps lost belongings make their way home safely.</p>
      </div>
      <div class="footer-column">
        <h2>Take action</h2>
        <a href="__REPORT_URL__">Report a lost item</a>
        <a href="__FOUND_REPORT_URL__">Report a found item</a>
        <a href="__BROWSE_ITEMS_URL__">Search the catalog</a>
      </div>
      <div class="footer-column">
        <h2>Account</h2>
        <a href="__ACCOUNT_URL__">Register or log in</a>
        <a href="__DASHBOARD_URL__">Your dashboard</a>
        <a href="/admin/">Staff administration</a>
      </div>
    </div>
    <div class="wrap copyright">© __YEAR__ FindIt. Built for safer campus returns.</div>
  </footer>
  __THEME_SCRIPT__
</body>
</html>"""


def home_page(request):
    reports = _filter_reports(request, _catalog_reports())
    visible_reports = random.sample(reports, min(6, len(reports)))
    sort = request.GET.get("sort", "newest")
    if sort == "oldest":
        visible_reports.sort(key=lambda report: report["date"])
    elif sort == "title":
        visible_reports.sort(key=lambda report: report["title"].casefold())

    account_link, account_url, dashboard_url = _account_navigation(request)
    page = HOME_PAGE
    for placeholder, value in (
        ("__THEME__", "theme-dark"),
        ("__THEME_SCRIPT__", _theme_script()),
        ("__ACCOUNT_LINK__", str(account_link)),
        ("__ACCOUNT_URL__", account_url),
        ("__DASHBOARD_URL__", dashboard_url),
        ("__USER_DASHBOARD_URL__", reverse("user_dashboard")),
        ("__REPORT_URL__", f'{reverse("found_report")}?type=lost'),
        ("__FOUND_REPORT_URL__", reverse("found_report")),
        ("__BROWSE_ITEMS_URL__", reverse("browse_items")),
        ("__FILTERS__", str(_filter_form(request, "#recent-items"))),
        ("__REPORT_COUNT__", str(len(reports))),
        ("__DISPLAY_COUNT__", str(len(visible_reports))),
        ("__REPORT_CARDS__", str(_report_cards_markup(visible_reports))),
        ("__YEAR__", str(date.today().year)),
    ):
        page = page.replace(placeholder, value)
    return page


def browse_items_page(request):
    reports = _filter_reports(request, _catalog_reports())
    account_link, account_url, dashboard_url = _account_navigation(request)
    page = BROWSE_ITEMS_PAGE
    for placeholder, value in (
        ("__HOME_URL__", reverse("home")),
        ("__ACCOUNT_LINK__", str(account_link)),
        ("__ACCOUNT_URL__", account_url),
        ("__DASHBOARD_URL__", dashboard_url),
        ("__REPORT_URL__", f'{reverse("found_report")}?type=lost'),
        ("__FOUND_REPORT_URL__", reverse("found_report")),
        ("__BROWSE_ITEMS_URL__", reverse("browse_items")),
        ("__FILTERS__", str(_filter_form(request, reverse("browse_items")))),
        ("__REPORT_COUNT__", str(len(reports))),
        ("__REPORT_CARDS__", str(_report_cards_markup(reports))),
        ("__YEAR__", str(date.today().year)),
        ("__THEME_SCRIPT__", _theme_script()),
    ):
        page = page.replace(placeholder, value)
    return page


FOUND_ITEM_DETAIL_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#014d48">
  <title>__ITEM_TITLE__ | FindIt</title>
  <style>
    :root {
      color-scheme: dark;
      --paper: #0b211f;
      --card: #111918;
      --ink: #eef5f3;
      --muted: #b3c0bd;
      --line: #34423f;
      --accent: #8ce8d8;
      --button: #075d56;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh; margin: 0; background: var(--paper); color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light { color-scheme: light; --paper: #f3f8f6; --card: #fff; --ink: #163d38; --muted: #596b67; --line: #dce8e5; --accent: #087c70; }
    a { color: var(--accent); }
    button, textarea { font: inherit; }
    .site-header { background: #090a0b; color: #fff; }
    .wrap { width: min(1280px, calc(100% - 64px)); margin-inline: auto; }
    .header-inner {
      display: grid; min-height: 64px; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 24px;
    }
    .brand { display: inline-flex; align-items: center; gap: 10px; justify-self: start; color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .brand-mark {
      position: relative; display: grid; width: 36px; height: 36px; place-items: center;
      border-radius: 12px; background: #075d56; color: #fff; font-size: 0;
    }
    .brand-mark::before { width: 13px; height: 13px; transform: translate(-2px, -2px); border: 2.5px solid currentColor; border-radius: 50%; content: ""; }
    .brand-mark::after { position: absolute; width: 7px; height: 2.5px; transform: translate(5px, 5px) rotate(45deg); border-radius: 2px; background: currentColor; content: ""; }
    .primary-nav, .header-actions { display: flex; align-items: center; gap: 20px; }
    .primary-nav { justify-self: center; }
    .header-actions { justify-self: end; }
    .primary-nav a, .header-actions a { color: #fff; font-weight: 650; text-decoration: none; }
    .primary-nav a:hover, .header-actions a:hover { color: #8ce8d8; }
    .header-actions .header-cta { padding: 9px 18px; border-radius: 999px; background: #fff; color: #064d47; }
    body.theme-dark .header-actions .header-cta { border: 1px solid #34786f; background: #075d56; color: #eef5f3; }
    .theme-toggle { padding: 0; border: 0; background: transparent; color: #fff; font-size: 1.2rem; cursor: pointer; }
    main { width: min(1280px, calc(100% - 64px)); margin: 30px auto 80px; }
    .back-link { display: inline-flex; margin-bottom: 20px; color: #fff; font-weight: 700; text-decoration: none; }
    body.theme-light .back-link { color: var(--accent); }
    .detail-grid { display: grid; grid-template-columns: minmax(0, 1.1fr) minmax(360px, .9fr); align-items: start; gap: 28px; }
    .item-detail-card, .request-panel {
      overflow: hidden; border-radius: 24px; background: var(--card); box-shadow: 0 18px 45px rgba(0,0,0,.12);
    }
    .item-image {
      position: relative; display: grid; min-height: 360px; place-items: center;
      background: linear-gradient(135deg, #dce5e2, #f3f5f4); color: #48716b;
    }
    body.theme-dark .item-image { background: linear-gradient(135deg, #192321, #111918); color: #8ce8d8; }
    .item-image img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
    .image-placeholder { font-size: clamp(5rem, 14vw, 11rem); font-weight: 800; opacity: .35; }
    .item-badge {
      position: absolute; z-index: 1; top: 20px; left: 22px; padding: 7px 18px;
      border-radius: 999px; background: #72e1d0; color: #064943; font-weight: 800;
    }
    .item-content { padding: clamp(24px, 4vw, 48px); }
    .item-category { margin: 0 0 8px; color: var(--accent); font-size: .84rem; font-weight: 850; letter-spacing: .1em; text-transform: uppercase; }
    h1 { margin: 0; font-size: clamp(2rem, 4.5vw, 3.2rem); letter-spacing: -.04em; line-height: 1.16; }
    .item-description { margin: 16px 0 28px; color: var(--muted); font-size: 1.1rem; white-space: pre-line; }
    .item-facts {
      display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px;
      margin: 0; padding: 20px; border-radius: 16px; background: #f5f6f5;
    }
    body.theme-light .item-facts { background: #f3f8f6; }
    body.theme-dark .item-facts { background: #111918; }
    .item-facts div { min-width: 0; }
    .item-facts dt { color: var(--muted); font-size: .78rem; font-weight: 750; }
    .item-facts dd { margin: 2px 0 0; font-weight: 700; overflow-wrap: anywhere; }
    .request-panel { padding: clamp(24px, 4vw, 48px); }
    .request-icon {
      display: grid; width: 58px; height: 58px; margin-bottom: 18px; place-items: center;
      border-radius: 18px; background: #effbf8; color: #064d47; font-size: 1.5rem; font-weight: 800;
    }
    body.theme-dark .request-icon { background: #263a36; color: #8ce8d8; }
    .request-panel h2 { margin: 0; font-size: clamp(1.6rem, 3vw, 2.2rem); letter-spacing: -.03em; line-height: 1.2; }
    .request-intro { margin: 12px 0 26px; color: var(--muted); font-size: 1rem; }
    .ownership-question { margin: 0 0 18px; padding: 14px; border-radius: 12px; background: #eaf7f4; color: #173d38; }
    .ownership-question p { margin: 6px 0 0; }
    body.theme-dark .ownership-question { background: #263a36; color: #eef5f3; }
    .notice { margin: 0 0 18px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 12px; background: #f5faf8; }
    body.theme-dark .notice { background: #111918; color: var(--ink); }
    .inquiry-form label { display: block; margin-bottom: 8px; font-weight: 750; }
    .inquiry-input {
      display: block; width: 100%; min-height: 150px; padding: 14px 16px; resize: vertical;
      border: 1px solid #d5ddda; border-radius: 16px; background: #fff; color: #17201e;
    }
    body.theme-dark .inquiry-input { border-color: #34423f; background: #192321; color: #eef5f3; color-scheme: dark; }
    .inquiry-input:focus { outline: 3px solid #72e1d0; outline-offset: 2px; }
    .field-errors { margin: 6px 0 0; padding-left: 20px; color: #b42318; font-size: .86rem; }
    .submit-request, .login-request {
      display: block; width: 100%; min-height: 58px; margin-top: 22px; padding: 13px 18px;
      border: 0; border-radius: 14px; background: var(--button); color: #fff;
      font-weight: 800; text-align: center; text-decoration: none; cursor: pointer;
    }
    .request-private-note, .request-blocked { margin: 14px 0 0; color: var(--muted); font-size: .85rem; }
    .site-footer { background: #090a0b; color: #b6c0be; }
    .footer-inner { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 40px; padding-block: 42px 24px; }
    .footer-brand { color: #fff; font-size: 1.15rem; font-weight: 800; }
    .footer-about p { max-width: 360px; margin: 10px 0 0; color: #a4afac; font-size: .88rem; }
    .footer-column h2 { margin: 0 0 12px; color: #fff; font-size: .86rem; }
    .footer-column a { display: block; margin: 7px 0; color: #b6c0be; font-size: .85rem; text-decoration: none; }
    .footer-column a:hover { color: #8ce8d8; }
    .copyright { padding: 16px 0 22px; border-top: 1px solid #252a2a; color: #9ba5a3; font-size: .78rem; text-align: center; }
    @media (max-width: 1120px) {
      .header-inner { display: flex; flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; }
    }
    @media (max-width: 900px) {
      .detail-grid { grid-template-columns: 1fr; }
      .item-image { min-height: 300px; }
    }
    @media (max-width: 850px) {
      .primary-nav, .header-actions { gap: 14px; }
    }
    @media (max-width: 650px) {
      .wrap, main { width: calc(100% - 36px); }
      .header-inner { flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; gap: 8px; }
      .primary-nav a, .header-actions a { font-size: .76rem; }
      .header-actions { flex-wrap: wrap; gap: 12px; }
      main { margin-top: 22px; }
      .detail-grid { gap: 18px; }
      .item-image { min-height: 230px; }
      .item-facts { grid-template-columns: 1fr; }
      .footer-inner { grid-template-columns: 1fr 1fr; gap: 24px; }
      .footer-about { grid-column: 1 / -1; }
    }
    @media (max-width: 390px) {
      .primary-nav { flex-wrap: wrap; justify-content: center; column-gap: 14px; }
      .header-actions a:not(.header-cta) { font-size: .8rem; }
      .footer-inner { grid-template-columns: 1fr; }
      .footer-about { grid-column: auto; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home"><span class="brand-mark" aria-hidden="true"></span>FindIt</a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="__HOME_URL__#how-it-works">How it works</a>
        <a href="__BROWSE_ITEMS_URL__">Browse items</a>
      </nav>
      <nav class="header-actions" aria-label="Primary navigation">
        <button class="theme-toggle" type="button" data-theme-toggle
          aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__DASHBOARD_URL__">Dashboard</a>
        <a class="header-cta" href="__FOUND_REPORT_URL__">Report an item</a>
      </nav>
    </div>
  </header>
  <main>
    <a class="back-link" href="__BROWSE_ITEMS_URL__">← &nbsp; Back to all items</a>
    <div class="detail-grid">
      <article class="item-detail-card">
        <div class="item-image">
          <span class="item-badge">__ITEM_TYPE__</span>
          __ITEM_MEDIA__
        </div>
        <div class="item-content">
          <p class="item-category">__CATEGORY__</p>
          <h1>__ITEM_TITLE__</h1>
          <p class="item-description">__ITEM_DESCRIPTION__</p>
          <dl class="item-facts">
            <div><dt>__ITEM_LOCATION_LABEL__</dt><dd>__ITEM_LOCATION__</dd></div>
            <div><dt>__ITEM_DATE_LABEL__</dt><dd>__ITEM_DATE__</dd></div>
            __ITEM_TIME_FACT__
            __ITEM_SPECIFIC_AREA_FACT__
          </dl>
        </div>
      </article>
      <aside class="request-panel" aria-labelledby="request-heading">
        <div class="request-icon" aria-hidden="true">✓</div>
        <h2 id="request-heading">Request information privately</h2>
        <p class="request-intro">Your message will only be shared with the person who reported this item. Contact details stay private.</p>
        __OWNERSHIP_QUESTION__
        __NOTICES__
        __REQUEST_CONTENT__
      </aside>
    </div>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-about">
        <div class="footer-brand">⌕ &nbsp; FindIt</div>
        <p>A campus-powered network that helps lost belongings make their way home safely.</p>
      </div>
      <div class="footer-column">
        <h2>Take action</h2>
        <a href="__LOST_REPORT_URL__">Report a lost item</a>
        <a href="__FOUND_REPORT_URL__">Report a found item</a>
        <a href="__BROWSE_ITEMS_URL__">Search the catalog</a>
      </div>
      <div class="footer-column">
        <h2>Account</h2>
        <a href="__DASHBOARD_URL__">Your dashboard</a>
        <a href="/admin/">Staff administration</a>
      </div>
    </div>
    <div class="wrap copyright">© __YEAR__ FindIt. Built for safer campus returns.</div>
  </footer>
  __THEME_SCRIPT__
</body>
</html>"""


def found_item_detail_page(request, item, form, request_status):
    notices = format_html_join(
        "",
        '<p class="notice" role="status">{}</p>',
        ((message,) for message in get_messages(request)),
    )
    if request_status == "available":
        message = form["message"]
        field_errors = (
            format_html(
                '<ul id="message-errors" class="field-errors" role="alert">{}</ul>',
                message.errors,
            )
            if message.errors
            else ""
        )
        request_content = format_html(
            '<form class="inquiry-form" action="{}" method="post" '
            'onsubmit="const button=this.querySelector(\'.submit-request\');'
            'if(button.disabled)return false;button.disabled=true;'
            'button.textContent=\'Sending...\';">{}'
            '<input type="hidden" name="submission_id" value="{}">'
            '<label for="{}">Your message</label>{}{}'
            '<button class="submit-request" type="submit">Send private request</button>'
            '<p class="request-private-note">Only the item reporter can read your request.</p></form>',
            reverse("request_found_item_information", args=(item.pk,)),
            csrf_input(request),
            uuid4().hex,
            message.id_for_label,
            message.as_widget(
                attrs={
                    "class": "inquiry-input",
                    "placeholder": "Ask a question or describe what you would like to know.",
                    "aria-invalid": "true" if message.errors else "false",
                    **({"aria-describedby": "message-errors"} if message.errors else {}),
                },
            ),
            field_errors,
        )
    elif request_status == "own":
        request_content = format_html(
            '<p class="request-blocked">{}</p>',
            "You reported this item, so you cannot send a request to yourself.",
        )
    elif request_status == "login":
        login_url = (
            f'{reverse("login")}?next={reverse("found_item_detail", args=(item.pk,))}'
        )
        request_content = format_html(
            '<p class="request-blocked">Log in to send a private request to the reporter.</p>'
            '<a class="login-request" href="{}">Log in to request information</a>',
            login_url,
        )
    else:
        request_content = format_html(
            '<p class="request-blocked">{}</p>',
            "This sample listing has no reporter account. Private requests are "
            "available on saved found-item reports.",
        )
    if isinstance(item, FoundItem):
        item_details = {
            "title": item.item_name,
            "initial": item.item_name[:1].upper(),
            "category": item.category,
            "description": item.description or "No description was provided.",
            "location": item.location,
            "date": date_format(item.date_found, "m/d/Y"),
            "time": (
                item.time_found.strftime("%I:%M %p").lstrip("0")
                if item.time_found
                else ""
            ),
            "specific_area": item.specific_area,
            "type": f'{item.get_report_type_display()} item',
            "location_label": (
                "Building lost" if item.report_type == "lost" else "Building found"
            ),
            "date_label": (
                "Date lost" if item.report_type == "lost" else "Date found"
            ),
            "time_label": (
                "Time lost" if item.report_type == "lost" else "Time found"
            ),
            "image": (
                reverse("found_item_image", args=(item.pk,))
                if item.image and item.image_approved
                else ""
            ),
            "alt": item.item_name,
        }
        ownership_question = (
            format_html(
                '<div class="ownership-question"><strong>To verify that this is yours, answer privately:</strong><p>{}</p>'
                '<p>Include your answer in your private request.</p></div>',
                item.ownership_question,
            )
            if item.report_type == "found" and item.ownership_question
            else ""
        )
    else:
        item_details = {
            "title": item["title"],
            "initial": item["title"][:1].upper(),
            "category": item["category"],
            "description": item["description"] or "No description was provided.",
            "location": item["building"],
            "date": date.fromisoformat(item["date"]).strftime("%m/%d/%Y"),
            "time": item.get("time", "Not provided"),
            "specific_area": "",
            "type": f'{item["type"].title()} item',
            "location_label": (
                "Building lost" if item["type"] == "lost" else "Building found"
            ),
            "date_label": (
                "Date lost" if item["type"] == "lost" else "Date found"
            ),
            "time_label": (
                "Time lost" if item["type"] == "lost" else "Time found"
            ),
            "image": item["image"],
            "alt": item["alt"],
        }
        ownership_question = ""
    item_media = (
        format_html(
            '<img src="{}" alt="{}">',
            item_details["image"],
            item_details["alt"],
        )
        if item_details["image"]
        else format_html(
            '<span class="image-placeholder" aria-hidden="true">{}</span>',
            item_details["initial"],
        )
    )
    replacements = {
        "__HOME_URL__": reverse("home"),
        "__BROWSE_ITEMS_URL__": reverse("browse_items"),
        "__DASHBOARD_URL__": (
            reverse("user_dashboard")
            if request.user.is_authenticated
            else reverse("login")
        ),
        "__LOST_REPORT_URL__": f'{reverse("found_report")}?type=lost',
        "__FOUND_REPORT_URL__": reverse("found_report"),
        "__YEAR__": str(date.today().year),
        "__ITEM_MEDIA__": str(item_media),
        "__ITEM_TYPE__": format_html("{}", item_details["type"]),
        "__ITEM_TITLE__": format_html("{}", item_details["title"]),
        "__CATEGORY__": format_html("{}", item_details["category"]),
        "__ITEM_DESCRIPTION__": format_html("{}", item_details["description"]),
        "__ITEM_LOCATION__": format_html("{}", item_details["location"]),
        "__ITEM_LOCATION_LABEL__": item_details["location_label"],
        "__ITEM_DATE_LABEL__": item_details["date_label"],
        "__ITEM_DATE__": item_details["date"],
        "__ITEM_TIME_FACT__": (
            format_html(
                '<div><dt>{}</dt><dd>{}</dd></div>',
                item_details["time_label"],
                item_details["time"],
            )
            if item_details["time"]
            else ""
        ),
        "__ITEM_SPECIFIC_AREA_FACT__": (
            format_html(
                '<div><dt>Specific area</dt><dd>{}</dd></div>',
                item_details["specific_area"],
            )
            if item_details["specific_area"]
            else ""
        ),
        "__NOTICES__": str(notices),
        "__OWNERSHIP_QUESTION__": str(ownership_question),
        "__REQUEST_CONTENT__": str(request_content),
        "__THEME_SCRIPT__": _theme_script(),
    }
    return re.sub(
        r"__[A-Z_]+__",
        lambda match: str(replacements[match.group(0)]),
        FOUND_ITEM_DETAIL_PAGE,
    )


FOUND_ITEM_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#014d48">
  <title>__PAGE_TITLE__ | FindIt</title>
  <style>
    :root {
      color-scheme: light;
      --teal: #014d48;
      --teal-bright: #78ddca;
      --paper: #fff;
      --ink: #171b1b;
      --muted: #64716e;
      --line: #e4e6e5;
      --accent: #087c70;
      --action-green: #014d48;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh; margin: 0; background: var(--teal); color: #fff;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light {
      color-scheme: light; --teal: #e5f4f0; --teal-bright: #087c70;
      --ink: #143b37; --muted: #596b67; --line: #dce8e5; --accent: #087c70;
      background: var(--teal); color: var(--ink);
    }
    body.theme-dark {
      color-scheme: dark; --teal: #0b211f; --teal-bright: #66d8c6; --paper: #111918;
      --ink: #eef5f3; --muted: #b3c0bd; --line: #34423f; --accent: #8ce8d8;
      --action-green: #075d56; background: var(--teal); color: var(--ink);
    }
    a { color: var(--accent); }
    button, input, select, textarea { font: inherit; }
    .wrap { width: min(1280px, calc(100% - 64px)); margin-inline: auto; }
    .site-header { position: sticky; z-index: 10; top: 0; background: #090a0b; color: #fff; }
    .header-inner {
      display: grid; min-height: 64px; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 24px;
    }
    .brand { display: inline-flex; align-items: center; gap: 10px; justify-self: start; color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .brand-mark {
      position: relative; display: grid; width: 36px; height: 36px; place-items: center;
      border-radius: 12px; background: #075d56; color: #fff; font-size: 0;
    }
    .brand-mark::before { width: 13px; height: 13px; transform: translate(-2px, -2px); border: 2.5px solid currentColor; border-radius: 50%; content: ""; }
    .brand-mark::after { position: absolute; width: 7px; height: 2.5px; transform: translate(5px, 5px) rotate(45deg); border-radius: 2px; background: currentColor; content: ""; }
    .primary-nav, .header-actions { display: flex; align-items: center; gap: 22px; }
    .primary-nav { justify-self: center; }
    .header-actions { justify-self: end; }
    .primary-nav a, .header-actions a { color: #f7f7f7; font-size: .9rem; font-weight: 650; text-decoration: none; }
    .primary-nav a:hover, .header-actions a:hover { color: var(--teal-bright); }
    .header-actions form { margin: 0; }
    .header-actions form button { padding: 0; border: 0; background: none; color: #fff; font-weight: 650; cursor: pointer; }
    .theme-toggle { padding: 0; border: 0; background: transparent; color: #fff; font-size: 1.2rem; cursor: pointer; }
    .header-actions .header-cta {
      padding: 9px 18px; border-radius: 999px; background: #fff; color: var(--action-green);
      font-weight: 750;
    }
    body.theme-dark .header-actions .header-cta { border: 1px solid #34786f; background: #075d56; color: #eef5f3; }
    main { width: min(1280px, calc(100% - 64px)); margin: 0 auto; padding: 52px 0 76px; }
    .report-layout { display: grid; grid-template-columns: minmax(0, .9fr) minmax(480px, 1.1fr); align-items: start; gap: 56px; }
    .report-copy {
      max-width: 560px; align-self: start;
      margin-top: clamp(0px, calc(50vh - 416px), 160px);
      padding: clamp(24px, 3vw, 36px);
      border: 1px solid rgba(102,216,198,.3); border-radius: 24px;
      background: #123a35; box-shadow: 0 20px 50px rgba(0,0,0,.2);
    }
    body.theme-light .report-copy {
      border-color: #c3dfd8; background: #fff;
      box-shadow: 0 20px 50px rgba(20,59,55,.12);
    }
    .eyebrow { margin: 0 0 14px; color: var(--teal-bright); font-size: .78rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
    h1 { max-width: 560px; margin: 0 0 16px; font-size: clamp(2.4rem, 4vw, 3.5rem); letter-spacing: -.045em; line-height: 1.08; }
    .intro { margin: 0 0 28px; color: rgba(255,255,255,.82); font-size: 1.02rem; }
    body.theme-light .intro { color: rgba(20,59,55,.78); }
    .report-benefits { display: grid; gap: 12px; }
    .report-benefits p { display: flex; align-items: center; gap: 11px; margin: 0; color: rgba(255,255,255,.92); font-weight: 650; }
    body.theme-light .report-benefits p { color: #24514b; }
    .report-benefits span { color: var(--teal-bright); font-size: 1.1rem; }
    .report-card { padding: clamp(26px, 4vw, 42px); border: 1px solid rgba(255,255,255,.9); border-radius: 24px; background: var(--paper); color: var(--ink); box-shadow: 0 24px 70px rgba(0,0,0,.14); }
    body.theme-dark .report-card { border-color: #34423f; }
    .report-form-heading { margin: 0 0 22px; color: var(--ink); font-size: 1.55rem; letter-spacing: -.03em; }
    .report-form-intro { margin: -12px 0 22px; color: var(--muted); font-size: .9rem; }
    .report-type { display: inline-flex; margin: 0 0 12px; padding: 6px 12px; border-radius: 999px; background: #eaf7f4; color: #087c70; font-size: .78rem; font-weight: 800; }
    body.theme-dark .report-type { background: #263a36; color: #8ce8d8; }
    .report-toggle { display: grid; grid-template-columns: repeat(2, 1fr); gap: 4px; margin: 0 0 20px; padding: 5px; border-radius: 14px; background: #edf2f0; }
    .report-toggle-option { padding: 12px 10px; border: 0; border-radius: 10px; background: transparent; color: #46534f; font: inherit; font-size: .9rem; font-weight: 750; text-align: center; cursor: pointer; }
    .report-toggle-option.active,
    .report-toggle-option[aria-pressed="true"] { background: #075d56; color: #fff; box-shadow: 0 2px 6px rgba(0,0,0,.12); }
    body.theme-dark .report-toggle { background: #192321; }
    body.theme-dark .report-toggle-option { color: #d4dfdc; }
    body.theme-dark .report-toggle-option.active,
    body.theme-dark .report-toggle-option[aria-pressed="true"] { background: #075d56; color: #fff; }
    .report-form [hidden] { display: none !important; }
    .report-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    .form-field { min-width: 0; }
    .form-field.full { grid-column: 1 / -1; }
    .form-field label { display: block; margin-bottom: 6px; color: #414648; font-size: .88rem; font-weight: 700; }
    body.theme-dark .form-field label { color: #d4dfdc; }
    .field-help { margin: 6px 0 0; color: var(--muted); font-size: .82rem; }
    .report-input {
      display: block; width: 100%; min-height: 48px; padding: 11px 13px;
      border: 1px solid #dedfdf; border-radius: 12px; background: #fff; color: #27292a;
    }
    body.theme-dark .report-input { border-color: #34423f; background: #192321; color: #eef5f3; color-scheme: dark; }
    textarea.report-input { min-height: 116px; resize: vertical; }
    .report-input:focus { border-color: #168b7d; outline: 3px solid rgba(22,139,125,.14); }
    .field-errors { margin: 6px 0 0; padding-left: 20px; color: #a52e28; font-size: .84rem; }
    .error-summary { grid-column: 1 / -1; margin: 0; color: #a52e28; }
    .notice { margin: 0 0 18px; padding: 12px 16px; border: 1px solid var(--line); border-radius: 12px; background: #f5faf8; color: var(--ink); }
    body.theme-dark .notice { background: #111918; }
    .submit-button {
      grid-column: 1 / -1; min-height: 48px; padding: 12px 20px; border: 0; border-radius: 12px;
      background: var(--action-green); color: #fff; font-weight: 800; cursor: pointer;
    }
    .submit-button:hover { background: #003e3a; }
    .form-footer { grid-column: 1 / -1; margin: 0; color: var(--muted); font-size: .84rem; }
    .site-footer { background: #090a0b; color: #b6c0be; }
    .footer-inner { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 40px; padding-block: 42px 24px; }
    .footer-brand { color: #fff; font-size: 1.15rem; font-weight: 800; }
    .footer-about p { max-width: 360px; margin: 10px 0 0; color: #a4afac; font-size: .88rem; }
    .footer-column h2 { margin: 0 0 12px; color: #fff; font-size: .86rem; }
    .footer-column a { display: block; margin: 7px 0; color: #b6c0be; font-size: .85rem; text-decoration: none; }
    .footer-column a:hover { color: #8ce8d8; }
    .copyright { padding: 16px 0 22px; border-top: 1px solid #252a2a; color: #9ba5a3; font-size: .78rem; text-align: center; }
    @media (max-width: 1120px) {
      .header-inner { display: flex; flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; }
    }
    @media (max-width: 900px) {
      .report-layout { grid-template-columns: 1fr; gap: 32px; }
      .report-copy { max-width: 720px; margin-top: 0; }
      .report-card { max-width: 760px; }
    }
    @media (max-width: 850px) {
      .primary-nav, .header-actions { gap: 14px; }
    }
    @media (max-width: 650px) {
      .wrap, main { width: calc(100% - 36px); }
      .header-inner { flex-wrap: wrap; gap: 10px; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; gap: 8px; }
      .primary-nav a, .header-actions a { font-size: .78rem; }
      .header-actions { gap: 12px; }
      .header-actions .header-cta { padding: 8px 11px; }
      main { padding: 34px 0 48px; }
      .report-card { padding: 24px; }
      .footer-inner { grid-template-columns: 1fr 1fr; gap: 24px; }
      .footer-about { grid-column: 1 / -1; }
    }
    @media (max-width: 560px) {
      .report-form { grid-template-columns: 1fr; }
      .form-field.full, .submit-button, .form-footer, .error-summary { grid-column: auto; }
    }
    @media (max-width: 390px) {
      .primary-nav { flex-wrap: wrap; justify-content: center; column-gap: 14px; }
      .header-actions a:not(.header-cta) { font-size: .8rem; }
      .footer-inner { grid-template-columns: 1fr; }
      .footer-about { grid-column: auto; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home"><span class="brand-mark" aria-hidden="true"></span>FindIt</a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="__HOME_URL__#how-it-works">How it works</a>
        <a href="__BROWSE_ITEMS_URL__">Browse items</a>
      </nav>
      <nav class="header-actions" aria-label="Account navigation">
        <button class="theme-toggle" type="button" data-theme-toggle
          aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__DASHBOARD_URL__">Dashboard</a>
        <form action="__LOGOUT_URL__" method="post">__CSRF_INPUT__
          <button type="submit">Log out</button>
        </form>
        <a class="header-cta" href="__FOUND_REPORT_URL__">Report an item</a>
      </nav>
    </div>
  </header>
  <main>
    <div class="report-layout">
      <section class="report-copy" aria-labelledby="report-heading">
        <p class="eyebrow">New campus report</p>
        <h1 id="report-heading">The right details create better matches.</h1>
        <p class="intro">Select a campus building and include distinguishing details. Your report helps the campus community reconnect belongings with their owners.</p>
        <div class="report-benefits">
          <p><span aria-hidden="true">⌖</span>Campus-specific location details</p>
          <p><span aria-hidden="true">✓</span>Owner-only editing and deletion</p>
          <p><span aria-hidden="true">◈</span>Private information requests</p>
        </div>
      </section>
      <section class="report-card" aria-label="__REPORT_CARD_LABEL__">
        __REPORT_TOGGLE__
        <p class="report-type" data-report-type-text data-lost-text="Lost item" data-found-text="Found item">__REPORT_TYPE_LABEL__ item</p>
        <h2 class="report-form-heading" data-report-type-text data-lost-text="Report a lost item" data-found-text="Report a found item">__PAGE_TITLE__</h2>
        <p class="report-form-intro" data-report-type-text data-lost-text="Share where and when you last had the item so others can help you find it." data-found-text="Share where and when you found the item so its owner can recognize it.">__FORM_INTRO__</p>
        __NOTICES__
        <form class="report-form" method="post" enctype="multipart/form-data">
          __CSRF_INPUT__
          __REPORT_TYPE_INPUT__
          __ERROR_SUMMARY__
          __FORM_FIELDS__
          <p class="form-footer">Your report will be listed with its category, campus building, and date. Found-item reports also include the time found.</p>
          <button class="submit-button" type="submit" data-report-type-text data-lost-text="Publish lost item report" data-found-text="Publish found item report">__SUBMIT_LABEL__</button>
        </form>
      </section>
    </div>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-about">
        <div class="footer-brand">⌕ &nbsp; FindIt</div>
        <p>A campus-powered network that helps lost belongings make their way home safely.</p>
      </div>
      <div class="footer-column">
        <h2>Take action</h2>
        <a href="__LOST_REPORT_URL__">Report a lost item</a>
        <a href="__FOUND_REPORT_URL__">Report a found item</a>
        <a href="__BROWSE_ITEMS_URL__">Search the catalog</a>
      </div>
      <div class="footer-column">
        <h2>Account</h2>
        <a href="__DASHBOARD_URL__">Your dashboard</a>
        <a href="/admin/">Staff administration</a>
      </div>
    </div>
    <div class="wrap copyright">© __YEAR__ FindIt. Built for safer campus returns.</div>
  </footer>
  __THEME_SCRIPT__
  __REPORT_TYPE_SCRIPT__
</body>
</html>"""


def _found_item_field(
    form,
    name,
    label,
    full_width=False,
    type_labels=None,
    visible_for=None,
    report_type="found",
):
    field = form[name]
    described_by = []
    if field.help_text:
        described_by.append(f"{field.html_name}-help")
    if field.errors:
        described_by.append(f"{field.html_name}-errors")
    field_errors = (
        format_html(
            '<ul id="{}-errors" class="field-errors" role="alert">{}</ul>',
            field.html_name,
            field.errors,
        )
        if field.errors
        else ""
    )
    field_help = (
        format_html(
            '<p id="{}-help" class="field-help">{}</p>',
            field.html_name,
            field.help_text,
        )
        if field.help_text
        else ""
    )
    label_attrs = (
        format_html(
            ' data-lost-label="{}" data-found-label="{}"',
            type_labels[0],
            type_labels[1],
        )
        if type_labels
        else ""
    )
    visibility_attrs = (
        format_html(
            ' data-report-only="{}"{}',
            visible_for,
            format_html(' hidden="{}"', "hidden")
            if visible_for != report_type
            else "",
        )
        if visible_for
        else ""
    )
    return format_html(
        '<div class="form-field{}"{}><label for="{}"{}>{}</label>{}{}{}</div>',
        " full" if full_width else "",
        visibility_attrs,
        field.id_for_label,
        label_attrs,
        label,
        field.as_widget(
            attrs={
                "class": "report-input",
                "aria-invalid": "true" if field.errors else "false",
                **({"aria-describedby": " ".join(described_by)} if described_by else {}),
            }
        ),
        field_help,
        field_errors,
    )


def found_item_page(request, form, editing=False):
    report_type = form["report_type"].value()
    if report_type not in {"lost", "found"}:
        report_type = "found"
    is_lost = report_type == "lost"
    type_label = "lost" if is_lost else "found"
    report_toggle = (
        format_html(
            '<div class="report-toggle" role="group" aria-label="Report type">'
            '<button class="report-toggle-option{}" type="button" data-report-type="lost" aria-pressed="{}">I Lost Something</button>'
            '<button class="report-toggle-option{}" type="button" data-report-type="found" aria-pressed="{}">I Found Something</button>'
            '</div>',
            " active" if is_lost else "",
            "true" if is_lost else "false",
            " active" if not is_lost else "",
            "false" if is_lost else "true",
        )
        if not editing
        else ""
    )
    error_summary = (
        format_html(
            '<ul class="error-summary" role="alert">{}</ul>',
            form.non_field_errors(),
        )
        if form.non_field_errors()
        else ""
    )
    form_fields = format_html(
        "{}{}{}{}{}{}{}{}{}",
        _found_item_field(form, "item_name", "Item name", full_width=True, report_type=report_type),
        _found_item_field(form, "category", "Category"),
        _found_item_field(form, "location", "Campus building", report_type=report_type),
        _found_item_field(
            form,
            "date_found",
            "Date lost" if is_lost else "Date found",
            type_labels=("Date lost", "Date found"),
            report_type=report_type,
        ),
        _found_item_field(form, "specific_area", "Specific area", report_type=report_type),
        _found_item_field(
            form,
            "time_found",
            "Time found",
            visible_for="found",
            report_type=report_type,
        ),
        _found_item_field(
            form,
            "description",
            "Description (optional)",
            full_width=True,
            report_type=report_type,
        ),
        _found_item_field(form, "image", "Item image", full_width=True, report_type=report_type),
        _found_item_field(
            form,
            "ownership_question",
            "Secure ownership question",
            full_width=True,
            visible_for="found",
            report_type=report_type,
        ),
    )
    notices = format_html_join(
        "",
        '<p class="notice" role="status">{}</p>',
        ((message,) for message in get_messages(request)),
    )
    page = FOUND_ITEM_PAGE
    for placeholder, value in (
        ("__HOME_URL__", reverse("home")),
        ("__BROWSE_ITEMS_URL__", reverse("browse_items")),
        ("__DASHBOARD_URL__", reverse("user_dashboard")),
        ("__FOUND_REPORT_URL__", reverse("found_report")),
        ("__LOGOUT_URL__", reverse("logout")),
        ("__LOST_REPORT_URL__", f'{reverse("found_report")}?type=lost'),
        ("__REPORT_CARD_LABEL__", f"{type_label.title()} item details"),
        ("__REPORT_TOGGLE__", str(report_toggle)),
        ("__REPORT_TYPE_LABEL__", type_label.title()),
        ("__REPORT_TYPE_INPUT__", str(form["report_type"])),
        ("__PAGE_TITLE__", f"Edit {type_label} item" if editing else f"Report a {type_label} item"),
        (
            "__FORM_INTRO__",
            (
                f"Update the {type_label} item details below."
                if editing
                else (
                    "Share where and when you last had the item so others can help you find it."
                    if is_lost
                    else "Share where and when you found the item so its owner can recognize it."
                )
            ),
        ),
        ("__SUBMIT_LABEL__", "Save changes" if editing else f"Publish {type_label} item report"),
        ("__CSRF_INPUT__", str(csrf_input(request))),
        ("__ERROR_SUMMARY__", str(error_summary)),
        ("__FORM_FIELDS__", str(form_fields)),
        ("__NOTICES__", str(notices)),
        ("__YEAR__", str(date.today().year)),
        ("__THEME_SCRIPT__", _theme_script()),
        (
            "__REPORT_TYPE_SCRIPT__",
            (
                '<script>(function(){'
                'const form=document.querySelector(".report-card form");'
                'if(!form)return;'
                'const typeInput=form.querySelector("[name=report_type]");'
                'const buttons=document.querySelectorAll("[data-report-type]");'
                'if(!typeInput||!buttons.length)return;'
                'function selectType(type){'
                'typeInput.value=type;'
                'buttons.forEach(button=>{'
                'const active=button.dataset.reportType===type;'
                'button.classList.toggle("active",active);'
                'button.setAttribute("aria-pressed",active?"true":"false");'
                '});'
                'document.querySelectorAll("[data-lost-label]").forEach(label=>{'
                'label.textContent=type==="lost"?label.dataset.lostLabel:label.dataset.foundLabel;'
                '});'
                'document.querySelectorAll("[data-report-only]").forEach(field=>{'
                'field.hidden=field.dataset.reportOnly!==type;'
                '});'
                'document.querySelectorAll("[data-report-type-text]").forEach(element=>{'
                'element.textContent=type==="lost"?element.dataset.lostText:element.dataset.foundText;'
                '});'
                '}'
                'buttons.forEach(button=>button.addEventListener("click",()=>selectType(button.dataset.reportType)));'
                'selectType(typeInput.value);'
                '})();</script>'
            ),
        ),
    ):
        page = page.replace(placeholder, value)
    return page


def _reported_item_card(request, item, show_reporter=False, can_approve_images=False):
    description = (
        format_html(
            '<p class="owned-report-description">{}</p>',
            item.description,
        )
        if item.description
        else ""
    )
    reporter = (
        format_html(' · Reported by {}', item.reporter.get_username())
        if show_reporter
        else ""
    )
    report_type = item.get_report_type_display()
    date_label = "lost on" if item.report_type == "lost" else "found on"
    time_at = (
        f' at {item.time_found.strftime("%I:%M %p").lstrip("0")}'
        if item.time_found
        else ""
    )
    image = (
        format_html(
            '<a href="{}"><img class="owned-report-image" src="{}" alt="Uploaded image for {}"></a>',
            reverse("found_item_image", args=(item.pk,)),
            reverse("found_item_image", args=(item.pk,)),
            item.item_name,
        )
        if item.image and (
            item.image_approved
            or item.reporter_id == request.user.pk
            or can_approve_images
        )
        else ""
    )
    image_status = (
        format_html(
            '<p class="owned-report-image-status">{}</p>',
            "Image approved and visible publicly."
            if item.image_approved
            else "Image pending admin approval.",
        )
        if item.image
        else ""
    )
    actions = format_html(
        '<div class="report-actions">{}{}{}</div>',
        (
            format_html(
                '<a href="{}">Edit</a>',
                reverse("edit_found_item", args=(item.pk,)),
            )
            if item.reporter_id == request.user.pk
            or request.user.has_perm("myapp.change_founditem")
            else ""
        ),
        (
            format_html(
                '<form action="{}" method="post" '
                'onsubmit="return confirm(\'Delete this found-item report?\')">{}'
                '<button class="delete-button" type="submit">Delete</button></form>',
                reverse("delete_found_item", args=(item.pk,)),
                csrf_input(request),
            )
            if item.reporter_id == request.user.pk
            or request.user.has_perm("myapp.delete_founditem")
            else ""
        ),
        (
            format_html(
                '<form action="{}" method="post">{}'
                '<button class="approve-image-button" type="submit">Approve image</button></form>',
                reverse("approve_found_item_image", args=(item.pk,)),
                csrf_input(request),
            )
            if item.image and not item.image_approved and can_approve_images
            else ""
        ),
    )
    return format_html(
        '<article class="owned-report"><div class="owned-report-content">'
        '<h3>{}</h3><p class="owned-report-meta">{} item · {} · {} · {} {}{}{}</p>{}{}{}'
        '</div>{}</article>',
        item.item_name,
        report_type,
        item.category,
        item.location,
        date_label,
        date_format(item.date_found, "M j, Y"),
        time_at,
        reporter,
        description,
        image,
        image_status,
        actions,
    )


def _reported_items_markup(
    request,
    found_items,
    show_reporter=False,
    can_approve_images=False,
):
    if not found_items:
        empty_message = (
            "There are no campus reports yet."
            if show_reporter
            else "You have not published a report yet."
        )
        return format_html(
            '<p class="empty-reports">{} <a href="{}">Report a found item</a>.</p>',
            empty_message,
            reverse("found_report"),
        )
    return format_html_join(
        "",
        "{}",
        (
            (
                _reported_item_card(
                    request,
                    item,
                    show_reporter=show_reporter,
                    can_approve_images=can_approve_images,
                ),
            )
            for item in found_items
        ),
    )


def _information_requests_markup(inquiries):
    if not inquiries:
        return format_html(
            '<p class="empty-requests">{}</p>',
            "No private information requests have arrived.",
        )
    return format_html_join(
        "",
        '<article class="private-request"><div class="private-request-heading">'
        '<h3>{}</h3><time>{}</time></div>'
        '<p class="private-request-sender">From {}</p><p class="private-request-message">{}</p></article>',
        (
            (
                inquiry.item.item_name,
                inquiry.created_at.strftime("%b %d, %Y at %I:%M %p"),
                inquiry.requester.get_username(),
                inquiry.message,
            )
            for inquiry in inquiries
        ),
    )


USER_DASHBOARD_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#014d48">
  <title>User dashboard | FindIt</title>
  <style>
    :root {
      color-scheme: light;
      --teal: #014d48;
      --paper: #fff;
      --card: #fff;
      --ink: #171b1b;
      --muted: #64716e;
      --line: #e4e6e5;
      --accent: #087c70;
      --button: #014d48;
      --button-ink: #fff;
      --danger: #b42318;
      --teal-bright: #8ce8d8;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh;
      margin: 0;
      background: var(--teal);
      color: #fff;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light {
      color-scheme: light;
      --teal: #e5f4f0;
      --paper: #fff;
      --card: #fff;
      --ink: #143b37;
      --muted: #596b67;
      --line: #dce8e5;
      --accent: #087c70;
      --button: #003e3a;
      --button-ink: #fff;
      --danger: #b42318;
      --teal-bright: #087c70;
      background: var(--teal);
      color: var(--ink);
    }
    body.theme-dark {
      color-scheme: dark;
      --teal: #0b211f;
      --paper: #111918;
      --card: #111918;
      --ink: #eef5f3;
      --muted: #b3c0bd;
      --line: #34423f;
      --accent: #8ce8d8;
      --button: #075d56;
      --button-ink: #eef5f3;
      --danger: #ff8982;
      --teal-bright: #66d8c6;
      background: var(--teal);
      color: var(--ink);
    }
    a { color: var(--accent); }
    button, input { font: inherit; }
    .wrap { width: min(1280px, calc(100% - 64px)); margin-inline: auto; }
    .site-header { position: sticky; z-index: 10; top: 0; background: #090a0b; color: #fff; }
    .header-inner {
      display: grid; min-height: 64px; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 24px;
    }
    .brand { display: inline-flex; align-items: center; gap: 10px; justify-self: start; color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .brand-mark {
      position: relative; display: grid; width: 36px; height: 36px; place-items: center;
      border-radius: 12px; background: #075d56; color: #fff; font-size: 0;
    }
    .brand-mark::before { width: 13px; height: 13px; transform: translate(-2px, -2px); border: 2.5px solid currentColor; border-radius: 50%; content: ""; }
    .brand-mark::after { position: absolute; width: 7px; height: 2.5px; transform: translate(5px, 5px) rotate(45deg); border-radius: 2px; background: currentColor; content: ""; }
    .primary-nav, .header-actions { display: flex; align-items: center; gap: 22px; }
    .primary-nav { justify-self: center; }
    .header-actions { justify-self: end; }
    .primary-nav a, .header-actions a { color: #f7f7f7; font-size: .9rem; font-weight: 650; text-decoration: none; }
    .primary-nav a:hover, .header-actions a:hover { color: #8ce8d8; }
    .header-actions form { margin: 0; }
    .header-actions button, .theme-toggle { padding: 0; border: 0; background: transparent; color: #fff; cursor: pointer; }
    .theme-toggle { font-size: 1.2rem; }
    .header-actions .header-cta { padding: 9px 18px; border-radius: 999px; background: #fff; color: #014d48; font-weight: 750; }
    body.theme-dark .header-actions .header-cta,
    body.theme-dark .new-report { border: 1px solid #34786f; background: #075d56; color: #eef5f3; }
    main { width: min(1280px, calc(100% - 64px)); margin: 0 auto; padding: 34px 0 80px; }
    .dashboard-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 24px; margin-bottom: 30px; }
    .eyebrow { margin: 0 0 5px; color: var(--teal-bright); font-size: .78rem; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; }
    h1 { margin: 0; font-size: clamp(2.2rem, 4vw, 3rem); letter-spacing: -.04em; line-height: 1.12; }
    .admin-indicator { display: inline-flex; width: .82em; height: .82em; margin-left: .16em; color: var(--teal-bright); vertical-align: .02em; }
    .admin-indicator svg { width: 100%; height: 100%; fill: none; stroke: currentColor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 1.8; }
    .intro { margin: 8px 0 0; color: rgba(255,255,255,.82); }
    body.theme-light .intro { color: rgba(20,59,55,.78); }
    .new-report {
      display: inline-flex; min-height: 46px; align-items: center; justify-content: center;
      gap: 8px; padding: 10px 18px; border-radius: 999px; background: #fff; color: #014d48;
      font-weight: 800; text-decoration: none; white-space: nowrap;
    }
    .dashboard-stats { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 16px; margin-bottom: 22px; }
    .stat-card { min-height: 96px; padding: 16px 20px; border: 1px solid rgba(255,255,255,.12); border-radius: 14px; background: rgba(255,255,255,.1); }
    .stat-icon { display: block; color: var(--teal-bright); font-size: .95rem; line-height: 1; }
    .stat-card strong { display: block; margin-top: 7px; font-size: 1.5rem; line-height: 1.2; }
    .stat-card .stat-label { color: rgba(255,255,255,.78); font-size: .88rem; }
    body.theme-light .stat-card { border-color: #cfe7e1; background: #eaf7f4; color: #163d38; }
    body.theme-light .stat-card .stat-label { color: #596b67; }
    body.theme-dark .stat-card { border-color: #34423f; background: #111918; color: #eef5f3; }
    body.theme-dark .stat-card .stat-label { color: #b3c0bd; }
    .notice { margin-bottom: 20px; padding: 12px 16px; border: 1px solid var(--line); border-radius: 12px; background: var(--card); color: var(--ink); }
    .dashboard-card {
      padding: clamp(22px, 4vw, 34px); border: 1px solid #eef0ef;
      border-radius: 22px; background: var(--card); color: var(--ink);
      box-shadow: 0 18px 45px rgba(0,0,0,.1);
    }
    body.theme-dark .dashboard-card { border-color: #34423f; }
    .dashboard-card h2 { margin: 0; font-size: 1.35rem; }
    .account-details h2 { margin-bottom: 20px; }
    .dashboard-card .section-eyebrow { margin: 0 0 3px; color: #087c70; font-size: .7rem; font-weight: 850; letter-spacing: .1em; text-transform: uppercase; }
    .reported-items, .account-details, .requests-section { margin-top: 24px; }
    .reports-heading-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .reports-heading-row h2 { margin: 0; }
    .reports-heading-row > a { font-weight: 700; }
    .report-list { display: grid; gap: 14px; margin-top: 20px; }
    .owned-report {
      display: flex; align-items: center; justify-content: space-between; gap: 20px;
      padding: 16px; border: 1px solid var(--line); border-radius: 14px; background: #fff;
    }
    body.theme-dark .owned-report,
    body.theme-dark .private-request,
    body.theme-dark .profile-details div { background: #111918; }
    .owned-report-content { min-width: 0; }
    .owned-report h3 { margin: 0 0 4px; font-size: 1.05rem; }
    .owned-report-meta, .owned-report-description { margin: 0; color: var(--muted); font-size: .88rem; }
    .owned-report-description { margin-top: 8px; }
    .report-actions { display: flex; align-items: center; gap: 14px; }
    .report-actions a { font-weight: 700; }
    .report-actions form { margin: 0; }
    .owned-report-image { display: block; width: 96px; height: 72px; margin-top: 10px; border-radius: 8px; object-fit: cover; }
    .owned-report-image-status { margin: 6px 0 0; color: var(--muted); font-size: .82rem; }
    .approve-image-button { padding: 7px 10px; border: 0; border-radius: 8px; background: var(--teal); color: #fff; font-weight: 700; cursor: pointer; }
    .delete-button {
      min-height: 40px; padding: 7px 14px; border: 1px solid var(--danger);
      border-radius: 999px; background: transparent; color: var(--danger);
      font-weight: 750; cursor: pointer;
    }
    .delete-button:hover { background: color-mix(in srgb, var(--danger) 12%, transparent); }
    .empty-reports { display: grid; min-height: 64px; place-items: center; margin: 16px 0 0; padding: 16px; border: 1px dashed var(--line); border-radius: 14px; color: var(--muted); text-align: center; }
    .private-request-list { display: grid; gap: 14px; }
    .private-request { padding: 16px; border: 1px solid var(--line); border-radius: 14px; background: #fff; }
    .private-request-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 14px; }
    .private-request h3 { margin: 0; font-size: 1rem; }
    .private-request time, .private-request-sender { color: var(--muted); font-size: .85rem; }
    .private-request-sender { margin: 5px 0 10px; }
    .private-request-message { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
    .empty-requests { margin: 0; color: var(--muted); }
    .requests-section > .private-request-list { margin-top: 16px; }
    .profile-details { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; margin: 0; }
    .profile-details div { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 14px; background: #fff; }
    .profile-details dt { margin-bottom: 4px; color: var(--muted); font-size: .82rem; font-weight: 700; }
    .profile-details dd { overflow-wrap: anywhere; margin: 0; font-weight: 650; }
    .username-form { max-width: 540px; margin-top: 30px; padding-top: 26px; border-top: 1px solid var(--line); }
    .username-form label { display: block; margin-bottom: 7px; font-weight: 700; }
    .text-input {
      width: 100%; min-height: 48px; padding: 10px 12px;
      border: 1px solid var(--line); border-radius: 10px; background: #fff; color: var(--ink);
    }
    body.theme-dark .text-input { border-color: #34423f; background: #192321; color: #eef5f3; color-scheme: dark; }
    .text-input:focus { outline: 3px solid var(--accent); outline-offset: 2px; }
    .field-help, .field-errors { margin: 6px 0 0; color: var(--muted); font-size: .85rem; }
    .field-errors { color: #d74848; }
    .field-errors ul { margin: 0; padding-left: 20px; }
    .submit-button {
      min-height: 46px; margin-top: 18px; padding: 10px 20px;
      border: 0; border-radius: 999px; background: var(--button); color: var(--button-ink);
      font-weight: 800; cursor: pointer;
    }
    .dashboard-feature { margin-top: 24px; padding: 28px 32px; border-radius: 22px; background: #090a0b; color: #fff; }
    body.theme-dark .dashboard-feature { border: 1px solid #34423f; background: #111918; color: #eef5f3; }
    .dashboard-feature .section-eyebrow { margin: 0 0 5px; color: #8ce8d8; font-size: .7rem; font-weight: 850; letter-spacing: .1em; text-transform: uppercase; }
    .dashboard-feature h2 { margin: 0 0 8px; font-size: 1.3rem; }
    .dashboard-feature p:last-child { margin: 0; color: #b6c0be; }
    .site-footer { background: #090a0b; color: #b6c0be; }
    .footer-inner { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 40px; padding-block: 42px 24px; }
    .footer-brand { color: #fff; font-size: 1.15rem; font-weight: 800; }
    .footer-about p { max-width: 360px; margin: 10px 0 0; color: #a4afac; font-size: .88rem; }
    .footer-column h2 { margin: 0 0 12px; color: #fff; font-size: .86rem; }
    .footer-column a { display: block; margin: 7px 0; color: #b6c0be; font-size: .85rem; text-decoration: none; }
    .footer-column a:hover { color: #8ce8d8; }
    .copyright { padding: 16px 0 22px; border-top: 1px solid #252a2a; color: #9ba5a3; font-size: .78rem; text-align: center; }
    .submit-button:focus-visible, .header-actions a:focus-visible,
    .header-actions button:focus-visible, .brand:focus-visible {
      outline: 3px solid #8ce8d8; outline-offset: 3px;
    }
    @media (max-width: 1120px) {
      .header-inner { display: flex; flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; }
    }
    @media (max-width: 560px) {
      .wrap, main { width: calc(100% - 36px); }
      .header-inner { flex-wrap: wrap; gap: 10px; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; gap: 8px; }
      .primary-nav a, .header-actions a { font-size: .76rem; }
      .header-actions { flex-wrap: wrap; gap: 12px; }
      .dashboard-heading { align-items: flex-start; flex-direction: column; }
      .dashboard-stats { grid-template-columns: 1fr; }
      .profile-details { grid-template-columns: 1fr; }
      .owned-report { align-items: flex-start; flex-direction: column; }
      .reports-heading-row { align-items: flex-start; flex-direction: column; }
      .private-request-heading { align-items: flex-start; flex-direction: column; gap: 2px; }
      .footer-inner { grid-template-columns: 1fr 1fr; gap: 24px; }
      .footer-about { grid-column: 1 / -1; }
    }
    @media (max-width: 390px) {
      .primary-nav { flex-wrap: wrap; justify-content: center; column-gap: 14px; }
      .header-actions a:not(.header-cta) { font-size: .8rem; }
      .footer-inner { grid-template-columns: 1fr; }
      .footer-about { grid-column: auto; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home"><span class="brand-mark" aria-hidden="true"></span>FindIt</a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="__HOME_URL__#how-it-works">How it works</a>
        <a href="__BROWSE_ITEMS_URL__">Browse items</a>
      </nav>
      <nav class="header-actions" aria-label="Account navigation">
        <button class="theme-toggle" type="button" data-theme-toggle
          aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__DASHBOARD_URL__">Dashboard</a>
        <form action="__LOGOUT_URL__" method="post">__CSRF_INPUT__
          <button type="submit">Log out</button>
        </form>
        <a class="header-cta" href="__FOUND_REPORT_URL__">Report an item</a>
      </nav>
    </div>
  </header>
  <main>
    <div class="dashboard-heading">
      <div>
        <p class="eyebrow">__DASHBOARD_ROLE__</p>
        <h1>Welcome back, __USERNAME____ADMIN_ICON__.</h1>
        <p class="intro">__DASHBOARD_INTRO__</p>
      </div>
      <a class="new-report" href="__FOUND_REPORT_URL__">＋ &nbsp; New report</a>
    </div>
    __NOTICES__
    <section class="dashboard-stats" aria-label="Account activity summary">
      <article class="stat-card"><span class="stat-icon" aria-hidden="true">◈</span><strong>__REPORT_COUNT__</strong><span class="stat-label">__REPORT_STAT_LABEL__</span></article>
      <article class="stat-card"><span class="stat-icon" aria-hidden="true">✣</span><strong>0</strong><span class="stat-label">Smart matches</span></article>
      <article class="stat-card"><span class="stat-icon" aria-hidden="true">◇</span><strong>0</strong><span class="stat-label">Claims tracked</span></article>
    </section>
    <section class="dashboard-card reported-items" aria-labelledby="reports-heading">
      <p class="section-eyebrow">__REPORTS_EYEBROW__</p>
      <div class="reports-heading-row">
        <h2 id="reports-heading">__REPORTS_HEADING__</h2>
        <a href="__FOUND_REPORT_URL__">Report another item</a>
      </div>
      <div class="report-list">__FOUND_ITEMS__</div>
    </section>
    <section class="dashboard-card account-details" aria-labelledby="profile-heading">
      <p class="section-eyebrow">Account settings</p>
      <h2 id="profile-heading">Your information</h2>
      <dl class="profile-details">
        <div><dt>Username</dt><dd>__USERNAME__</dd></div>
        <div><dt>Email</dt><dd>__EMAIL__</dd></div>
        <div><dt>Member since</dt><dd>__JOINED__</dd></div>
      </dl>
      <form class="username-form" method="post">
        __CSRF_INPUT__
        <div class="form-field">__USERNAME_FIELD__</div>
        <button class="submit-button" type="submit">Save username</button>
      </form>
    </section>
    <section class="dashboard-card requests-section" aria-labelledby="requests-heading">
      <h2 id="requests-heading">Private information requests</h2>
      <div class="private-request-list">__INFORMATION_REQUESTS__</div>
    </section>
    <section class="dashboard-feature" aria-labelledby="matching-heading">
      <p class="section-eyebrow">AI-assisted matching</p>
      <h2 id="matching-heading">Smart-match insights</h2>
      <p>Matching features are not available yet. Your reports and private requests remain available above.</p>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-about">
        <div class="footer-brand">⌕ &nbsp; FindIt</div>
        <p>A campus-powered network that helps lost belongings make their way home safely.</p>
      </div>
      <div class="footer-column">
        <h2>Take action</h2>
        <a href="__LOST_REPORT_URL__">Report a lost item</a>
        <a href="__FOUND_REPORT_URL__">Report a found item</a>
        <a href="__BROWSE_ITEMS_URL__">Search the catalog</a>
      </div>
      <div class="footer-column">
        <h2>Account</h2>
        <a href="__DASHBOARD_URL__">Your dashboard</a>
        <a href="/admin/">Staff administration</a>
      </div>
    </div>
    <div class="wrap copyright">© __YEAR__ FindIt. Built for safer campus returns.</div>
  </footer>
  __THEME_SCRIPT__
</body>
</html>"""


def user_dashboard_page(
    request,
    form,
    found_items,
    inquiries,
    can_manage_reports=False,
    can_approve_images=False,
):
    username = form.instance.get_username()
    email = form.instance.email or "Not provided"
    joined = date_format(form.instance.date_joined.date(), "F j, Y")
    described_by = []
    if form["username"].help_text:
        described_by.append("username-help")
    if form["username"].errors:
        described_by.append("username-errors")
    field_errors = (
        format_html('<div id="username-errors" class="field-errors" role="alert">{}</div>', form["username"].errors)
        if form["username"].errors
        else ""
    )
    field_help = (
        format_html('<p id="username-help" class="field-help">{}</p>', form["username"].help_text)
        if form["username"].help_text
        else ""
    )
    username_field = format_html(
        '<label for="{}">New username</label>{}{}{}',
        form["username"].id_for_label,
        form["username"].as_widget(
            attrs={
                "class": "text-input",
                "autocomplete": "username",
                "aria-invalid": "true" if form["username"].errors else "false",
                **({"aria-describedby": " ".join(described_by)} if described_by else {}),
            },
        ),
        field_errors,
        field_help,
    )
    admin_icon = (
        format_html(
            '<span class="admin-indicator" role="img" aria-label="{}" '
            'title="{}"><svg viewBox="0 0 24 24" aria-hidden="true">'
            '<path d="M12 2.5 4.5 5.4v5.3c0 4.8 3.2 9 7.5 10.8 4.3-1.8 7.5-6 7.5-10.8V5.4L12 2.5Z"/>'
            '<path d="m8.7 11.9 2.2 2.2 4.5-4.5"/></svg></span>',
            "Administrator",
            "Administrator",
        )
        if can_manage_reports
        else ""
    )
    notices = format_html_join(
        "",
        '<p class="notice" role="status">{}</p>',
        ((message,) for message in get_messages(request)),
    )
    reported_items = _reported_items_markup(
        request,
        found_items,
        show_reporter=can_manage_reports,
        can_approve_images=can_approve_images,
    )
    information_requests = _information_requests_markup(inquiries)
    page = USER_DASHBOARD_PAGE
    for placeholder, value in (
        ("__HOME_URL__", reverse("home")),
        ("__BROWSE_ITEMS_URL__", reverse("browse_items")),
        ("__DASHBOARD_URL__", reverse("user_dashboard")),
        ("__LOGOUT_URL__", reverse("logout")),
        ("__FOUND_REPORT_URL__", reverse("found_report")),
        ("__LOST_REPORT_URL__", f'{reverse("found_report")}?type=lost'),
        ("__CSRF_INPUT__", str(csrf_input(request))),
        ("__USERNAME__", format_html("{}", username)),
        ("__ADMIN_ICON__", str(admin_icon)),
        ("__EMAIL__", format_html("{}", email)),
        ("__JOINED__", str(joined)),
        ("__USERNAME_FIELD__", str(username_field)),
        ("__FOUND_ITEMS__", str(reported_items)),
        ("__REPORT_COUNT__", str(len(found_items))),
        (
            "__DASHBOARD_ROLE__",
            "Report administration" if can_manage_reports else "Member dashboard",
        ),
        (
            "__DASHBOARD_INTRO__",
            "Review and manage reports from across campus."
            if can_manage_reports
            else "Manage reports, monitor claims, and review smart matches.",
        ),
        ("__REPORT_STAT_LABEL__", "Campus reports" if can_manage_reports else "Your reports"),
        ("__REPORTS_EYEBROW__", "Report management" if can_manage_reports else "Item status tracking"),
        ("__REPORTS_HEADING__", "All campus reports" if can_manage_reports else "Your reports"),
        ("__INFORMATION_REQUESTS__", str(information_requests)),
        ("__YEAR__", str(date.today().year)),
        ("__NOTICES__", str(notices)),
        ("__THEME_SCRIPT__", _theme_script()),
    ):
        page = page.replace(placeholder, value)
    return page


def csrf_input(request):
    return format_html(
        '<input type="hidden" name="csrfmiddlewaretoken" value="{}">',
        get_token(request),
    )


def _theme_script():
    return """<script>
      (() => {
        const storageKey = "findit-theme";
        const applyTheme = (theme, save = false) => {
          document.body.classList.toggle("theme-light", theme === "light");
          document.body.classList.toggle("theme-dark", theme === "dark");
          document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
            const lightMode = theme === "light";
            button.textContent = lightMode ? "☾" : "☀";
            button.setAttribute("aria-label", `Switch to ${lightMode ? "dark" : "light"} mode`);
            button.setAttribute("aria-pressed", String(lightMode));
          });
          if (save) {
            try {
              localStorage.setItem(storageKey, theme);
            } catch {}
          }
        };
        let savedTheme = "dark";
        try {
          savedTheme = localStorage.getItem(storageKey) === "light" ? "light" : "dark";
        } catch {}
        applyTheme(savedTheme);
        document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
          button.addEventListener("click", () => {
            const nextTheme = document.body.classList.contains("theme-light") ? "dark" : "light";
            applyTheme(nextTheme, true);
          });
        });
      })();
    </script>"""


def signup_page(request, form):
    page = LOGIN_PAGE.replace(
        "<title>Log in | FindIt</title>", "<title>Create account | FindIt</title>"
    )
    page = page.replace(
        '<a class="auth-tab active" href="__LOGIN_URL__" aria-current="page">Log in</a>\n'
        '          <a class="auth-tab" href="__SIGNUP_URL__">Create account</a>',
        '<a class="auth-tab" href="__LOGIN_URL__">Log in</a>\n'
        '          <a class="auth-tab active" href="__SIGNUP_URL__" aria-current="page">Create account</a>',
    )
    page = page.replace("Welcome back", "Join FindIt")
    page = page.replace("Access your dashboard", "Create your member account")
    page = page.replace("__NEXT_INPUT__", "")

    fields = (
        ("username", "Username", "Choose a username", "username"),
        ("email", "Campus email", "you@campus.edu", "email"),
        ("password1", "Password", "At least 8 characters", "new-password"),
        ("password2", "Confirm password", "Enter your password again", "new-password"),
    )
    field_markup = {
        name: _styled_auth_field(
                form[name],
                label,
                placeholder,
                autocomplete,
                autofocus=name == "username",
            )
        for name, label, placeholder, autocomplete in fields
    }
    account_fields = format_html(
        '<div class="auth-field">{}</div><div class="auth-field">{}</div>'
        '<div class="auth-field">{}</div><div class="auth-field">{}</div>'
        '<button class="submit-button" type="submit">Create account</button>',
        field_markup["username"],
        field_markup["email"],
        field_markup["password1"],
        field_markup["password2"],
    )

    errors = form.non_field_errors()
    error_summary = (
        format_html('<div class="error-summary" role="alert">{}</div>', errors)
        if errors
        else ""
    )
    for placeholder, value in (
        ("__HOME_URL__", reverse("home")),
        ("__BROWSE_ITEMS_URL__", reverse("browse_items")),
        ("__LOGIN_URL__", reverse("login")),
        ("__SIGNUP_URL__", reverse("signup")),
        ("__FOUND_REPORT_URL__", reverse("found_report")),
        ("__ADMIN_URL__", reverse("admin:index")),
        ("__CSRF_INPUT__", str(csrf_input(request))),
        ("__THEME_SCRIPT__", _theme_script()),
        ("__FORM_ERRORS__", str(error_summary)),
        ("__ACCOUNT_FIELDS__", str(account_fields)),
        ("__YEAR__", str(date.today().year)),
    ):
        page = page.replace(placeholder, value)
    return page


def _styled_auth_field(bound_field, label, placeholder, autocomplete, autofocus=False):
    errors = bound_field.errors
    error_markup = (
        format_html('<div class="field-errors">{}</div>', errors)
        if errors
        else ""
    )
    help_markup = (
        format_html('<div class="field-help">{}</div>', bound_field.help_text)
        if bound_field.help_text
        else ""
    )
    return format_html(
        '<label for="{}">{}</label>{}{}{}',
        bound_field.id_for_label,
        label,
        bound_field.as_widget(
            attrs={
                "class": "auth-input",
                "placeholder": placeholder,
                "autocomplete": autocomplete,
                "autofocus": autofocus,
            }
        ),
        error_markup,
        help_markup,
    )


LOGIN_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="theme-color" content="#014d48">
  <title>Log in | FindIt</title>
  <style>
    :root {
      color-scheme: light;
      --teal: #014d48;
      --teal-deep: #003e3a;
      --teal-bright: #78ddca;
      --action-green: #014d48;
      --ink: #171b1b;
      --muted: #64716e;
      --line: #e4e6e5;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh;
      margin: 0;
      background: var(--teal);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    a { color: inherit; }
    .wrap { width: min(1280px, calc(100% - 64px)); margin-inline: auto; }
    .site-header {
      position: sticky; z-index: 10; top: 0; min-height: 64px;
      border-bottom: 1px solid rgba(255,255,255,.1); background: rgba(9,10,11,.96);
      color: #fff; backdrop-filter: blur(14px);
    }
    .header-inner { display: grid; min-height: 64px; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 24px; }
    .brand { display: inline-flex; align-items: center; gap: 10px; justify-self: start; color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .brand-mark {
      position: relative; display: grid; width: 36px; height: 36px; place-items: center;
      border-radius: 12px; background: #075d56; color: #fff;
    }
    .brand-mark::before { width: 13px; height: 13px; transform: translate(-2px,-2px); border: 2.5px solid currentColor; border-radius: 50%; content: ""; }
    .brand-mark::after { position: absolute; width: 7px; height: 2.5px; transform: translate(5px,5px) rotate(45deg); border-radius: 2px; background: currentColor; content: ""; }
    .primary-nav, .header-actions { display: flex; align-items: center; gap: 24px; }
    .primary-nav { justify-self: center; }
    .header-actions { justify-self: end; }
    .primary-nav a, .header-actions a { color: #f7f7f7; font-size: .9rem; font-weight: 600; text-decoration: none; }
    .primary-nav a:hover, .header-actions a:hover { color: var(--teal-bright); }
    .theme-link { border: 0; background: transparent; color: #fff !important; font-size: 1.2rem !important; cursor: pointer; }
    .header-actions .header-cta { padding: 9px 18px; border-radius: 999px; background: #fff; color: var(--action-green); font-weight: 750; }
    body { background: #014d48; }
    body.theme-light { background: #e5f4f0; --teal: #e5f4f0; --teal-bright: #087c70; --action-green: #003e3a; }
    body.theme-light .submit-button { background: #003e3a; }
    body.theme-light .welcome-panel { color: #143b37; }
    body.theme-light .welcome-panel > p { color: rgba(20,59,55,.78); }
    body.theme-light .benefit { color: #24514b; }
    main { min-height: 535px; padding: 48px 0 64px; }
    .auth-panel {
      display: grid; width: min(896px, calc(100% - 36px)); min-height: 390px; margin: 0 auto;
      grid-template-columns: 1fr 1.18fr; overflow: hidden;
      border: 1px solid var(--panel-border, rgba(255,255,255,.9)); border-radius: 28px;
      background: #fff; box-shadow: 0 24px 70px rgba(0,0,0,.14);
    }
    body.theme-light .auth-panel { --panel-border: #cfe7e1; }
    .welcome-panel { padding: 40px; background: var(--teal); color: #fff; }
    .lock-icon {
      position: relative; display: grid; width: 48px; height: 48px; margin-bottom: 28px;
      place-items: center; border-radius: 16px; background: rgba(255,255,255,.11); color: var(--teal-bright);
    }
    .lock-icon::before {
      width: 17px; height: 14px; margin-top: 8px; border: 2px solid currentColor;
      border-radius: 3px; content: "";
    }
    .lock-icon::after {
      position: absolute; top: 11px; left: 17px; width: 12px; height: 11px;
      border: 2px solid currentColor; border-bottom: 0; border-radius: 9px 9px 0 0; content: "";
    }
    .welcome-panel h1 { max-width: 380px; margin: 0 0 14px; font-size: clamp(2rem, 3.2vw, 2.65rem); font-weight: 750; letter-spacing: -.04em; line-height: 1.16; }
    .welcome-panel > p { max-width: 440px; margin: 0 0 24px; color: rgba(255,255,255,.78); font-size: .98rem; }
    .benefits { display: grid; gap: 10px; }
    .benefit { display: flex; align-items: center; gap: 9px; margin: 0; color: rgba(255,255,255,.9); font-size: .94rem; }
    .benefit span { color: var(--teal-bright); font-size: 1.05rem; }
    .form-panel { padding: 40px; background: #fff; }
    .auth-tabs { display: grid; grid-template-columns: 1fr 1fr; gap: 4px; margin-bottom: 26px; padding: 4px; border-radius: 14px; background: #f4f4f5; }
    .auth-tab { display: block; padding: 10px 12px; border-radius: 10px; color: #64646b; font-size: .9rem; font-weight: 750; text-align: center; text-decoration: none; }
    .auth-tab.active { background: #fff; color: var(--action-green); box-shadow: 0 1px 5px rgba(0,0,0,.12); }
    .form-eyebrow { display: flex; align-items: center; gap: 9px; margin: 0 0 4px; color: #315d58; font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    .form-eyebrow span { font-size: 1.1rem; }
    .form-panel h2 { margin: 0 0 22px; color: #171717; font-size: 1.8rem; font-weight: 800; letter-spacing: -.035em; line-height: 1.25; }
    .error-summary { margin: 0 0 16px; padding: 10px 12px; border: 1px solid #f2c5c2; border-radius: 10px; background: #fff5f4; color: #9c2823; font-size: .88rem; }
    .error-summary ul { margin: 0; padding-left: 20px; }
    .auth-field { margin-bottom: 14px; }
    .auth-field label { display: block; margin-bottom: 6px; color: #414648; font-size: .88rem; font-weight: 700; }
    .auth-input {
      display: block; width: 100%; min-height: 48px; padding: 12px 14px;
      border: 1px solid #dedfdf; border-radius: 12px; background: #fff; color: #27292a;
      font: inherit; font-size: .92rem;
    }
    .auth-input::placeholder { color: #969b9a; }
    .auth-input:focus { border-color: #168b7d; outline: 3px solid rgba(22,139,125,.14); }
    .field-errors { margin: 5px 0 0; padding-left: 18px; color: #a52e28; font-size: .8rem; }
    .field-errors ul, .field-help ul { margin: 5px 0 0; padding-left: 18px; }
    .field-help { margin-top: 5px; color: #747d7a; font-size: .77rem; }
    .submit-button {
      width: 100%; min-height: 48px; margin-top: 4px; padding: 12px 20px;
      border: 0; border-radius: 12px; background: var(--action-green); color: #fff;
      font: inherit; font-size: .92rem; font-weight: 800; cursor: pointer;
      transition: background 160ms ease;
    }
    .submit-button:hover { background: #002f2c; }
    body.theme-dark {
      color-scheme: dark; background: #0b211f; --teal: #0b211f; --teal-deep: #071917;
      --teal-bright: #66d8c6; --action-green: #075d56; --ink: #eef5f3; --muted: #b3c0bd;
      --line: #34423f;
    }
    body.theme-dark .header-actions .header-cta {
      border: 1px solid #66d8c6; background: #075d56; color: #fff;
    }
    body.theme-dark .header-actions .header-cta:hover { background: #087c70; color: #fff; }
    body.theme-dark .auth-panel {
      border-color: #34423f; background: #111918;
    }
    body.theme-dark .form-panel { background: #111918; }
    body.theme-dark .auth-tabs { background: #202b29; }
    body.theme-dark .auth-tab { color: #b8c5c1; }
    body.theme-dark .auth-tab.active { background: #2b3936; color: #9ce7d9; }
    body.theme-dark .form-eyebrow { color: #9ce7d9; }
    body.theme-dark .form-panel h2 { color: #f2f7f5; }
    body.theme-dark .auth-field label { color: #d4dfdc; }
    body.theme-dark .auth-input {
      border-color: #465451; background: #1a2522; color: #f2f7f5; color-scheme: dark;
    }
    body.theme-dark .auth-input::placeholder { color: #a9b7b3; }
    body.theme-dark .error-summary { border-color: #713e3b; background: #321f1e; color: #ffc5bf; }
    body.theme-dark .field-errors { color: #ffaaa2; }
    body.theme-dark .field-help { color: #b3c0bd; }
    .site-footer { background: #090a0b; color: #b6c0be; }
    .footer-inner { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: 40px; padding-block: 42px 24px; }
    .footer-brand { color: #fff; font-size: 1.15rem; font-weight: 800; }
    .footer-about p { max-width: 360px; margin: 10px 0 0; color: #a4afac; font-size: .88rem; }
    .footer-column h2 { margin: 0 0 12px; color: #fff; font-size: .86rem; }
    .footer-column a { display: block; margin: 7px 0; color: #b6c0be; font-size: .85rem; text-decoration: none; }
    .footer-column a:hover { color: #8ce8d8; }
    .copyright { padding: 16px 0 22px; border-top: 1px solid #252a2a; color: #9ba5a3; font-size: .78rem; text-align: center; }
    @media (max-width: 1120px) {
      .header-inner { display: flex; flex-wrap: wrap; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; }
    }
    @media (max-width: 850px) {
      .primary-nav, .header-actions { gap: 14px; }
      .auth-panel { grid-template-columns: .9fr 1.1fr; }
      .welcome-panel, .form-panel { padding: 30px; }
    }
    @media (max-width: 650px) {
      .wrap { width: calc(100% - 36px); }
      .header-inner { flex-wrap: wrap; gap: 10px; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: center; gap: 8px; }
      .primary-nav a { font-size: .76rem; }
      .header-actions { gap: 12px; }
      .header-actions .header-cta { padding: 8px 11px; font-size: .76rem; }
      main { padding: 28px 0 42px; }
      .auth-panel { grid-template-columns: 1fr; border-radius: 22px; }
      .welcome-panel { padding: 28px; }
      .lock-icon { margin-bottom: 18px; }
      .welcome-panel h1 { font-size: 2rem; }
      .welcome-panel > p { margin-bottom: 18px; }
      .benefits { gap: 7px; }
      .form-panel { padding: 26px; }
      .auth-tabs { margin-bottom: 22px; }
      .footer-inner { grid-template-columns: 1fr 1fr; gap: 24px; }
      .footer-about { grid-column: 1 / -1; }
    }
    @media (max-width: 390px) {
      .primary-nav { flex-wrap: wrap; justify-content: center; column-gap: 14px; }
      .header-actions a:not(.header-cta) { font-size: .8rem; }
      .footer-inner { grid-template-columns: 1fr; }
      .footer-about { grid-column: auto; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="wrap header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home"><span class="brand-mark" aria-hidden="true"></span>FindIt</a>
      <nav class="primary-nav" aria-label="Primary navigation">
        <a href="__HOME_URL__#how-it-works">How it works</a>
        <a href="__BROWSE_ITEMS_URL__">Browse items</a>
      </nav>
      <div class="header-actions">
        <button class="theme-link" type="button" data-theme-toggle aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__LOGIN_URL__">Log in</a>
        <a class="header-cta" href="__FOUND_REPORT_URL__">Report an item</a>
      </div>
    </div>
  </header>
  <main>
    <section class="auth-panel" aria-label="FindIt account access">
      <div class="welcome-panel">
        <span class="lock-icon" aria-hidden="true"></span>
        <h1>Your campus recovery hub</h1>
        <p>Sign in to publish reports, review smart matches, track claim status, and manage every listing from one secure dashboard.</p>
        <div class="benefits">
          <p class="benefit"><span aria-hidden="true">ⓥ</span>Private account sessions</p>
          <p class="benefit"><span aria-hidden="true">ⓥ</span>Owner-only report editing</p>
          <p class="benefit"><span aria-hidden="true">ⓥ</span>Verified claim workflow</p>
        </div>
      </div>
      <div class="form-panel">
        <nav class="auth-tabs" aria-label="Account options">
          <a class="auth-tab active" href="__LOGIN_URL__" aria-current="page">Log in</a>
          <a class="auth-tab" href="__SIGNUP_URL__">Create account</a>
        </nav>
        <p class="form-eyebrow"><span aria-hidden="true">♙</span>Welcome back</p>
        <h2>Access your dashboard</h2>
        <form method="post">
          __CSRF_INPUT__
          __NEXT_INPUT__
          __FORM_ERRORS__
          __ACCOUNT_FIELDS__
        </form>
      </div>
    </section>
  </main>
  <footer class="site-footer">
    <div class="wrap footer-inner">
      <div class="footer-about">
        <div class="footer-brand">⌕ &nbsp; FindIt</div>
        <p>A campus-powered network that helps lost belongings make their way home safely.</p>
      </div>
      <div class="footer-column">
        <h2>Take action</h2>
        <a href="__FOUND_REPORT_URL__">Report a lost item</a>
        <a href="__FOUND_REPORT_URL__">Report a found item</a>
        <a href="__BROWSE_ITEMS_URL__">Search the catalog</a>
      </div>
      <div class="footer-column">
        <h2>Account</h2>
        <a href="__LOGIN_URL__">Register or log in</a>
        <a href="__LOGIN_URL__">Your dashboard</a>
        <a href="__ADMIN_URL__">Staff administration</a>
      </div>
    </div>
    <div class="wrap copyright">© __YEAR__ FindIt. Built for safer campus returns.</div>
  </footer>
  __THEME_SCRIPT__
</body>
</html>"""


def login_page(request, form, next_url):
    username_field = _styled_auth_field(
        form["username"], "Campus username", "Your campus username", "username", autofocus=True
    )
    password_field = _styled_auth_field(
        form["password"], "Password", "Enter your password", "current-password"
    )
    errors = form.non_field_errors()
    error_summary = (
        format_html('<div class="error-summary" role="alert">{}</div>', errors)
        if errors
        else ""
    )
    account_fields = format_html(
        '<div class="auth-field">{}</div><div class="auth-field">{}</div>'
        '<button class="submit-button" type="submit">Log in securely</button>',
        username_field,
        password_field,
    )
    page = LOGIN_PAGE
    for placeholder, value in (
        ("__HOME_URL__", reverse("home")),
        ("__BROWSE_ITEMS_URL__", reverse("browse_items")),
        ("__LOGIN_URL__", reverse("login")),
        ("__SIGNUP_URL__", reverse("signup")),
        ("__FOUND_REPORT_URL__", reverse("found_report")),
        ("__ADMIN_URL__", reverse("admin:index")),
        ("__CSRF_INPUT__", str(csrf_input(request))),
        ("__THEME_SCRIPT__", _theme_script()),
        (
            "__NEXT_INPUT__",
            str(format_html('<input type="hidden" name="next" value="{}">', next_url)),
        ),
        ("__FORM_ERRORS__", str(error_summary)),
        ("__ACCOUNT_FIELDS__", str(account_fields)),
        ("__YEAR__", str(date.today().year)),
    ):
        page = page.replace(placeholder, value)
    return page
