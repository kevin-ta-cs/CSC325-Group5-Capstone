import re
from datetime import date

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
      --paper: #111918;
      --ink: #eef5f3;
      --muted: #b3c0bd;
      --line: #34423f;
      --card: #192321;
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
    .header-inner { display: flex; min-height: 64px; align-items: center; justify-content: space-between; gap: 24px; }
    .brand { display: inline-flex; align-items: center; gap: 10px; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
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
      background: #192321; color: #eef5f3; box-shadow: 0 20px 50px rgba(0,0,0,.25);
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
      padding: 0; border: 0; background: none; font: inherit; text-align: left; cursor: not-allowed;
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
    body.theme-dark .step { background: #192321; }
    body.theme-dark .step-icon { background: #263a36; color: #8ce8d8; }
    body.theme-dark .filters { background: #192321; color: #eef5f3; }
    body.theme-dark .filters label { color: #c1ceca; }
    body.theme-dark .filters input,
    body.theme-dark .filters select {
      border-color: #465451; background-color: #111918; color: #eef5f3; color-scheme: dark;
    }
    body.theme-dark .report-card { border-color: #34423f; background: #192321; color: #eef5f3; }
    body.theme-dark .report-category { color: #8ce8d8; }
    body.theme-dark .report-description,
    body.theme-dark .report-meta { color: #b3c0bd; }
    body.theme-dark .report-details-link { background: #111918; color: #eef5f3; }
    body.theme-dark .report-card-link:hover .report-details-link { background: #263a36; color: #8ce8d8; }
    body.theme-dark .dashboard-card.secondary {
      border-color: #34423f; background: #192321; color: #eef5f3;
    }
    body.theme-dark .dashboard-card:not(.secondary) { background: #192321; }
    body.theme-dark .dashboard-card.secondary .eyebrow { color: #8ce8d8; }
    body.theme-dark .dashboard-card.secondary p { color: #b3c0bd; }
    body.theme-dark .dashboard-card.secondary a,
    body.theme-dark .dashboard-card.secondary .dashboard-action { color: #8ce8d8; }
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
      .primary-nav { order: 3; width: 100%; justify-content: space-between; gap: 10px; }
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
      .primary-nav { flex-wrap: wrap; justify-content: flex-start; column-gap: 14px; }
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
        <a href="#report-actions">Report lost</a>
        <a href="__FOUND_REPORT_URL__">Report found</a>
        <a href="#recent-items">Browse items</a>
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
          <strong>__REPORT_COUNT__ active reports</strong>
          <span>✳ &nbsp;Smart matches compare category, place, date, and description</span>
        </div>
        <div class="report-grid">__REPORT_CARDS__</div>
        <a class="browse-link" href="#recent-items">Browse all reports &nbsp;→</a>
      </div>
    </section>
    <section class="light-section dashboard-section">
      <div class="section-inner">
        <div class="dashboard-grid">
          <article class="dashboard-card">
            <p class="eyebrow">For students and staff</p>
            <h2>One dashboard for every report.</h2>
            <p>Edit or delete reports, track status, monitor claims, and see new smart matches as the catalog grows.</p>
            <a class="dashboard-action" href="__DASHBOARD_URL__">Open your dashboard &nbsp;→</a>
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
        <a href="#recent-items">Search the catalog</a>
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


def _filter_form(request, theme):
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
        '<form class="filters" action="#recent-items" method="get">'
        '<label class="search-field"><span class="sr-only">Search reports</span>'
        '<input type="search" name="q" value="{}" placeholder="Search item details">'
        '<button class="filter-submit" type="submit" aria-label="Search reports">⌕</button></label>'
        '<label><span class="sr-only">Report type</span><select name="type">{}</select></label>'
        '<label><span class="sr-only">Category</span><select name="category">{}</select></label>'
        '<label><span class="sr-only">Building</span><select name="building">{}</select></label>'
        '<label><span class="sr-only">Sort</span><select name="sort">{}</select></label>'
        '</form>',
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


def home_page(request):
    theme = "dark"
    selected_type = request.GET.get("type", "")
    selected_category = request.GET.get("category", "")
    selected_building = request.GET.get("building", "")
    search = request.GET.get("q", "").strip()[:100].casefold()
    reports = [
        {**report, "item_id": f"sample-{index}"}
        for index, report in enumerate(REPORTS)
    ]
    reports.extend(
        {
            "type": "found",
            "item_id": str(item.pk),
            "category": item.category,
            "title": item.item_name,
            "description": item.description,
            "building": item.location,
            "date": item.date_found.isoformat(),
            "time": item.time_found.strftime("%I:%M %p").lstrip("0"),
            "image": "",
            "alt": "",
        }
        for item in FoundItem.objects.all()
    )
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

    if reports:
        report_cards = format_html_join("", "{}", ((_report_card(report),) for report in reports))
    else:
        report_cards = format_html(
            '<p class="empty-state">{}</p>',
            "No reports match those filters. Try another search.",
        )

    account_url = reverse("login")
    dashboard_url = reverse("user_dashboard")
    dashboard_login_url = f"{account_url}?next={dashboard_url}"
    report_url = reverse("signup")
    found_report_url = reverse("found_report")
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
    page = HOME_PAGE
    for placeholder, value in (
        ("__THEME__", f"theme-{theme}"),
        ("__THEME_SCRIPT__", _theme_script()),
        ("__ACCOUNT_LINK__", str(account_link)),
        ("__ACCOUNT_URL__", account_url),
        (
            "__DASHBOARD_URL__",
            dashboard_url if request.user.is_authenticated else dashboard_login_url,
        ),
        ("__REPORT_URL__", report_url),
        ("__FOUND_REPORT_URL__", found_report_url),
        ("__FILTERS__", str(_filter_form(request, theme))),
        ("__REPORT_COUNT__", str(len(reports))),
        ("__REPORT_CARDS__", str(report_cards)),
        ("__YEAR__", str(date.today().year)),
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
      --paper: #174b47;
      --card: #fff;
      --ink: #171d1c;
      --muted: #66716e;
      --line: #e1e7e5;
      --accent: #087c70;
      --button: #064d47;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh; margin: 0; background: var(--paper); color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light { color-scheme: light; --paper: #f3f8f6; --card: #fff; --ink: #163d38; --muted: #596b67; --line: #dce8e5; }
    a { color: var(--accent); }
    button, textarea { font: inherit; }
    .site-header { background: #090a0b; color: #fff; }
    .header-inner {
      display: flex; width: min(1440px, calc(100% - 48px)); min-height: 68px;
      align-items: center; justify-content: space-between; gap: 24px; margin-inline: auto;
    }
    .brand { color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .header-actions { display: flex; align-items: center; gap: 20px; }
    .header-actions a { color: #fff; font-weight: 650; text-decoration: none; }
    .theme-toggle { padding: 0; border: 0; background: transparent; color: #fff; font-size: 1.2rem; cursor: pointer; }
    main { width: min(1440px, calc(100% - 48px)); margin: 30px auto 80px; }
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
    .item-facts div { min-width: 0; }
    .item-facts dt { color: var(--muted); font-size: .78rem; font-weight: 750; }
    .item-facts dd { margin: 2px 0 0; font-weight: 700; overflow-wrap: anywhere; }
    .request-panel { padding: clamp(24px, 4vw, 48px); }
    .request-icon {
      display: grid; width: 58px; height: 58px; margin-bottom: 18px; place-items: center;
      border-radius: 18px; background: #effbf8; color: #064d47; font-size: 1.5rem; font-weight: 800;
    }
    .request-panel h2 { margin: 0; font-size: clamp(1.6rem, 3vw, 2.2rem); letter-spacing: -.03em; line-height: 1.2; }
    .request-intro { margin: 12px 0 26px; color: var(--muted); font-size: 1rem; }
    .notice { margin: 0 0 18px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 12px; background: #f5faf8; }
    .inquiry-form label { display: block; margin-bottom: 8px; font-weight: 750; }
    .inquiry-input {
      display: block; width: 100%; min-height: 150px; padding: 14px 16px; resize: vertical;
      border: 1px solid #d5ddda; border-radius: 16px; background: #fff; color: #17201e;
    }
    .inquiry-input:focus { outline: 3px solid #72e1d0; outline-offset: 2px; }
    .field-errors { margin: 6px 0 0; padding-left: 20px; color: #b42318; font-size: .86rem; }
    .submit-request, .login-request {
      display: block; width: 100%; min-height: 58px; margin-top: 22px; padding: 13px 18px;
      border: 0; border-radius: 14px; background: var(--button); color: #fff;
      font-weight: 800; text-align: center; text-decoration: none; cursor: pointer;
    }
    .request-private-note, .request-blocked { margin: 14px 0 0; color: var(--muted); font-size: .85rem; }
    @media (max-width: 900px) {
      .detail-grid { grid-template-columns: 1fr; }
      .item-image { min-height: 300px; }
    }
    @media (max-width: 560px) {
      .header-inner { flex-wrap: wrap; padding-block: 12px; }
      .header-actions { flex-wrap: wrap; gap: 12px; }
      main { width: min(100% - 28px, 620px); margin-top: 22px; }
      .detail-grid { gap: 18px; }
      .item-image { min-height: 230px; }
      .item-facts { grid-template-columns: 1fr; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home">FindIt</a>
      <nav class="header-actions" aria-label="Primary navigation">
        <button class="theme-toggle" type="button" data-theme-toggle
          aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__HOME_URL__#recent-items">Browse items</a>
        <a href="__DASHBOARD_URL__">Dashboard</a>
      </nav>
    </div>
  </header>
  <main>
    <a class="back-link" href="__HOME_URL__#recent-items">← &nbsp; Back to all items</a>
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
            <div><dt>Building found</dt><dd>__ITEM_LOCATION__</dd></div>
            <div><dt>Date found</dt><dd>__ITEM_DATE__</dd></div>
            <div><dt>Time found</dt><dd>__ITEM_TIME__</dd></div>
          </dl>
        </div>
      </article>
      <aside class="request-panel" aria-labelledby="request-heading">
        <div class="request-icon" aria-hidden="true">✓</div>
        <h2 id="request-heading">Request information privately</h2>
        <p class="request-intro">Your message will only be shared with the person who reported this item. Contact details stay private.</p>
        __NOTICES__
        __REQUEST_CONTENT__
      </aside>
    </div>
  </main>
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
            '<form class="inquiry-form" action="{}" method="post">{}'
            '<label for="{}">Your message</label>{}{}'
            '<button class="submit-request" type="submit">Send private request</button>'
            '<p class="request-private-note">Only the item reporter can read your request.</p></form>',
            reverse("request_found_item_information", args=(item.pk,)),
            csrf_input(request),
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
            "time": item.time_found.strftime("%I:%M %p").lstrip("0"),
            "type": "Found item",
            "image": "",
            "alt": "",
        }
    else:
        item_details = {
            "title": item["title"],
            "initial": item["title"][:1].upper(),
            "category": item["category"],
            "description": item["description"] or "No description was provided.",
            "location": item["building"],
            "date": date.fromisoformat(item["date"]).strftime("%m/%d/%Y"),
            "time": item.get("time", "Not provided"),
            "type": f'{item["type"].title()} item',
            "image": item["image"],
            "alt": item["alt"],
        }
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
        "__DASHBOARD_URL__": (
            reverse("user_dashboard")
            if request.user.is_authenticated
            else reverse("login")
        ),
        "__ITEM_MEDIA__": str(item_media),
        "__ITEM_TYPE__": format_html("{}", item_details["type"]),
        "__ITEM_TITLE__": format_html("{}", item_details["title"]),
        "__CATEGORY__": format_html("{}", item_details["category"]),
        "__ITEM_DESCRIPTION__": format_html("{}", item_details["description"]),
        "__ITEM_LOCATION__": format_html("{}", item_details["location"]),
        "__ITEM_DATE__": item_details["date"],
        "__ITEM_TIME__": item_details["time"],
        "__NOTICES__": str(notices),
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
      color-scheme: dark;
      --paper: #111918;
      --card: #192321;
      --ink: #eef5f3;
      --muted: #b3c0bd;
      --line: #34423f;
      --accent: #8ce8d8;
      --button: #66d8c6;
      --button-ink: #082f2b;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh; margin: 0; background: var(--paper); color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light {
      color-scheme: light; --paper: #f3f8f6; --card: #fff; --ink: #163d38;
      --muted: #596b67; --line: #dce8e5; --accent: #087c70; --button: #003e3a; --button-ink: #fff;
    }
    a { color: var(--accent); }
    button, input, select, textarea { font: inherit; }
    .site-header { background: #090a0b; color: #fff; }
    .header-inner {
      display: flex; width: min(1120px, calc(100% - 40px)); min-height: 68px;
      align-items: center; justify-content: space-between; gap: 20px; margin-inline: auto;
    }
    .brand { color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .header-actions { display: flex; align-items: center; gap: 18px; }
    .header-actions a { color: #fff; font-weight: 650; text-decoration: none; }
    .theme-toggle { padding: 0; border: 0; background: transparent; color: #fff; font-size: 1.2rem; cursor: pointer; }
    main { width: min(760px, calc(100% - 40px)); margin: 48px auto 80px; }
    .eyebrow { margin: 0 0 6px; color: var(--accent); font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    h1 { margin: 0; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -.04em; line-height: 1.15; }
    .intro { margin: 10px 0 26px; color: var(--muted); }
    .report-card { padding: clamp(22px, 5vw, 36px); border: 1px solid var(--line); border-radius: 22px; background: var(--card); }
    .report-form { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; }
    .form-field { min-width: 0; }
    .form-field.full { grid-column: 1 / -1; }
    .form-field label { display: block; margin-bottom: 7px; font-weight: 700; }
    .report-input {
      display: block; width: 100%; min-height: 48px; padding: 10px 12px;
      border: 1px solid var(--line); border-radius: 10px; background: var(--paper); color: var(--ink);
    }
    textarea.report-input { min-height: 120px; resize: vertical; }
    .report-input:focus { outline: 3px solid var(--accent); outline-offset: 2px; }
    .field-errors { margin: 6px 0 0; padding-left: 20px; color: #ffaaa2; font-size: .86rem; }
    .error-summary { grid-column: 1 / -1; margin: 0; color: #ffaaa2; }
    .notice { margin-bottom: 18px; padding: 12px 16px; border: 1px solid var(--line); border-radius: 12px; background: var(--card); }
    .submit-button {
      grid-column: 1 / -1; min-height: 48px; padding: 12px 20px; border: 0; border-radius: 12px;
      background: var(--button); color: var(--button-ink); font-weight: 800; cursor: pointer;
    }
    .form-footer { grid-column: 1 / -1; margin: 0; color: var(--muted); font-size: .88rem; }
    @media (max-width: 560px) {
      .header-inner { flex-wrap: wrap; padding-block: 12px; }
      .header-actions { flex-wrap: wrap; gap: 12px; }
      main { margin-top: 32px; }
      .report-form { grid-template-columns: 1fr; }
      .form-field.full, .submit-button, .form-footer, .error-summary { grid-column: auto; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home">FindIt</a>
      <nav class="header-actions" aria-label="Page navigation">
        <button class="theme-toggle" type="button" data-theme-toggle
          aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__DASHBOARD_URL__">Dashboard</a>
        <a href="__HOME_URL__">Home</a>
      </nav>
    </div>
  </header>
  <main>
    <p class="eyebrow">Help return a belonging</p>
    <h1>__PAGE_TITLE__</h1>
    <p class="intro">__FORM_INTRO__</p>
    __NOTICES__
    <section class="report-card" aria-label="Found item details">
      <form class="report-form" method="post">
        __CSRF_INPUT__
        __ERROR_SUMMARY__
        __FORM_FIELDS__
        <p class="form-footer">Your report will be listed with its category, location, and found date and time.</p>
        <button class="submit-button" type="submit">__SUBMIT_LABEL__</button>
      </form>
    </section>
  </main>
  __THEME_SCRIPT__
</body>
</html>"""


def _found_item_field(form, name, label, full_width=False):
    field = form[name]
    field_errors = (
        format_html(
            '<ul id="{}-errors" class="field-errors" role="alert">{}</ul>',
            field.html_name,
            field.errors,
        )
        if field.errors
        else ""
    )
    return format_html(
        '<div class="form-field{}"><label for="{}">{}</label>{}{}</div>',
        " full" if full_width else "",
        field.id_for_label,
        label,
        field.as_widget(
            attrs={
                "class": "report-input",
                "aria-invalid": "true" if field.errors else "false",
                **(
                    {"aria-describedby": f"{field.html_name}-errors"}
                    if field.errors
                    else {}
                ),
            }
        ),
        field_errors,
    )


def found_item_page(request, form, editing=False):
    error_summary = (
        format_html(
            '<ul class="error-summary" role="alert">{}</ul>',
            form.non_field_errors(),
        )
        if form.non_field_errors()
        else ""
    )
    form_fields = format_html(
        "{}{}{}{}{}{}",
        _found_item_field(form, "item_name", "Item name"),
        _found_item_field(form, "category", "Category"),
        _found_item_field(form, "location", "Building found"),
        _found_item_field(form, "date_found", "Date found"),
        _found_item_field(form, "time_found", "Time found"),
        _found_item_field(form, "description", "Description (optional)", full_width=True),
    )
    notices = format_html_join(
        "",
        '<p class="notice" role="status">{}</p>',
        ((message,) for message in get_messages(request)),
    )
    page = FOUND_ITEM_PAGE
    for placeholder, value in (
        ("__HOME_URL__", reverse("home")),
        ("__DASHBOARD_URL__", reverse("user_dashboard")),
        ("__PAGE_TITLE__", "Edit found item" if editing else "Report a found item"),
        (
            "__FORM_INTRO__",
            (
                "Update the item details below."
                if editing
                else "Share where and when you found the item so its owner can recognize it."
            ),
        ),
        (
            "__SUBMIT_LABEL__",
            "Save changes" if editing else "Submit found item report",
        ),
        ("__CSRF_INPUT__", str(csrf_input(request))),
        ("__ERROR_SUMMARY__", str(error_summary)),
        ("__FORM_FIELDS__", str(form_fields)),
        ("__NOTICES__", str(notices)),
        ("__THEME_SCRIPT__", _theme_script()),
    ):
        page = page.replace(placeholder, value)
    return page


def _reported_item_card(request, item):
    description = (
        format_html(
            '<p class="owned-report-description">{}</p>',
            item.description,
        )
        if item.description
        else ""
    )
    return format_html(
        '<article class="owned-report"><div class="owned-report-content">'
        '<h3>{}</h3><p class="owned-report-meta">{} · {} · {} at {}</p>{}'
        '</div><div class="report-actions"><a href="{}">Edit</a>'
        '<form action="{}" method="post" '
        'onsubmit="return confirm(\'Delete this found-item report?\')">{}'
        '<button class="delete-button" type="submit">Delete</button></form></div></article>',
        item.item_name,
        item.category,
        item.location,
        date_format(item.date_found, "M j, Y"),
        item.time_found.strftime("%I:%M %p").lstrip("0"),
        description,
        reverse("edit_found_item", args=(item.pk,)),
        reverse("delete_found_item", args=(item.pk,)),
        csrf_input(request),
    )


def _reported_items_markup(request, found_items):
    if not found_items:
        return format_html(
            '<p class="empty-reports">You have not reported any found items yet. '
            '<a href="{}">Report a found item</a>.</p>',
            reverse("found_report"),
        )
    return format_html_join(
        "",
        "{}",
        ((_reported_item_card(request, item),) for item in found_items),
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
      color-scheme: dark;
      --paper: #111918;
      --card: #192321;
      --ink: #eef5f3;
      --muted: #b3c0bd;
      --line: #34423f;
      --accent: #8ce8d8;
      --button: #66d8c6;
      --button-ink: #082f2b;
      --danger: #ffaaa2;
    }
    * { box-sizing: border-box; }
    body {
      min-height: 100vh;
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.6;
    }
    body.theme-light {
      color-scheme: light;
      --paper: #f3f8f6;
      --card: #fff;
      --ink: #163d38;
      --muted: #596b67;
      --line: #dce8e5;
      --accent: #087c70;
      --button: #003e3a;
      --button-ink: #fff;
      --danger: #b42318;
    }
    a { color: var(--accent); }
    button, input { font: inherit; }
    .site-header { background: #090a0b; color: #fff; }
    .header-inner {
      display: flex;
      width: min(1120px, calc(100% - 40px));
      min-height: 68px;
      align-items: center;
      justify-content: space-between;
      gap: 20px;
      margin-inline: auto;
    }
    .brand { color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .header-actions { display: flex; align-items: center; gap: 18px; }
    .header-actions a { color: #fff; font-weight: 650; text-decoration: none; }
    .header-actions a:hover { color: #8ce8d8; }
    .header-actions form { margin: 0; }
    .header-actions button, .theme-toggle {
      padding: 0; border: 0; background: transparent; color: #fff; cursor: pointer;
    }
    .theme-toggle { font-size: 1.2rem; }
    main { width: min(900px, calc(100% - 40px)); margin: 52px auto 80px; }
    .eyebrow { margin-bottom: 6px; color: var(--accent); font-size: .78rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }
    h1 { margin: 0; font-size: clamp(2rem, 5vw, 3rem); letter-spacing: -.04em; line-height: 1.15; }
    .intro { margin: 10px 0 28px; color: var(--muted); }
    .notice { margin-bottom: 20px; padding: 12px 16px; border: 1px solid var(--line); border-radius: 12px; background: var(--card); }
    .dashboard-card {
      padding: clamp(22px, 5vw, 36px);
      border: 1px solid var(--line);
      border-radius: 22px;
      background: var(--card);
    }
    .dashboard-card h2 { margin: 0 0 20px; font-size: 1.35rem; }
    .reported-items { margin-top: 24px; }
    .reports-heading-row { display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .reports-heading-row h2 { margin: 0; }
    .reports-heading-row > a { font-weight: 700; }
    .report-list { display: grid; gap: 14px; margin-top: 20px; }
    .owned-report {
      display: flex; align-items: center; justify-content: space-between; gap: 20px;
      padding: 16px; border: 1px solid var(--line); border-radius: 14px;
    }
    .owned-report-content { min-width: 0; }
    .owned-report h3 { margin: 0 0 4px; font-size: 1.05rem; }
    .owned-report-meta, .owned-report-description { margin: 0; color: var(--muted); font-size: .88rem; }
    .owned-report-description { margin-top: 8px; }
    .report-actions { display: flex; align-items: center; gap: 14px; }
    .report-actions a { font-weight: 700; }
    .report-actions form { margin: 0; }
    .delete-button {
      min-height: 40px; padding: 7px 14px; border: 1px solid var(--danger);
      border-radius: 999px; background: transparent; color: var(--danger);
      font-weight: 750; cursor: pointer;
    }
    .delete-button:hover { background: color-mix(in srgb, var(--danger) 12%, transparent); }
    .empty-reports { margin: 18px 0 0; color: var(--muted); }
    .private-request-list { display: grid; gap: 14px; }
    .private-request { padding: 16px; border: 1px solid var(--line); border-radius: 14px; }
    .private-request-heading { display: flex; align-items: baseline; justify-content: space-between; gap: 14px; }
    .private-request h3 { margin: 0; font-size: 1rem; }
    .private-request time, .private-request-sender { color: var(--muted); font-size: .85rem; }
    .private-request-sender { margin: 5px 0 10px; }
    .private-request-message { margin: 0; white-space: pre-wrap; overflow-wrap: anywhere; }
    .empty-requests { margin: 0; color: var(--muted); }
    .profile-details { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18px; margin: 0; }
    .profile-details div { min-width: 0; padding: 14px; border: 1px solid var(--line); border-radius: 14px; }
    .profile-details dt { margin-bottom: 4px; color: var(--muted); font-size: .82rem; font-weight: 700; }
    .profile-details dd { overflow-wrap: anywhere; margin: 0; font-weight: 650; }
    .username-form { max-width: 540px; margin-top: 30px; padding-top: 26px; border-top: 1px solid var(--line); }
    .username-form label { display: block; margin-bottom: 7px; font-weight: 700; }
    .text-input {
      width: 100%; min-height: 48px; padding: 10px 12px;
      border: 1px solid var(--line); border-radius: 10px; background: var(--paper); color: var(--ink);
    }
    .text-input:focus { outline: 3px solid var(--accent); outline-offset: 2px; }
    .field-help, .field-errors { margin: 6px 0 0; color: var(--muted); font-size: .85rem; }
    .field-errors { color: #d74848; }
    .field-errors ul { margin: 0; padding-left: 20px; }
    .submit-button {
      min-height: 46px; margin-top: 18px; padding: 10px 20px;
      border: 0; border-radius: 999px; background: var(--button); color: var(--button-ink);
      font-weight: 800; cursor: pointer;
    }
    .submit-button:focus-visible, .header-actions a:focus-visible,
    .header-actions button:focus-visible, .brand:focus-visible {
      outline: 3px solid #8ce8d8; outline-offset: 3px;
    }
    @media (max-width: 560px) {
      .header-inner { flex-wrap: wrap; padding-block: 12px; }
      .header-actions { flex-wrap: wrap; gap: 12px; }
      main { margin-top: 32px; }
      .profile-details { grid-template-columns: 1fr; }
      .owned-report { align-items: flex-start; flex-direction: column; }
      .reports-heading-row { align-items: flex-start; flex-direction: column; }
      .private-request-heading { align-items: flex-start; flex-direction: column; gap: 2px; }
    }
  </style>
</head>
<body class="theme-dark">
  <header class="site-header">
    <div class="header-inner">
      <a class="brand" href="__HOME_URL__" aria-label="FindIt home">FindIt</a>
      <nav class="header-actions" aria-label="Account navigation">
        <button class="theme-toggle" type="button" data-theme-toggle
          aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__HOME_URL__">Home</a>
        <form action="__LOGOUT_URL__" method="post">__CSRF_INPUT__
          <button type="submit">Log out</button>
        </form>
      </nav>
    </div>
  </header>
  <main>
    <p class="eyebrow">Account</p>
    <h1>User dashboard</h1>
    <p class="intro">View your account details and update your username.</p>
    __NOTICES__
    <section class="dashboard-card" aria-labelledby="profile-heading">
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
    <section class="dashboard-card reported-items" aria-labelledby="reports-heading">
      <div class="reports-heading-row">
        <h2 id="reports-heading">Your found-item reports</h2>
        <a href="__FOUND_REPORT_URL__">Report another item</a>
      </div>
      <div class="report-list">__FOUND_ITEMS__</div>
    </section>
    <section class="dashboard-card reported-items" aria-labelledby="requests-heading">
      <h2 id="requests-heading">Private information requests</h2>
      <div class="private-request-list">__INFORMATION_REQUESTS__</div>
    </section>
  </main>
  __THEME_SCRIPT__
</body>
</html>"""


def user_dashboard_page(request, form, found_items, inquiries):
    username = form.instance.get_username()
    email = form.instance.email or "Not provided"
    joined = date_format(form.instance.date_joined, "F j, Y")
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
    notices = format_html_join(
        "",
        '<p class="notice" role="status">{}</p>',
        ((message,) for message in get_messages(request)),
    )
    reported_items = _reported_items_markup(request, found_items)
    information_requests = _information_requests_markup(inquiries)
    page = USER_DASHBOARD_PAGE
    for placeholder, value in (
        ("__HOME_URL__", reverse("home")),
        ("__LOGOUT_URL__", reverse("logout")),
        ("__CSRF_INPUT__", str(csrf_input(request))),
        ("__USERNAME__", format_html("{}", username)),
        ("__EMAIL__", format_html("{}", email)),
        ("__JOINED__", str(joined)),
        ("__USERNAME_FIELD__", str(username_field)),
        ("__FOUND_REPORT_URL__", reverse("found_report")),
        ("__FOUND_ITEMS__", str(reported_items)),
        ("__INFORMATION_REQUESTS__", str(information_requests)),
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
    .header-inner { display: flex; min-height: 64px; align-items: center; justify-content: space-between; gap: 24px; }
    .brand { display: inline-flex; align-items: center; gap: 10px; color: #fff; font-size: 1.2rem; font-weight: 800; text-decoration: none; }
    .brand-mark {
      position: relative; display: grid; width: 36px; height: 36px; place-items: center;
      border-radius: 12px; background: #075d56; color: #fff;
    }
    .brand-mark::before { width: 13px; height: 13px; transform: translate(-2px,-2px); border: 2.5px solid currentColor; border-radius: 50%; content: ""; }
    .brand-mark::after { position: absolute; width: 7px; height: 2.5px; transform: translate(5px,5px) rotate(45deg); border-radius: 2px; background: currentColor; content: ""; }
    .primary-nav, .header-actions { display: flex; align-items: center; gap: 24px; }
    .primary-nav a, .header-actions a { color: #f7f7f7; font-size: .9rem; font-weight: 600; text-decoration: none; }
    .primary-nav a:hover, .header-actions a:hover { color: var(--teal-bright); }
    .theme-link { border: 0; background: transparent; color: #fff !important; font-size: 1.2rem !important; cursor: pointer; }
    .header-actions .header-cta { padding: 9px 18px; border-radius: 999px; background: #fff; color: var(--action-green); font-weight: 750; }
    .header-actions button.header-cta { border: 0; font: inherit; font-size: .9rem; cursor: pointer; }
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
    body.theme-dark { color-scheme: dark; }
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
    @media (max-width: 850px) {
      .primary-nav, .header-actions { gap: 14px; }
      .auth-panel { grid-template-columns: .9fr 1.1fr; }
      .welcome-panel, .form-panel { padding: 30px; }
    }
    @media (max-width: 650px) {
      .wrap { width: calc(100% - 36px); }
      .header-inner { flex-wrap: wrap; gap: 10px; padding-block: 10px; }
      .primary-nav { order: 3; width: 100%; justify-content: space-between; gap: 8px; }
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
      .primary-nav { flex-wrap: wrap; justify-content: flex-start; column-gap: 14px; }
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
        <a href="__SIGNUP_URL__">Report lost</a>
        <a href="__FOUND_REPORT_URL__">Report found</a>
        <a href="__HOME_URL__#recent-items">Browse items</a>
      </nav>
      <div class="header-actions">
        <button class="theme-link" type="button" data-theme-toggle aria-label="Switch to light mode" aria-pressed="false">☀</button>
        <a href="__LOGIN_URL__">Log in</a>
        <button class="header-cta" type="button">Report an item</button>
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
        <a href="__SIGNUP_URL__">Report a lost item</a>
        <a href="__FOUND_REPORT_URL__">Report a found item</a>
        <a href="__HOME_URL__#recent-items">Search the catalog</a>
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
