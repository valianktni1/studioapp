import React, { useEffect, useState } from "react";
import { toast } from "sonner";
import AdminShell from "@/components/AdminShell";
import { tenantApi, apiError } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";

export default function AdminSettings() {
  const { tenant, refresh } = useAuth();
  const [tab, setTab] = useState("branding");
  const [brand, setBrand] = useState({ business_name: "", phone: "", website: "", logo_url: "", accent_color: "#D4AF37", secondary_color: "#0A0A0B" });
  const [pw, setPw] = useState({ current_password: "", new_password: "" });

  useEffect(() => {
    if (tenant) setBrand({
      business_name: tenant.business_name || "", phone: tenant.phone || "", website: tenant.website || "",
      logo_url: tenant.logo_url || "", accent_color: tenant.accent_color || "#D4AF37", secondary_color: tenant.secondary_color || "#0A0A0B",
    });
  }, [tenant]);

  const saveBrand = async (e) => {
    e.preventDefault();
    try { await tenantApi.put("/admin/branding", brand); await refresh(); toast.success("Branding saved"); }
    catch (err) { toast.error(apiError(err)); }
  };
  const savePw = async (e) => {
    e.preventDefault();
    try { await tenantApi.put("/admin/change-password", pw); toast.success("Password updated"); setPw({ current_password: "", new_password: "" }); }
    catch (err) { toast.error(apiError(err)); }
  };

  const tabs = [["branding", "Branding"], ["password", "Password"], ["email", "Email (SMTP)"], ["twofa", "2FA"]];

  return (
    <AdminShell>
      <h1 className="font-display text-4xl mb-6">Settings</h1>
      <div className="flex flex-wrap gap-2 mb-6">
        {tabs.map(([k, l]) => (
          <button key={k} onClick={() => setTab(k)} className="px-4 py-2 rounded text-sm"
            style={{ background: tab === k ? "var(--sa-gold)" : "var(--sa-surface)", color: tab === k ? "#0A0A0B" : "var(--sa-text)", border: "1px solid var(--sa-border)" }}
            data-testid={`settings-tab-${k}`}>{l}</button>
        ))}
      </div>

      {tab === "branding" && (
        <form onSubmit={saveBrand} className="sa-card p-8 max-w-xl space-y-5" data-testid="branding-form">
          <div><label className="sa-label block mb-2">Business name</label><input className="sa-input" value={brand.business_name} onChange={(e) => setBrand({ ...brand, business_name: e.target.value })} data-testid="br-name" /></div>
          <div><label className="sa-label block mb-2">Logo URL</label><input className="sa-input" value={brand.logo_url} onChange={(e) => setBrand({ ...brand, logo_url: e.target.value })} data-testid="br-logo" /></div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="sa-label block mb-2">Phone</label><input className="sa-input" value={brand.phone} onChange={(e) => setBrand({ ...brand, phone: e.target.value })} /></div>
            <div><label className="sa-label block mb-2">Website</label><input className="sa-input" value={brand.website} onChange={(e) => setBrand({ ...brand, website: e.target.value })} /></div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div><label className="sa-label block mb-2">Accent colour</label><input type="color" className="sa-input h-12 p-1" value={brand.accent_color} onChange={(e) => setBrand({ ...brand, accent_color: e.target.value })} data-testid="br-accent" /></div>
            <div><label className="sa-label block mb-2">Background</label><input type="color" className="sa-input h-12 p-1" value={brand.secondary_color} onChange={(e) => setBrand({ ...brand, secondary_color: e.target.value })} /></div>
          </div>
          <button className="sa-btn" data-testid="br-save">Save branding</button>
        </form>
      )}

      {tab === "password" && (
        <form onSubmit={savePw} className="sa-card p-8 max-w-md space-y-5" data-testid="password-form">
          <div><label className="sa-label block mb-2">Current password</label><input type="password" className="sa-input" value={pw.current_password} onChange={(e) => setPw({ ...pw, current_password: e.target.value })} required data-testid="pw-current" /></div>
          <div><label className="sa-label block mb-2">New password</label><input type="password" className="sa-input" value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} required data-testid="pw-new" /></div>
          <button className="sa-btn" data-testid="pw-save">Update password</button>
        </form>
      )}

      {(tab === "email" || tab === "twofa") && (
        <div className="sa-card p-8 max-w-xl" style={{ color: "var(--sa-muted)" }}>
          <p>{tab === "email" ? "Per-studio SMTP configuration" : "TOTP two-factor authentication"} is coming in the next release.</p>
        </div>
      )}
    </AdminShell>
  );
}
