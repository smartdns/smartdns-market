// ==UserScript==
// @name        example-css
// @version     1.1.0
// @author      smartdns
// @description Validation script for the content market. Injects one visible banner on example.com, a reserved domain that serves no real traffic, so installing it cannot affect any site you actually use. Also demonstrates the settings panel: the fields below render as a form at /panel/example-css.
// @match       *://example.com/*
// @match       *://www.example.com/*
// @setting     banner_text:string=Injected by SmartDNS Text shown in the banner.
// @setting     banner_color:select:green,blue,orange,red=green Banner background colour.
// @setting     enabled:bool=true Turn the banner off without uninstalling the script.
// @panel-auth  user
// ==/UserScript==

// Proves the market pipeline end to end (publish -> review -> install ->
// the engine actually runs it) and doubles as the smallest worked example
// of @setting: declaring the fields above is enough to get a settings form
// at /panel/example-css -- no onPanel needed. Values are read back with
// ctx.kvGet, which is where the built-in form stores them.
//
// Touches nothing but example.com.

const COLORS = {
  green: '#0b5',
  blue: '#0a5fb4',
  orange: '#d97706',
  red: '#c0392b',
};

// A setting the user has never touched has no stored value, so fall back
// to the @setting default rather than rendering an empty banner.
function setting(ctx, name, fallback) {
  const stored = ctx.kvGet(name);
  return stored === null || stored === undefined || stored === '' ? fallback : stored;
}

function onResponse(ctx) {
  if (setting(ctx, 'enabled', 'true') !== 'true') {
    return ctx.pass();
  }

  const text = setting(ctx, 'banner_text', 'Injected by SmartDNS');
  const color = COLORS[setting(ctx, 'banner_color', 'green')] || COLORS.green;

  // The text lands inside a CSS string literal, so a stray quote or
  // backslash would break out of it -- escape both.
  const safe = String(text).replace(/\\/g, '\\\\').replace(/"/g, '\\"');

  ctx.injectCSS(`
    body::before {
      content: "${safe}";
      display: block;
      padding: 12px 16px;
      background: ${color};
      color: #fff;
      font: 600 14px/1.4 system-ui, sans-serif;
      text-align: center;
    }
  `);
  return ctx.pass();
}
