const projectVersion = "1.0.0";
const badge = document.createElement("span");
badge.className = "project-version";
badge.textContent = "ver. " + projectVersion;
Object.assign(badge.style, {
  position: "fixed",
  right: "calc(12px + env(safe-area-inset-right, 0px))",
  bottom: "calc(12px + env(safe-area-inset-bottom, 0px))",
  zIndex: "100",
  padding: "5px 9px",
  border: "1px solid rgba(255,255,255,.24)",
  borderRadius: "6px",
  background: "rgba(14,14,14,.86)",
  color: "#f5f2eb",
  fontFamily: "inherit",
  fontSize: "11px",
  fontWeight: "600",
  lineHeight: "1.4",
  fontVariantNumeric: "tabular-nums",
  whiteSpace: "nowrap",
  pointerEvents: "none",
  backdropFilter: "blur(8px)",
  letterSpacing: ".05em",
});
document.body.append(badge);
