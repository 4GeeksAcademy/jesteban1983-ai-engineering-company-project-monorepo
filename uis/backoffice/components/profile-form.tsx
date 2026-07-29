// components/profile-form.tsx — Formulario de perfil del usuario
//
// Propósito: Muestra y permite editar los datos del perfil del usuario.
//
// Flujo:
// 1. Al cargar: llama a getCurrentUser() → GET /auth/me usando useAsync
// 2. Muestra email (solo lectura) + name/phone/address (editables)
// 3. Al guardar: llama a updateProfile() → PUT /profiles/me
// 4. Si éxito → muestra mensaje de confirmación
// 5. Si 401 → redirige a /login (sesión expirada)
//
// PROTEGIDO

"use client";

import { useState, useEffect, FormEvent } from "react";
import { useRouter } from "next/navigation";
import {
  getCurrentUser,
  updateProfile,
  logoutUser,
} from "@/lib/auth-actions";

export default function ProfileForm() {
  // ── Estado del formulario ─────────────────────────────────
  const [userData, setUserData] = useState<Record<string, any> | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [address, setAddress] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const router = useRouter();

  const loadProfile = async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const user = await getCurrentUser();
      setUserData(user);
      setName(user.profile?.name ?? "");
      setPhone(user.profile?.phone ?? "");
      setAddress(user.profile?.address ?? "");
    } catch (err: unknown) {
      const apiError = err as { status?: number };
      if (apiError.status === 401) {
        logoutUser();
      } else {
        setLoadError("Error al cargar el perfil. Intenta de nuevo.");
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSaveError(null);
    setSuccess(null);
    setSaving(true);

    try {
      await updateProfile({ name, phone: phone || undefined, address: address || undefined });
      setSuccess("Perfil actualizado correctamente");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: unknown) {
      const apiError = err as { status?: number };
      if (apiError.status === 401) {
        logoutUser();
      } else {
        setSaveError("Error al guardar el perfil. Intenta de nuevo.");
      }
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-[calc(100vh-12rem)] items-center justify-center">
        <div className="mb-4 h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-t-transparent" />
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="mx-auto w-full max-w-2xl px-5 py-8">
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-center">
          <p className="mb-2 font-medium text-red-800">Algo salió mal</p>
          <p className="mb-4 text-sm text-red-600">{loadError}</p>
          <button onClick={loadProfile} className="rounded bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700">
            Intentar de nuevo
          </button>
          <a href="/" className="mt-2 block text-sm text-blue-600 underline">Volver al inicio</a>
        </div>
      </div>
    );
  }

  if (!userData) {
    return <div className="p-8 text-center text-gray-400">No hay datos disponibles.</div>;
  }

  return (
    <div className="mx-auto w-full max-w-2xl px-5 py-8 md:px-8 md:py-10">
      <div className="rounded-3xl border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-6">
          <p className="inline-block rounded-full border border-indigo-200 bg-indigo-100 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-indigo-900">
            Mi cuenta
          </p>
          <h1 className="mt-3 text-2xl font-bold text-slate-900 md:text-3xl">
            Perfil de usuario
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Gestiona tu información personal. El email no se puede modificar.
          </p>
        </div>

        {saveError && (
          <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700 border border-red-200">
            {saveError}
          </div>
        )}

        {success && (
          <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-700 border border-green-200">
            {success}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-700">Email</label>
            <input
              type="email"
              value={userData.email}
              disabled
              className="mt-1 block w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500 cursor-not-allowed"
            />
            <p className="mt-1 text-xs text-slate-400">El email no se puede modificar.</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700">Rol</label>
            <input
              type="text"
              value={userData.role}
              disabled
              className="mt-1 block w-full rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-500 cursor-not-allowed"
            />
          </div>

          <div>
            <label htmlFor="name" className="block text-sm font-medium text-slate-700">Nombre</label>
            <input
              id="name" type="text" value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Tu nombre completo"
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="phone" className="block text-sm font-medium text-slate-700">Teléfono</label>
            <input
              id="phone" type="tel" value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+34 600 000 000"
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <div>
            <label htmlFor="address" className="block text-sm font-medium text-slate-700">Dirección</label>
            <textarea
              id="address" rows={2} value={address}
              onChange={(e) => setAddress(e.target.value)}
              placeholder="Calle, ciudad, código postal..."
              className="mt-1 block w-full rounded-lg border border-slate-300 px-3 py-2 text-sm shadow-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {saving ? "Guardando..." : "Guardar cambios"}
          </button>
        </form>
      </div>
    </div>
  );
}