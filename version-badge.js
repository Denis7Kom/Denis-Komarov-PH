const projectVersion = "1.0.0";
const badge = document.createElement("span");
badge.textContent = "ver. " + projectVersion;
badge.style.cssText = "position:fixed;right:max(12px,env(safe-area-inset-right));bottom:max(12px,env(safe-area-inset-bottom));z-index:100;padding:4px 9px;border:1px solid #ffffff40;border-radius:999px;background:#17191e;color:#e6e9ee;font:11px ui-monospace,monospace;pointer-events:none";
document.body.append(badge);
